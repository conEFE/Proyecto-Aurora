from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.auth.rbac import require_roles
from app.db.models.user import User, UserRole
from app.deps import get_db
from app.schemas.patients import PatientCreate, PatientOut, PatientUpdate
from app.schemas.privacy import (
    BlockRequest,
    ConsentEventOut,
    ConsentGrant,
    ConsentWithdraw,
    DataSubjectRequestCreate,
    DataSubjectRequestOut,
    PatientExport,
)
from app.services import patient_service, privacy_service
from app.services.audit_service import client_ip

router = APIRouter()
clinical_staff = require_roles(UserRole.ADMINISTRATIVO, UserRole.MEDICO)
medico_only = require_roles(UserRole.MEDICO)


@router.post("", response_model=PatientOut, status_code=201)
def create_patient(
    data: PatientCreate,
    request: Request,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Registra un paciente. El consentimiento informado es obligatorio."""
    return patient_service.create_patient(db, data, actor, client_ip(request))


@router.get("", response_model=list[PatientOut])
def list_patients(
    request: Request,
    search: str | None = Query(None, description="Buscar por RUT o nombre"),
    include_blocked: bool = Query(False, description="Incluir pacientes con datos bloqueados"),
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Busca pacientes por RUT o nombre (registra VIEW). Los bloqueados solo aparecen si se piden."""
    return patient_service.search_patients(
        db, actor, search, ip=client_ip(request), include_blocked=include_blocked
    )


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    request: Request,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Detalle del paciente (registra VIEW)."""
    return patient_service.get_patient(db, patient_id, actor, client_ip(request))


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int,
    data: PatientUpdate,
    request: Request,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Edita datos y antecedentes del paciente; recalcula el triage de sus casos abiertos."""
    return patient_service.update_patient(db, patient_id, data, actor, client_ip(request))


# --- Privacidad: consentimiento, bloqueo, exportación y solicitudes (Ley 21.719) -------------------


@router.post("/{patient_id}/consent", response_model=PatientOut)
def grant_consent(
    patient_id: int,
    data: ConsentGrant,
    request: Request,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Registra el consentimiento con el texto vigente (nuevo otorgamiento o actualización de versión)."""
    patient = privacy_service.grant_consent(
        db, patient_id, data.consent_text_version, actor, client_ip(request)
    )
    return patient_service.with_version(db, patient)


@router.post("/{patient_id}/consent/withdraw", response_model=PatientOut)
def withdraw_consent(
    patient_id: int,
    data: ConsentWithdraw,
    request: Request,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Retira el consentimiento: impide nuevos casos e imágenes; la ficha clínica se conserva."""
    patient = privacy_service.withdraw_consent(db, patient_id, data.reason, actor, client_ip(request))
    return patient_service.with_version(db, patient)


@router.get("/{patient_id}/consent/events", response_model=list[ConsentEventOut])
def consent_events(patient_id: int, _: User = Depends(clinical_staff), db: Session = Depends(get_db)):
    """Historial del consentimiento con la versión del texto aceptado."""
    return privacy_service.consent_events(db, patient_id)


@router.post("/{patient_id}/block", response_model=PatientOut)
def block_patient(
    patient_id: int,
    data: BlockRequest,
    request: Request,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Bloquea el tratamiento de los datos (exige casos cerrados). Los datos se conservan por la Ley 20.584."""
    patient = privacy_service.block_patient(db, patient_id, data.reason, actor, client_ip(request))
    return patient_service.with_version(db, patient)


@router.post("/{patient_id}/unblock", response_model=PatientOut)
def unblock_patient(
    patient_id: int,
    request: Request,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Levanta el bloqueo de los datos del paciente."""
    patient = privacy_service.unblock_patient(db, patient_id, actor, client_ip(request))
    return patient_service.with_version(db, patient)


@router.get("/{patient_id}/export", response_model=PatientExport)
def export_patient(
    patient_id: int,
    request: Request,
    actor: User = Depends(medico_only),
    db: Session = Depends(get_db),
):
    """Copia de todos los datos del paciente en JSON (derechos de acceso y portabilidad). Registra EXPORT."""
    return privacy_service.export_patient(db, patient_id, actor, client_ip(request))


@router.post("/{patient_id}/requests", response_model=DataSubjectRequestOut, status_code=201)
def create_request(
    patient_id: int,
    data: DataSubjectRequestCreate,
    request: Request,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Registra una solicitud del titular; el plazo de respuesta es de 30 días corridos."""
    return privacy_service.create_request(db, patient_id, data, actor, client_ip(request))
