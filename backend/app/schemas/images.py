from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.db.models.image import ExamType


class InferenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    image_id: int
    detected: bool
    confidence: float
    detections: list[dict[str, Any]] | None = None
    processing_time_ms: int
    model_version: str
    is_simulated: bool
    message: str
    created_at: datetime | None = None


class ImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    filename: str
    mime_type: str
    width: int | None = None
    height: int | None = None
    size_kb: int | None = None
    exam_type: ExamType
    laterality: str | None = None
    uploaded_by: int | None = None
    sha256: str | None = None
    uploaded_at: datetime
    # Estado de la inferencia (sin el resultado: solo lo ve el rol MEDICO)
    inference_status: str = "PENDIENTE"
    # Solo se completan para el rol MEDICO
    inference: InferenceOut | None = None
    validation: dict[str, Any] | None = None
