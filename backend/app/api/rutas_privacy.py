from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.rbac import require_roles
from app.db.models.privacy import REQUEST_STATUSES, DataSubjectRequest
from app.db.models.user import User, UserRole
from app.deps import get_db
from app.schemas.privacy import ConsentTextOut, DataSubjectRequestOut, DataSubjectRequestUpdate, RequestStatus
from app.services import privacy_service
from app.services.audit_service import client_ip

router = APIRouter()
clinical_staff = require_roles(UserRole.ADMINISTRATIVO, UserRole.MEDICO)
all_roles = require_roles(UserRole.ADMIN, UserRole.MEDICO, UserRole.ADMINISTRATIVO)


class RequestSummary(BaseModel):
    by_status: dict[str, int]
    open_total: int
    overdue: int


@router.get("/consent-text", response_model=ConsentTextOut)
def get_active_consent_text(_: User = Depends(clinical_staff), db: Session = Depends(get_db)):
    """Texto de consentimiento vigente, para mostrarlo al paciente antes de registrarlo."""
    return privacy_service.active_consent_text(db)


@router.get("/consent-texts/{version}", response_model=ConsentTextOut)
def get_consent_text(version: str, _: User = Depends(clinical_staff), db: Session = Depends(get_db)):
    """Una versión del texto de consentimiento (para saber qué aceptó cada paciente)."""
    return privacy_service.get_consent_text(db, version)


@router.get("/requests", response_model=list[DataSubjectRequestOut])
def list_requests(
    status: RequestStatus | None = None,
    overdue: bool = Query(False, description="Solo solicitudes abiertas con el plazo vencido"),
    patient_id: int | None = None,
    _: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Solicitudes de los titulares, ordenadas por vencimiento del plazo."""
    return privacy_service.list_requests(db, status, overdue, patient_id)


@router.patch("/requests/{request_id}", response_model=DataSubjectRequestOut)
def update_request(
    request_id: int,
    data: DataSubjectRequestUpdate,
    request: Request,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Avanza el estado de una solicitud; resolverla o rechazarla exige una respuesta."""
    return privacy_service.update_request(db, request_id, data, actor, client_ip(request))


@router.get("/requests/summary", response_model=RequestSummary)
def requests_summary(_: User = Depends(all_roles), db: Session = Depends(get_db)):
    """Conteo de solicitudes por estado y vencidas (sin datos de pacientes; visible para el ADMIN)."""
    counts = dict(
        db.query(DataSubjectRequest.status, func.count(DataSubjectRequest.id))
        .group_by(DataSubjectRequest.status)
        .all()
    )
    open_ids = ("RECIBIDA", "EN_PROCESO")
    overdue = (
        db.query(func.count(DataSubjectRequest.id))
        .filter(DataSubjectRequest.status.in_(open_ids), DataSubjectRequest.due_at < func.now())
        .scalar()
    )
    by_status = {s: counts.get(s, 0) for s in REQUEST_STATUSES}
    return RequestSummary(
        by_status=by_status, open_total=sum(by_status[s] for s in open_ids), overdue=overdue or 0
    )
