"""Casos clínicos: código anónimo, máquina de estados y antecedentes del caso."""

from datetime import datetime, timezone

from sqlalchemy import func, text
from sqlalchemy.orm import Session, selectinload

from app.db.models.case import Case, CaseStatus
from app.db.models.image import Image
from app.db.models.patient import Patient
from app.db.models.user import User
from app.schemas.cases import CaseCreate, CaseOut, CaseUpdate
from app.services.audit_service import audit
from app.services.errors import ConflictError, NotFoundError

# ABIERTO -> PRIORIZADO -> EN_REVISION -> CERRADO, y PRIORIZADO -> ABIERTO cuando cambian los datos
ALLOWED_TRANSITIONS: dict[CaseStatus, set[CaseStatus]] = {
    CaseStatus.ABIERTO: {CaseStatus.PRIORIZADO},
    CaseStatus.PRIORIZADO: {CaseStatus.ABIERTO, CaseStatus.EN_REVISION},
    CaseStatus.EN_REVISION: {CaseStatus.CERRADO},
    CaseStatus.CERRADO: set(),
}


class InvalidTransition(ConflictError):
    pass


def can_transition(current: CaseStatus, target: CaseStatus) -> bool:
    return target in ALLOWED_TRANSITIONS[current]


def transition(case: Case, target: CaseStatus) -> None:
    """Cambia el estado validando la transición (409 si no está permitida)."""
    if not can_transition(case.status, target):
        raise InvalidTransition(f"Transición de estado no permitida: {case.status.value} → {target.value}")
    case.status = target
    if target == CaseStatus.CERRADO:
        case.closed_at = datetime.now(timezone.utc)


def generate_code(db: Session, when: datetime | None = None) -> str:
    year = (when or datetime.now(timezone.utc)).year
    seq = db.execute(text("SELECT nextval('case_code_seq')")).scalar_one()
    return f"AUR-{year}-{seq:06d}"


def _get(db: Session, case_id: int) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise NotFoundError("Caso no encontrado")
    return case


def to_out(db: Session, case: Case) -> CaseOut:
    return to_out_many(db, [case])[0]


def to_out_many(db: Session, cases: list[Case]) -> list[CaseOut]:
    """CaseOut de varios casos con dos consultas en total (cantidad de imágenes y nivel vigente), no dos por caso."""
    from app.db.models.triage import TriageResult

    ids = [c.id for c in cases]
    if not ids:
        return []
    counts = dict(
        db.query(Image.case_id, func.count(Image.id)).filter(Image.case_id.in_(ids)).group_by(Image.case_id).all()
    )
    levels = dict(
        db.query(TriageResult.case_id, TriageResult.final_level)
        .filter(TriageResult.case_id.in_(ids), TriageResult.is_current.is_(True))
        .all()
    )
    items = []
    for case in cases:
        out = CaseOut.model_validate(case)
        out.image_count = counts.get(case.id, 0)
        level = levels.get(case.id)
        out.triage_level = level.value if level is not None else None
        items.append(out)
    return items


def create_case(db: Session, data: CaseCreate, actor: User, ip: str | None = None) -> Case:
    patient = db.get(Patient, data.patient_id)
    if patient is None:
        raise NotFoundError("Paciente no encontrado")
    if patient.blocked_at is not None:
        raise ConflictError("Los datos del paciente están bloqueados: no se pueden crear casos")
    if not patient.consent_given:
        raise ConflictError(
            "El paciente no tiene consentimiento informado registrado; no se puede crear el caso"
        )
    case = Case(
        code=generate_code(db),
        patient_id=patient.id,
        created_by=actor.id,
        status=CaseStatus.ABIERTO,
        **data.model_dump(exclude={"patient_id"}),
    )
    db.add(case)
    db.flush()
    audit(db, actor, "CREATE", "case", case.id, {"code": case.code}, ip, commit=False)
    db.commit()
    db.refresh(case)
    on_case_data_changed(db, case, actor)
    return case


def get_case(db: Session, case_id: int, actor: User, ip: str | None = None) -> Case:
    case = _get(db, case_id)
    audit(db, actor, "VIEW", "case", case.id, None, ip)
    return case


def list_cases(
    db: Session,
    status: CaseStatus | None = None,
    patient_id: int | None = None,
    page: int = 1,
    size: int = 20,
    level=None,
    code: str | None = None,
    q: str | None = None,
    date_from=None,
    date_to=None,
) -> tuple[list[Case], int]:
    from app.db.models.triage import TriageResult

    query = db.query(Case)
    if status is not None:
        query = query.filter(Case.status == status)
    if level is not None:
        query = query.join(
            TriageResult, (TriageResult.case_id == Case.id) & TriageResult.is_current.is_(True)
        ).filter(TriageResult.final_level == level)
    if patient_id is not None:
        query = query.filter(Case.patient_id == patient_id)
    if code:
        query = query.filter(Case.code == code.strip().upper())
    if q and q.strip():
        term = q.strip().upper()
        if term.isdigit():
            # Un número busca el correlativo: «23» encuentra AUR-2026-000023 (y también 000123, 000230…)
            query = query.filter(Case.code.like(f"AUR-%-%{term}%"))
        else:
            query = query.filter(Case.code.ilike(f"%{term}%"))
    if date_from is not None:
        query = query.filter(Case.created_at >= date_from)
    if date_to is not None:
        query = query.filter(Case.created_at <= date_to)
    total = query.count()
    items = (
        query.options(selectinload(Case.patient))  # el resumen del paciente de toda la página en una consulta
        .order_by(Case.created_at.desc(), Case.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return items, total


def update_case(db: Session, case_id: int, data: CaseUpdate, actor: User, ip: str | None = None) -> Case:
    case = _get(db, case_id)
    if case.status == CaseStatus.CERRADO:
        raise ConflictError("El caso está cerrado y es de solo lectura")
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        if field != "birads_reported" and value is None:
            continue
        setattr(case, field, value)
    mark_data_changed(case)
    audit(db, actor, "UPDATE", "case", case.id, {"fields": sorted(changes)}, ip, commit=False)
    db.commit()
    db.refresh(case)
    on_case_data_changed(db, case, actor)
    return case


def mark_data_changed(case: Case) -> None:
    """Un caso priorizado vuelve a ABIERTO cuando cambian sus datos (luego se recalcula el triage)."""
    if case.status == CaseStatus.PRIORIZADO:
        transition(case, CaseStatus.ABIERTO)


def on_case_data_changed(db: Session, case: Case, actor: User | None = None) -> None:
    """Al crear el caso o editar síntomas/BI-RADS se recalcula el triage."""
    from app.services import triage_service

    triage_service.recalculate(db, case)
