from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.auth.rbac import require_roles
from app.db.models.case import CaseStatus
from app.db.models.user import User, UserRole
from app.deps import get_db
from app.schemas.cases import CaseCreate, CaseOut, CasePage, CaseUpdate
from app.services import case_service
from app.services.audit_service import client_ip

router = APIRouter()
clinical_staff = require_roles(UserRole.ADMINISTRATIVO, UserRole.MEDICO)


@router.post("", response_model=CaseOut, status_code=201)
def create_case(
    data: CaseCreate,
    request: Request,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Crea un caso para un paciente con consentimiento registrado (409 si no lo tiene)."""
    case = case_service.create_case(db, data, actor, client_ip(request))
    return case_service.to_out(db, case)


@router.get("", response_model=CasePage)
def list_cases(
    status: CaseStatus | None = None,
    patient_id: int | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Lista casos con filtros por estado y paciente."""
    items, total = case_service.list_cases(db, status, patient_id, page, size)
    return CasePage(items=[case_service.to_out(db, c) for c in items], total=total, page=page, size=size)


@router.get("/{case_id}", response_model=CaseOut)
def get_case(
    case_id: int,
    request: Request,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    case = case_service.get_case(db, case_id, actor, client_ip(request))
    return case_service.to_out(db, case)


@router.patch("/{case_id}", response_model=CaseOut)
def update_case(
    case_id: int,
    data: CaseUpdate,
    request: Request,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Edita síntomas y BI-RADS informado. Bloqueado si el caso está CERRADO (409)."""
    case = case_service.update_case(db, case_id, data, actor, client_ip(request))
    return case_service.to_out(db, case)
