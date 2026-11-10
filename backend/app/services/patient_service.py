from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models.patient import Patient
from app.db.models.user import User
from app.schemas.patients import PatientCreate, PatientUpdate
from app.services.audit_service import audit
from app.services.errors import ConflictError, NotFoundError, ValidationError
from app.services.privacy_service import ensure_not_blocked, record_consent, require_active_version


def create_patient(db: Session, data: PatientCreate, actor: User, ip: str | None = None) -> Patient:
    if db.query(Patient).filter(Patient.rut == data.rut).first():
        raise ConflictError("Ya existe un paciente con ese RUT")
    text = require_active_version(db, data.consent_text_version)
    patient = Patient(
        **data.model_dump(exclude={"consent_given", "consent_text_version"}), created_by=actor.id
    )
    db.add(patient)
    db.flush()
    record_consent(db, patient, text, actor)
    audit(
        db,
        actor,
        "CREATE",
        "patient",
        patient.id,
        {"consent": True, "version": text.version},
        ip,
        commit=False,
    )
    db.commit()
    db.refresh(patient)
    return with_version(db, patient)


def with_version(db: Session, patient: Patient) -> Patient:
    """Agrega la versión del texto de consentimiento (atributo de presentación para PatientOut)."""
    from app.db.models.privacy import ConsentText

    text = db.get(ConsentText, patient.consent_text_id) if patient.consent_text_id else None
    patient.consent_text_version = text.version if text else None
    return patient


def get_patient(db: Session, patient_id: int, actor: User, ip: str | None = None) -> Patient:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise NotFoundError("Paciente no encontrado")
    audit(db, actor, "VIEW", "patient", patient.id, None, ip)
    return with_version(db, patient)


def search_patients(
    db: Session,
    actor: User,
    search: str | None = None,
    limit: int = 50,
    ip: str | None = None,
    include_blocked: bool = False,
) -> list[Patient]:
    q = db.query(Patient)
    if not include_blocked:  # los datos bloqueados no aparecen en la búsqueda habitual
        q = q.filter(Patient.blocked_at.is_(None))
    if search:
        term = f"%{search.strip()}%"
        q = q.filter(
            or_(Patient.rut.ilike(term), Patient.first_name.ilike(term), Patient.last_name.ilike(term))
        )
    patients = q.order_by(Patient.created_at.desc()).limit(limit).all()
    # Se registra la consulta sin el término buscado (puede contener un RUT)
    audit(db, actor, "VIEW", "patient", None, {"list": True, "results": len(patients)}, ip)
    return [with_version(db, p) for p in patients]


def update_patient(
    db: Session, patient_id: int, data: PatientUpdate, actor: User, ip: str | None = None
) -> Patient:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise NotFoundError("Paciente no encontrado")
    ensure_not_blocked(patient)
    changes = data.model_dump(exclude_unset=True)
    if "consent_given" in changes and changes["consent_given"] != patient.consent_given:
        raise ValidationError(
            "El consentimiento no se cambia desde la edición: use el registro o el retiro del consentimiento"
        )
    changes.pop("consent_given", None)
    for field in ("first_name", "last_name", "birth_date"):
        if field in changes and changes[field] is None:
            raise ValidationError(f"El campo {field} es obligatorio")
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
    return with_version(db, patient)


def on_patient_updated(db: Session, patient: Patient) -> None:
    """Los antecedentes y la edad del paciente influyen en el triage de sus casos abiertos."""
    from app.services import triage_service

    triage_service.recalculate_for_patient(db, patient.id)
