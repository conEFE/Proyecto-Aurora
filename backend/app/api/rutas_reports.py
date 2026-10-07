from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.auth.bearer import get_current_user
from app.auth.rbac import require_roles
from app.db.models.case import Case
from app.db.models.image import Image
from app.db.models.inference_result import InferenceResult
from app.db.models.user import User, UserRole
from app.deps import get_db

router = APIRouter()


class DetectionBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_name: str | None = None


class InferenceResultResponse(BaseModel):
    image_id: str
    inference_model_version: str | None = None
    detections: list[DetectionBox] = []
    inference_ms: int | None = None
    fecha_procesamiento: datetime | None = None
    status: str = "pending"
    message: str = "Inference not implemented yet"


class StatisticsResponse(BaseModel):
    total_cases: int
    positive_cases: int
    negative_cases: int
    average_confidence: float
    average_processing_time_ms: float
    total_detections: int


class MonthlyData(BaseModel):
    month: str
    cases: int
    positive: int
    negative: int


@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtiene estadísticas generales del sistema"""
    # Base query de casos
    cases_query = db.query(Case)

    # Si no es ADMIN, solo sus casos
    if current_user.role.value != "ADMIN":
        cases_query = cases_query.filter(Case.medico_id == current_user.id)

    total_cases = cases_query.count()

    # Obtener casos con resultados
    cases_with_results = cases_query.join(Image).join(InferenceResult).all()

    positive_cases = sum(
        1
        for case_obj in cases_with_results
        if any(
            img.inference_result and img.inference_result.detected
            for img in case_obj.images
            if img.inference_result
        )
    )

    negative_cases = total_cases - positive_cases

    # Estadísticas de inferencia
    results_query = db.query(InferenceResult).join(Image).join(Case)
    if current_user.role.value != "ADMIN":
        results_query = results_query.filter(Case.medico_id == current_user.id)

    results = results_query.all()

    if results:
        average_confidence = sum(r.confidence for r in results) / len(results)
        average_processing_time = sum(r.processing_time_ms for r in results) / len(results)
        total_detections = sum(len(r.detections) if r.detections else 0 for r in results if r.detected)
    else:
        average_confidence = 0.0
        average_processing_time = 0.0
        total_detections = 0

    return StatisticsResponse(
        total_cases=total_cases,
        positive_cases=positive_cases,
        negative_cases=negative_cases,
        average_confidence=round(average_confidence, 2),
        average_processing_time_ms=round(average_processing_time, 0),
        total_detections=total_detections,
    )


@router.get("/monthly", response_model=list[MonthlyData])
def get_monthly_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    year: int | None = Query(None, description="Año (por defecto año actual)"),
):
    """Obtiene datos mensuales de casos"""
    if not year:
        year = datetime.now().year

    # Base query
    cases_query = db.query(Case)
    if current_user.role.value != "ADMIN":
        cases_query = cases_query.filter(Case.medico_id == current_user.id)

    # Filtrar por año
    cases_query = cases_query.filter(extract("year", Case.created_at) == year)

    # Agrupar por mes
    monthly_stats = {}
    for month in range(1, 13):
        month_cases = cases_query.filter(extract("month", Case.created_at) == month).all()
        positive = sum(
            1
            for case_obj in month_cases
            if any(
                img.inference_result and img.inference_result.detected
                for img in case_obj.images
                if img.inference_result
            )
        )

        monthly_stats[month] = {
            "cases": len(month_cases),
            "positive": positive,
            "negative": len(month_cases) - positive,
        }

    month_names = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    return [
        MonthlyData(
            month=month_names[i],
            cases=monthly_stats[i + 1]["cases"],
            positive=monthly_stats[i + 1]["positive"],
            negative=monthly_stats[i + 1]["negative"],
        )
        for i in range(12)
    ]


@router.get("/{image_id}/result")
def get_image_result(
    image_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles(UserRole.MEDICO, UserRole.ADMIN)),
):
    """Obtiene los resultados de inferencia para una imagen"""
    # TODO: Implementar cuando lleguen modelos de BD
    # from app.db.models import ResultadoIA
    # resultado = db.query(ResultadoIA).filter(
    #     ResultadoIA.id_imagen == image_id
    # ).first()

    # Por ahora devuelve estructura vacía
    return InferenceResultResponse(
        image_id=image_id,
        status="pending",
        message="Inference service not implemented yet. Waiting for YOLO integration.",
    )


@router.get("/cases/{case_id}/results")
def get_case_results(
    case_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles(UserRole.MEDICO, UserRole.ADMIN)),
):
    """Obtiene todos los resultados de inferencia para un caso"""
    # TODO: Implementar cuando lleguen modelos
    # from app.db.models import ResultadoIA, ImagenMedica
    # resultados = db.query(ResultadoIA).join(ImagenMedica).filter(
    #     ImagenMedica.id_caso == case_id
    # ).all()

    return {"case_id": case_id, "results": [], "message": "Inference service not implemented yet"}
