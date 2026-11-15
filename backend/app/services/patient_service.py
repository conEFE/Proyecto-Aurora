import unicodedata

from sqlalchemy import func, or_
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


# Tildes y diéresis que se ignoran al buscar: «Maria» encuentra «María» y «Nunez», «Núñez»
# (mayúsculas incluidas: así no depende de cómo la BD pase a minúsculas los caracteres no ASCII)
_ACCENTED = "áéíóúüàèìòùâêîôûäëïöñÁÉÍÓÚÜÀÈÌÒÙÂÊÎÔÛÄËÏÖÑ"
_PLAIN = "aeiouuaeiouaeiouaeionaeiouuaeiouaeiouaeion"
assert len(_ACCENTED) == len(_PLAIN)


def _fold(text: str) -> str:
    """Minúsculas y sin tildes (para comparar)."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def _folded(column):
    return func.lower(func.translate(column, _ACCENTED, _PLAIN))


def _patients_query(db: Session, search: str | None, include_blocked: bool, status: str | None):
    q = db.query(Patient)
    if status == "bloqueado":
        q = q.filter(Patient.blocked_at.is_not(None))
    elif not include_blocked or status is not None:  # los datos bloqueados no aparecen en la búsqueda habitual
        q = q.filter(Patient.blocked_at.is_(None))
    if status == "activo":
        q = q.filter(Patient.consent_given.is_(True))
    elif status == "sin_consentimiento":
        q = q.filter(Patient.consent_given.is_(False))
    if search and search.strip():
        term = f"%{_fold(search.strip())}%"
        rut = f"%{search.strip().replace('.', '')}%"
        full_name = func.concat(_folded(Patient.first_name), " ", _folded(Patient.last_name))
        q = q.filter(
            or_(
                Patient.rut.ilike(rut),
                _folded(Patient.first_name).like(term),
                _folded(Patient.last_name).like(term),
                full_name.like(term),
            )
        )
    return q


def search_patients(
    db: Session,
    actor: User,
    search: str | None = None,
    limit: int = 50,
    ip: str | None = None,
    include_blocked: bool = False,
    status: str | None = None,
) -> list[Patient]:
    patients = (
        _patients_query(db, search, include_blocked, status).order_by(Patient.created_at.desc()).limit(limit).all()
    )
    # Se registra la consulta sin el término buscado (puede contener un RUT)
    audit(db, actor, "VIEW", "patient", None, {"list": True, "results": len(patients)}, ip)
    return [with_version(db, p) for p in patients]


def page_patients(
    db: Session,
    actor: User,
    search: str | None = None,
    status: str | None = None,
    include_blocked: bool = True,
    page: int = 1,
    size: int = 25,
    ip: str | None = None,
) -> tuple[list[Patient], int]:
    """Página de pacientes con el total, para recorrer la lista completa."""
    q = _patients_query(db, search, include_blocked, status)
    total = q.count()
    patients = q.order_by(Patient.created_at.desc(), Patient.id.desc()).offset((page - 1) * size).limit(size).all()
    audit(db, actor, "VIEW", "patient", None, {"list": True, "results": len(patients), "page": page}, ip)
    return [with_version(db, p) for p in patients], total


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


def delete_patient(db: Session, patient_id: int, actor: User, ip: str | None = None) -> None:
    """Elimina un paciente registrado por error. Solo si no tiene casos: la ficha clínica se conserva
    (Ley 20.584) y para esos pacientes corresponde «Bloquear datos»."""
    from app.db.models.case import Case
    from app.db.models.privacy import ConsentEvent, DataSubjectRequest

    patient = db.get(Patient, patient_id)
    if patient is None:
        raise NotFoundError("Paciente no encontrado")
    if db.query(Case.id).filter(Case.patient_id == patient.id).first() is not None:
        raise ConflictError(
            "No se puede eliminar: el paciente tiene casos clínicos y su ficha se conserva por la Ley 20.584. "
            "Use «Bloquear datos»."
        )
    db.query(DataSubjectRequest).filter(DataSubjectRequest.patient_id == patient.id).delete()
    db.query(ConsentEvent).filter(ConsentEvent.patient_id == patient.id).delete()
    # Sin RUT ni nombre en la auditoría: solo el identificador interno
    audit(db, actor, "DELETE", "patient", patient.id, {"reason": "sin casos"}, ip, commit=False)
    db.delete(patient)
    db.commit()


def on_patient_updated(db: Session, patient: Patient) -> None:
    """Los antecedentes y la edad del paciente influyen en el triage de sus casos abiertos."""
    from app.services import triage_service

    triage_service.recalculate_for_patient(db, patient.id)
