"""Toma de caso, revisión médica y registro de reportes PDF."""

from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.auth.rbac import require_roles
from app.db.models.user import User, UserRole
from app.deps import get_db
from app.schemas.cases import CaseOut
from app.schemas.reviews import ReportIn, ReportOut, ReviewIn, ReviewOut
from app.services import case_service, review_service
from app.services.audit_service import client_ip

router = APIRouter()
medico_only = require_roles(UserRole.MEDICO)


@router.post("/{case_id}/take", response_model=CaseOut)
def take_case(
    case_id: int, request: Request, actor: User = Depends(medico_only), db: Session = Depends(get_db)
):
    """El médico toma el caso: PRIORIZADO → EN_REVISION."""
    case = review_service.take_case(db, case_id, actor, client_ip(request))
    return case_service.to_out(db, case)


@router.post("/{case_id}/review", response_model=ReviewOut, status_code=201)
def create_review(
    case_id: int,
    data: ReviewIn,
    request: Request,
    actor: User = Depends(medico_only),
    db: Session = Depends(get_db),
):
    """Registra la revisión médica y cierra el caso (EN_REVISION → CERRADO)."""
    return review_service.create_review(db, case_id, data, actor, client_ip(request))


@router.get("/{case_id}/review", response_model=ReviewOut)
def get_review(
    case_id: int, request: Request, actor: User = Depends(medico_only), db: Session = Depends(get_db)
):
    """Revisión médica del caso."""
    return review_service.get_review(db, case_id, actor, client_ip(request))


@router.get("/{case_id}/reports/metadata", response_model=dict[str, Any])
def get_report_metadata(case_id: int, actor: User = Depends(medico_only), db: Session = Depends(get_db)):
    """Metadatos tipo DICOM (SC-02) que el frontend incrusta en el PDF antes de calcular su SHA-256."""
    return review_service.report_metadata(db, case_id, actor)


@router.post("/{case_id}/reports", response_model=ReportOut, status_code=201)
def register_report(
    case_id: int,
    data: ReportIn,
    request: Request,
    actor: User = Depends(medico_only),
    db: Session = Depends(get_db),
):
    """Registra un PDF generado (SHA-256) y devuelve sus metadatos DICOM. Queda auditado como EXPORT."""
    return review_service.register_report(db, case_id, data.content_hash, actor, client_ip(request))


@router.get("/{case_id}/reports", response_model=list[ReportOut])
def list_reports(case_id: int, _: User = Depends(medico_only), db: Session = Depends(get_db)):
    """Reportes PDF registrados del caso."""
    return review_service.list_reports(db, case_id)
