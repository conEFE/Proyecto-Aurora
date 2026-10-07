from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.rbac import require_roles
from app.db.models.user import User, UserRole
from app.deps import get_db
from app.schemas.reviews import DashboardMetrics
from app.services import dashboard_service

router = APIRouter()
all_roles = require_roles(UserRole.ADMIN, UserRole.MEDICO, UserRole.ADMINISTRATIVO)


@router.get("/metrics", response_model=DashboardMetrics)
def get_metrics(
    date_from: datetime | None = Query(None, alias="from"),
    date_to: datetime | None = Query(None, alias="to"),
    alta_pending_hours: int | None = Query(None, ge=1, le=24 * 30),
    _: User = Depends(all_roles),
    db: Session = Depends(get_db),
):
    """Métricas agregadas: volumen por estado y nivel, KPIs de tiempo, ALTA pendientes, p95 y overrides."""
    return dashboard_service.metrics(db, date_from, date_to, alta_pending_hours)
