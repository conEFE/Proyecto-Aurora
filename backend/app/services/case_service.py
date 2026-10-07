"""Casos clínicos: código anónimo, máquina de estados y antecedentes del caso."""

from datetime import datetime, timezone

from sqlalchemy import func, text
from sqlalchemy.orm import Session

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


def to_out(db: Session, case: Case, triage_level: str | None = None) -> CaseOut:
    out = CaseOut.model_validate(case)
    out.image_count = db.query(func.count(Image.id)).filter(Image.case_id == case.id).scalar() or 0
    out.triage_level = triage_level
    return out


def create_case(db: Session, data: CaseCreate, actor: User, ip: str | None = None) -> Case:
    patient = db.get(Patient, data.patient_id)
    if patient is None:
        raise NotFoundError("Paciente no encontrado")
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
) -> tuple[list[Case], int]:
    q = db.query(Case)
    if status is not None:
        q = q.filter(Case.status == status)
    if patient_id is not None:
        q = q.filter(Case.patient_id == patient_id)
    total = q.count()
    items = q.order_by(Case.created_at.desc(), Case.id.desc()).offset((page - 1) * size).limit(size).all()
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
    """Hook: se dispara al crear el caso o editar síntomas/BI-RADS (el triage se conecta en S5)."""
