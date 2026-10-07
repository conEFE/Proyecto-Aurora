from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models.patient import Patient
from app.db.models.user import User
from app.schemas.patients import PatientCreate, PatientUpdate
from app.services.audit_service import audit
from app.services.errors import ConflictError, NotFoundError, ValidationError


def create_patient(db: Session, data: PatientCreate, actor: User, ip: str | None = None) -> Patient:
    if db.query(Patient).filter(Patient.rut == data.rut).first():
        raise ConflictError("Ya existe un paciente con ese RUT")
    now = datetime.now(timezone.utc)
    patient = Patient(
        **data.model_dump(exclude={"consent_given"}),
        consent_given=True,
        consent_at=now,
        consent_registered_by=actor.id,
        created_by=actor.id,
    )
    db.add(patient)
    db.flush()
    audit(db, actor, "CREATE", "patient", patient.id, {"consent": True}, ip, commit=False)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: int, actor: User, ip: str | None = None) -> Patient:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise NotFoundError("Paciente no encontrado")
    audit(db, actor, "VIEW", "patient", patient.id, None, ip)
    return patient


def search_patients(
    db: Session, actor: User, search: str | None = None, limit: int = 50, ip: str | None = None
) -> list[Patient]:
    q = db.query(Patient)
    if search:
        term = f"%{search.strip()}%"
        q = q.filter(
            or_(Patient.rut.ilike(term), Patient.first_name.ilike(term), Patient.last_name.ilike(term))
        )
    patients = q.order_by(Patient.created_at.desc()).limit(limit).all()
    # Se registra la consulta sin el término buscado (puede contener un RUT)
    audit(db, actor, "VIEW", "patient", None, {"list": True, "results": len(patients)}, ip)
    return patients


def update_patient(
    db: Session, patient_id: int, data: PatientUpdate, actor: User, ip: str | None = None
) -> Patient:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise NotFoundError("Paciente no encontrado")
    changes = data.model_dump(exclude_unset=True)
    if changes.get("consent_given") is False and patient.consent_given:
        raise ValidationError("El consentimiento registrado no puede retirarse desde la edición")
    for field in ("first_name", "last_name", "birth_date"):
        if field in changes and changes[field] is None:
            raise ValidationError(f"El campo {field} es obligatorio")
    if changes.pop("consent_given", None) and not patient.consent_given:
        patient.consent_given = True
        patient.consent_at = datetime.now(timezone.utc)
        patient.consent_registered_by = actor.id
    for field, value in changes.items():
        setattr(patient, field, value)
    audit(
        db,
        actor,
        "UPDATE",
        "patient",
        patient.id,
        {"fields": sorted(data.model_fields_set)},
        ip,
        commit=False,
    )
    db.commit()
    db.refresh(patient)
    on_patient_updated(db, patient)
    return patient


def on_patient_updated(db: Session, patient: Patient) -> None:
    """Hook: los antecedentes del paciente influyen en el triage (se conecta en S5)."""
