"""Derechos de los titulares y consentimiento (Ley 19.628 / Ley 21.719, Ley 20.584)."""

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.case import Case, CaseStatus
from app.db.models.image import Image
from app.db.models.inference_result import InferenceResult
from app.db.models.patient import Patient
from app.db.models.privacy import ConsentEvent, ConsentText, DataSubjectRequest
from app.db.models.review import AIValidation, ClinicalReview, Report
from app.db.models.triage import TriageResult
from app.db.models.user import User
from app.schemas.privacy import (
    ConsentEventOut,
    DataSubjectRequestCreate,
    DataSubjectRequestOut,
    DataSubjectRequestUpdate,
    PatientExport,
)
from app.services.audit_service import audit
from app.services.consent_text import CONSENT_TEXT_BODY, CONSENT_TEXT_VERSION
from app.services.errors import ConflictError, NotFoundError, ValidationError

# Plazo legal de respuesta: 30 días corridos (prorrogable una vez; la prórroga se registra en la resolución)
RESPONSE_DAYS = 30


def _now() -> datetime:
    return datetime.now(timezone.utc)


# --- Texto de consentimiento ------------------------------------------------------------------


def ensure_consent_text(db: Session) -> ConsentText:
    """La migración crea la v1; esto la repone si la tabla quedó vacía (BD de pruebas)."""
    active = db.query(ConsentText).filter(ConsentText.is_active.is_(True)).first()
    if active is None:
        active = ConsentText(version=CONSENT_TEXT_VERSION, body=CONSENT_TEXT_BODY, is_active=True)
        db.add(active)
        db.commit()
    return active


def active_consent_text(db: Session) -> ConsentText:
    text = db.query(ConsentText).filter(ConsentText.is_active.is_(True)).first()
    if text is None:
        raise NotFoundError("No hay un texto de consentimiento vigente")
    return text


def get_consent_text(db: Session, version: str) -> ConsentText:
    text = db.query(ConsentText).filter(ConsentText.version == version).first()
    if text is None:
        raise NotFoundError("Versión del texto de consentimiento no encontrada")
    return text


def require_active_version(db: Session, version: str | None) -> ConsentText:
    """El consentimiento solo vale si se mostró el texto vigente: se compara la versión que envió el cliente."""
    active = active_consent_text(db)
    if not version:
        raise ValidationError("Indique la versión del texto de consentimiento que leyó el paciente")
    if version != active.version:
        raise ConflictError(
            "El texto de consentimiento cambió. Vuelva a mostrarlo al paciente antes de registrar su consentimiento"
        )
    return active


# --- Pacientes: consentimiento y bloqueo ---------------------------------------------------------


def _patient(db: Session, patient_id: int) -> Patient:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise NotFoundError("Paciente no encontrado")
    return patient


def ensure_not_blocked(patient: Patient) -> None:
    if patient.blocked_at is not None:
        raise ConflictError("Los datos del paciente están bloqueados: no se pueden tratar ni modificar")


def record_consent(
    db: Session, patient: Patient, text: ConsentText, actor: User, note: str | None = None
) -> ConsentEvent:
    """Registra el otorgamiento (sin commit)."""
    now = _now()
    patient.consent_given = True
    patient.consent_at = now
    patient.consent_registered_by = actor.id
    patient.consent_text_id = text.id
    event = ConsentEvent(
        patient_id=patient.id,
        action="OTORGADO",
        consent_text_id=text.id,
        occurred_at=now,
        registered_by=actor.id,
        note=note,
    )
    db.add(event)
    return event


def grant_consent(db: Session, patient_id: int, version: str, actor: User, ip: str | None = None) -> Patient:
    patient = _patient(db, patient_id)
    ensure_not_blocked(patient)
    text = require_active_version(db, version)
    if patient.consent_given and patient.consent_text_id == text.id:
        raise ConflictError("El paciente ya tiene registrado el consentimiento con el texto vigente")
    record_consent(db, patient, text, actor)
    audit(db, actor, "CONSENT_GRANT", "patient", patient.id, {"version": text.version}, ip, commit=False)
    db.commit()
    db.refresh(patient)
    return patient


