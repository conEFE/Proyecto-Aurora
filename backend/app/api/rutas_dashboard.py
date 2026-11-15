from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.rbac import require_roles
from app.db.models.triage import TriageLevel
from app.db.models.user import User, UserRole
from app.deps import get_db
from app.schemas.reviews import DashboardCase, DashboardMetrics, ModelPerformanceReport, Reviewer
from app.services import dashboard_service

router = APIRouter()
all_roles = require_roles(UserRole.ADMIN, UserRole.MEDICO, UserRole.ADMINISTRATIVO)
clinical_roles = require_roles(UserRole.ADMIN, UserRole.MEDICO)


@router.get("/model-performance", response_model=ModelPerformanceReport)
def get_model_performance(
    date_from: datetime | None = Query(None, alias="from"),
    date_to: datetime | None = Query(None, alias="to"),
    _: User = Depends(clinical_roles),
    db: Session = Depends(get_db),
):
    """Desempeño del modelo por versión (matriz de confusión, exactitud, sensibilidad, especificidad, IC 95 %).

    La referencia es la validación del médico sobre cada imagen; mide el modelo en funcionamiento (KPI K5).
    """
    return dashboard_service.model_performance(db, date_from, date_to)


@router.get("/metrics", response_model=DashboardMetrics)
def get_metrics(
    date_from: datetime | None = Query(None, alias="from"),
    date_to: datetime | None = Query(None, alias="to"),
    alta_pending_hours: int | None = Query(None, ge=1, le=24 * 30),
    level: TriageLevel | None = Query(None, description="Solo casos con este nivel vigente"),
    medico_id: int | None = Query(None, description="Solo casos que revisa o revisó este médico"),
    _: User = Depends(all_roles),
    db: Session = Depends(get_db),
):
    """Métricas agregadas: volumen por estado y nivel, KPIs de tiempo, ALTA pendientes, p95 y overrides."""
    return dashboard_service.metrics(db, date_from, date_to, alta_pending_hours, level=level, medico_id=medico_id)


@router.get("/reviewers", response_model=list[Reviewer])
def get_reviewers(_: User = Depends(all_roles), db: Session = Depends(get_db)):
    """Médicos, para filtrar el dashboard por quien revisa los casos."""
    return dashboard_service.reviewers(db)


@router.get("/cases", response_model=list[DashboardCase])
def get_cases(
    date_from: datetime | None = Query(None, alias="from"),
    date_to: datetime | None = Query(None, alias="to"),
    level: TriageLevel | None = None,
    medico_id: int | None = None,
    alta_pending_hours: int | None = Query(None, ge=1, le=24 * 30),
    _: User = Depends(all_roles),
    db: Session = Depends(get_db),
):
    """Casos de un período (código anónimo, nivel, estado, espera, revisor y si está atrasado), atrasados primero."""
    return dashboard_service.case_rows(db, date_from, date_to, level, medico_id, alta_pending_hours)
