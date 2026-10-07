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
from app.schemas.users import UserCreate, UserOut, UserUpdate
from app.services import user_service
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
    return user_service.list_users(db, role, active)


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    data: UserCreate,
    request: Request,
    actor: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    return user_service.create_user(db, data, actor, client_ip(request))


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    request: Request,
    actor: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    return user_service.update_user(db, user_id, data, actor, client_ip(request))


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
