from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.rbac import require_roles
from app.db.models.audit_log import AuditLog
from app.db.models.case import Case
from app.db.models.patient import Patient
from app.db.models.user import User, UserRole
from app.deps import get_db
from app.schemas.audit import AuditPage
from app.schemas.errors import ErrorLogPage, ErrorTypeCount
from app.schemas.users import UserCreate, UserOut, UserUpdate
from app.services import error_log_service, user_service
from app.services.audit_service import client_ip

router = APIRouter()
admin_only = require_roles(UserRole.ADMIN)


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_cases: int
    total_patients: int


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(_: User = Depends(admin_only), db: Session = Depends(get_db)):
    """Conteos agregados del sistema (sin datos clínicos)."""
    return AdminStatsResponse(
        total_users=db.query(User).count(),
        active_users=db.query(User).filter(User.is_active.is_(True)).count(),
        total_cases=db.query(Case).count(),
        total_patients=db.query(Patient).count(),
    )


@router.get("/users", response_model=list[UserOut])
def list_users(
    role: UserRole | None = None,
    active: bool | None = None,
    _: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    """Lista usuarios (filtros por rol y estado)."""
    return user_service.list_users(db, role, active)


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    data: UserCreate,
    request: Request,
    actor: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    """Crea un usuario con su rol (reemplaza al signup público)."""
    return user_service.create_user(db, data, actor, client_ip(request))


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    request: Request,
    actor: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    """Cambia rol, datos o estado activo de un usuario."""
    return user_service.update_user(db, user_id, data, actor, client_ip(request))


@router.post("/users/{user_id}/unlock", response_model=UserOut)
def unlock_user(
    user_id: int,
    request: Request,
    actor: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    """Quita el bloqueo por intentos fallidos de inicio de sesión."""
    return user_service.unlock_user(db, user_id, actor, client_ip(request))


@router.get("/errors", response_model=ErrorLogPage)
def list_errors(
    error_type: str | None = Query(None, max_length=120),
    status_code: int | None = Query(None, ge=500, le=599),
    date_from: datetime | None = Query(None, alias="from"),
    date_to: datetime | None = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    _: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    """Errores 5xx del servidor (sin datos sensibles), con filtros por fecha, tipo y código."""
    items, total = error_log_service.list_errors(db, date_from, date_to, error_type, status_code, page, size)
    return ErrorLogPage(items=items, total=total, page=page, size=size)


@router.get("/errors/types", response_model=list[ErrorTypeCount])
def list_error_types(_: User = Depends(admin_only), db: Session = Depends(get_db)):
    """Tipos de error registrados y su frecuencia (para el filtro de la vista)."""
    return error_log_service.error_types(db)


@router.get("/audit", response_model=AuditPage)
def list_audit(
    user_id: int | None = None,
    action: str | None = None,
    entity: str | None = None,
    date_from: datetime | None = Query(None, alias="from"),
    date_to: datetime | None = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    _: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    """Bitácora de auditoría con filtros por usuario, acción, entidad y fecha (paginada)."""
    q = db.query(AuditLog)
    if user_id is not None:
        q = q.filter(AuditLog.user_id == user_id)
    if action:
        q = q.filter(AuditLog.action == action.upper())
    if entity:
        q = q.filter(AuditLog.entity == entity)
    if date_from:
        q = q.filter(AuditLog.created_at >= date_from)
    if date_to:
        q = q.filter(AuditLog.created_at <= date_to)
    total = q.count()
    items = q.order_by(AuditLog.id.desc()).offset((page - 1) * size).limit(size).all()
    return AuditPage(items=items, total=total, page=page, size=size)
