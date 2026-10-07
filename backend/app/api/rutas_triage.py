from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.auth.bearer import get_current_user
from app.auth.rbac import require_roles
from app.db.models.case import CaseStatus
from app.db.models.user import User, UserRole
from app.deps import get_db
from app.schemas.triage import (
    NotificationOut,
    OverrideIn,
    QueueItem,
    TriageConfigChangeOut,
    TriageConfigIn,
    TriageConfigOut,
    TriageOut,
)
from app.services import triage_service
from app.services.audit_service import client_ip

case_router = APIRouter()
triage_router = APIRouter()
notifications_router = APIRouter()

medico_only = require_roles(UserRole.MEDICO)
clinical_staff = require_roles(UserRole.MEDICO, UserRole.ADMINISTRATIVO)
config_readers = require_roles(UserRole.MEDICO, UserRole.ADMIN)


# --- /cases/{id}/triage --------------------------------------------------------


@case_router.post("/{case_id}/triage", response_model=TriageOut)
def recalculate_triage(
    case_id: int, request: Request, actor: User = Depends(medico_only), db: Session = Depends(get_db)
):
    """Recalcula el triage del caso con la configuración activa."""
    return triage_service.manual_recalculate(db, case_id, actor, client_ip(request))


@case_router.get("/{case_id}/triage", response_model=TriageOut)
def get_triage(
    case_id: int, request: Request, actor: User = Depends(medico_only), db: Session = Depends(get_db)
):
    """Triage vigente con el desglose por factor (solo MEDICO)."""
    return triage_service.get_current(db, case_id, actor, client_ip(request))


@case_router.get("/{case_id}/triage/history", response_model=list[TriageOut])
def get_triage_history(
    case_id: int, request: Request, actor: User = Depends(medico_only), db: Session = Depends(get_db)
):
    """Todos los cálculos del caso, del más reciente al más antiguo."""
    return triage_service.history(db, case_id, actor, client_ip(request))


@case_router.post("/{case_id}/triage/override", response_model=TriageOut)
def override_triage(
    case_id: int,
    data: OverrideIn,
    request: Request,
    actor: User = Depends(medico_only),
    db: Session = Depends(get_db),
):
    """El médico fija el nivel final. El motivo es obligatorio y queda en la auditoría (OVERRIDE)."""
    return triage_service.override(db, case_id, data.level, data.reason, actor, client_ip(request))


# --- /triage -------------------------------------------------------------------


@triage_router.get("/queue", response_model=list[QueueItem], response_model_exclude_none=True)
def get_queue(
    request: Request,
    include_in_review: bool = True,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Cola priorizada. ADMINISTRATIVO solo recibe código, nivel, estado y antigüedad."""
    statuses = (
        (CaseStatus.PRIORIZADO, CaseStatus.EN_REVISION) if include_in_review else (CaseStatus.PRIORIZADO,)
    )
    return triage_service.queue(db, actor, statuses, client_ip(request))


@triage_router.get("/config", response_model=TriageConfigOut)
def get_active_config(_: User = Depends(config_readers), db: Session = Depends(get_db)):
    """Configuración de triage activa."""
    return triage_service.active_config(db)


@triage_router.get("/config/history", response_model=list[TriageConfigOut])
def get_config_history(_: User = Depends(config_readers), db: Session = Depends(get_db)):
    """Todas las versiones de la configuración de triage."""
    return triage_service.list_configs(db)


@triage_router.post("/config", response_model=TriageConfigChangeOut, status_code=201)
def create_config(
    data: TriageConfigIn,
    request: Request,
    actor: User = Depends(medico_only),
    db: Session = Depends(get_db),
):
    """Crea una nueva versión activa (solo MEDICO) y recalcula los casos no cerrados."""
    config, count = triage_service.create_config(
        db, data.params, data.change_reason, actor, client_ip(request)
    )
    return TriageConfigChangeOut(config=TriageConfigOut.model_validate(config), recalculated_cases=count)


# --- /notifications ------------------------------------------------------------


@notifications_router.get("", response_model=list[NotificationOut])
def list_notifications(
    unread_only: bool = False, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Notificaciones del usuario autenticado (no leídas primero)."""
    return triage_service.list_notifications(db, user, unread_only)


@notifications_router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notification_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Marca como leída una notificación propia."""
    return triage_service.mark_read(db, notification_id, user)
