from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.auth.rbac import require_roles
from app.db.models.user import User, UserRole
from app.deps import get_db
from app.schemas.patients import PatientCreate, PatientOut, PatientUpdate
from app.services import patient_service
from app.services.audit_service import client_ip

router = APIRouter()
clinical_staff = require_roles(UserRole.ADMINISTRATIVO, UserRole.MEDICO)


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
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Busca pacientes por RUT o nombre (registra VIEW)."""
    return patient_service.search_patients(db, actor, search, ip=client_ip(request))


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