def withdraw_consent(
    db: Session, patient_id: int, reason: str | None, actor: User, ip: str | None = None
) -> Patient:
    patient = _patient(db, patient_id)
    if not patient.consent_given:
        raise ConflictError("El paciente no tiene un consentimiento vigente")
    now = _now()
    patient.consent_given = False
    db.add(
        ConsentEvent(
            patient_id=patient.id,
            action="RETIRADO",
            consent_text_id=patient.consent_text_id,
            occurred_at=now,
            registered_by=actor.id,
            note=(reason or "").strip()[:500] or None,
        )
    )
    # El motivo no va a la auditoría (puede contener datos del paciente)
    audit(db, actor, "CONSENT_WITHDRAW", "patient", patient.id, None, ip, commit=False)
    db.commit()
    db.refresh(patient)
    return patient


def consent_events(db: Session, patient_id: int) -> list[ConsentEventOut]:
    _patient(db, patient_id)
    rows = (
        db.query(ConsentEvent, ConsentText.version)
        .outerjoin(ConsentText, ConsentText.id == ConsentEvent.consent_text_id)
        .filter(ConsentEvent.patient_id == patient_id)
        .order_by(ConsentEvent.occurred_at, ConsentEvent.id)
        .all()
    )
    return [
        ConsentEventOut(
            id=e.id,
            action=e.action,
            consent_text_version=version,
            occurred_at=e.occurred_at,
            registered_by=e.registered_by,
            note=e.note,
        )
        for e, version in rows
    ]


def block_patient(db: Session, patient_id: int, reason: str, actor: User, ip: str | None = None) -> Patient:
    """Bloqueo: reemplaza a la supresión cuando la ficha clínica debe conservarse (Ley 20.584)."""
    patient = _patient(db, patient_id)
    ensure_not_blocked(patient)
    open_cases = (
        db.query(Case).filter(Case.patient_id == patient.id, Case.status != CaseStatus.CERRADO).count()
    )
    if open_cases:
        raise ConflictError(
            f"El paciente tiene {open_cases} caso(s) sin cerrar. Ciérrelos antes de bloquear sus datos"
        )
    patient.blocked_at = _now()
    patient.blocked_by = actor.id
    patient.block_reason = reason.strip()[:500]
    audit(db, actor, "BLOCK", "patient", patient.id, None, ip, commit=False)
    db.commit()
    db.refresh(patient)
    return patient


def unblock_patient(db: Session, patient_id: int, actor: User, ip: str | None = None) -> Patient:
    patient = _patient(db, patient_id)
    if patient.blocked_at is None:
        raise ConflictError("Los datos del paciente no están bloqueados")
    patient.blocked_at = None
    patient.blocked_by = None
    patient.block_reason = None
    audit(db, actor, "UNBLOCK", "patient", patient.id, None, ip, commit=False)
    db.commit()
    db.refresh(patient)
    return patient


# --- Exportación (acceso y portabilidad) -----------------------------------------------------------

# Columnas internas que no son datos del titular
_INTERNAL = {"filepath", "storage_key"}


def _row(obj: Any, exclude: set[str] = frozenset()) -> dict[str, Any]:
    out = {}
    for column in obj.__table__.columns:
        if column.key in exclude or column.key in _INTERNAL:
            continue
        value = getattr(obj, column.key)
        if hasattr(value, "value"):  # enums
            value = value.value
        elif isinstance(value, datetime):
            value = value.isoformat()
        elif hasattr(value, "isoformat"):
            value = value.isoformat()
        out[column.key] = value
    return out


def export_patient(db: Session, patient_id: int, actor: User, ip: str | None = None) -> PatientExport:
    patient = _patient(db, patient_id)
    cases_out = []
    for case in db.query(Case).filter(Case.patient_id == patient.id).order_by(Case.id).all():
        images_out = []
        for image in db.query(Image).filter(Image.case_id == case.id).order_by(Image.id).all():
            item = _row(image)
            inference = db.query(InferenceResult).filter(InferenceResult.image_id == image.id).first()
            validation = db.query(AIValidation).filter(AIValidation.image_id == image.id).first()
            item["inference"] = _row(inference) if inference else None
            item["medical_validation"] = _row(validation) if validation else None
            images_out.append(item)
        review = db.query(ClinicalReview).filter(ClinicalReview.case_id == case.id).first()
        cases_out.append(
            {
                **_row(case),
                "triage_history": [
                    _row(t)
                    for t in db.query(TriageResult)
                    .filter(TriageResult.case_id == case.id)
                    .order_by(TriageResult.id)
                    .all()
                ],
                "images": images_out,
                "clinical_review": _row(review) if review else None,
                "reports": [
                    _row(r)
                    for r in db.query(Report).filter(Report.case_id == case.id).order_by(Report.id).all()
                ],
            }
        )
    requests = (
        db.query(DataSubjectRequest)
        .filter(DataSubjectRequest.patient_id == patient.id)
        .order_by(DataSubjectRequest.id)
        .all()
    )
    audit(db, actor, "EXPORT", "patient", patient.id, {"cases": len(cases_out)}, ip)
    return PatientExport(
        generated_at=_now(),
        generated_by=actor.id,
        patient=_row(patient),
        consent_events=consent_events(db, patient.id),
        cases=cases_out,
        data_subject_requests=[_row(r) for r in requests],
        note=(
            "Copia de los datos personales y de salud del paciente registrados en la plataforma Aurora. "
            "Las imágenes se entregan aparte, a pedido, porque se guardan cifradas. Los resultados marcados "
            "con is_simulated provienen de una IA simulada y no son un resultado clínico."
        ),
    )


# --- Solicitudes de los titulares ---------------------------------------------------------------


def _request_out(req: DataSubjectRequest, patient: Patient | None, now: datetime) -> DataSubjectRequestOut:
    out = DataSubjectRequestOut.model_validate(req)
    if patient is not None:
        out.patient_name = f"{patient.first_name} {patient.last_name}"
        out.patient_rut = patient.rut
    due = req.due_at if req.due_at.tzinfo else req.due_at.replace(tzinfo=timezone.utc)
    out.overdue = req.status in ("RECIBIDA", "EN_PROCESO") and due < now
    return out


def create_request(
    db: Session, patient_id: int, data: DataSubjectRequestCreate, actor: User, ip: str | None = None
) -> DataSubjectRequestOut:
    patient = _patient(db, patient_id)
    now = _now()
    received = data.received_at or now
    if received.tzinfo is None:
        received = received.replace(tzinfo=timezone.utc)
    if received > now + timedelta(minutes=5):
        raise ValidationError("La fecha de recepción no puede ser futura")
    req = DataSubjectRequest(
        patient_id=patient.id,
        request_type=data.request_type,
        status="RECIBIDA",
        detail=(data.detail or "").strip() or None,
        received_at=received,
        due_at=received + timedelta(days=RESPONSE_DAYS),
        registered_by=actor.id,
    )
    db.add(req)
    db.flush()
    audit(db, actor, "CREATE", "data_subject_request", req.id, {"type": data.request_type}, ip, commit=False)
    db.commit()
    db.refresh(req)
    return _request_out(req, patient, now)


def list_requests(
    db: Session, status: str | None = None, overdue_only: bool = False, patient_id: int | None = None
) -> list[DataSubjectRequestOut]:
    q = db.query(DataSubjectRequest, Patient).join(Patient, Patient.id == DataSubjectRequest.patient_id)
    if status:
        q = q.filter(DataSubjectRequest.status == status)
    if patient_id is not None:
        q = q.filter(DataSubjectRequest.patient_id == patient_id)
    now = _now()
    if overdue_only:
        q = q.filter(
            DataSubjectRequest.status.in_(("RECIBIDA", "EN_PROCESO")), DataSubjectRequest.due_at < now
        )
    rows = q.order_by(DataSubjectRequest.due_at, DataSubjectRequest.id).all()
    return [_request_out(req, patient, now) for req, patient in rows]


_TRANSITIONS = {
    "RECIBIDA": {"EN_PROCESO", "RESUELTA", "RECHAZADA"},
    "EN_PROCESO": {"RESUELTA", "RECHAZADA"},
    "RESUELTA": set(),
    "RECHAZADA": set(),
}


def update_request(
    db: Session, request_id: int, data: DataSubjectRequestUpdate, actor: User, ip: str | None = None
) -> DataSubjectRequestOut:
    req = db.get(DataSubjectRequest, request_id)
    if req is None:
        raise NotFoundError("Solicitud no encontrada")
    if data.status not in _TRANSITIONS[req.status]:
        raise ConflictError(f"No se puede pasar una solicitud de {req.status} a {data.status}")
    resolution = (data.resolution or "").strip()
    if data.status in ("RESUELTA", "RECHAZADA"):
        if len(resolution) < 5:
            raise ValidationError("Indique cómo se resolvió la solicitud o el motivo del rechazo")
        req.resolved_at = _now()
        req.resolved_by = actor.id
    if resolution:
        req.resolution = resolution[:1000]
    req.status = data.status
    audit(db, actor, "UPDATE", "data_subject_request", req.id, {"status": data.status}, ip, commit=False)
    db.commit()
    db.refresh(req)
    return _request_out(req, db.get(Patient, req.patient_id), _now())
