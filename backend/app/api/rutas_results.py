import random
import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.bearer import get_current_user
from app.db.models.image import Image
from app.db.models.inference_result import InferenceResult
from app.db.models.user import User
from app.deps import get_db

router = APIRouter()


class DetectionBox(BaseModel):
    x: float
    y: float
    width: float
    height: float
    confidence: float
    class_name: str


class InferenceResultResponse(BaseModel):
    image_id: int
    detected: bool
    confidence: float
    detections: list[DetectionBox]
    processing_time_ms: int
    model_version: str = "placeholder-v1.0"
    message: str

    class Config:
        from_attributes = True


@router.post("/{image_id}/results", response_model=InferenceResultResponse)
def get_image_results(
    image_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Obtiene o genera resultados de inferencia para una imagen"""
    # Verificar que la imagen exista
    imagen = db.query(Image).filter(Image.id == image_id).first()
    if not imagen:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    # Verificar permisos (a través del caso)
    if imagen.case.medico_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="No tienes acceso a esta imagen")

    # Verificar si ya existe un resultado guardado
    existing_result = db.query(InferenceResult).filter(InferenceResult.image_id == image_id).first()

    if existing_result:
        # Devolver resultado existente
        detections = []
        if existing_result.detections:
            detections = [DetectionBox(**det) for det in existing_result.detections]

        return InferenceResultResponse(
            image_id=existing_result.image_id,
            detected=existing_result.detected,
            confidence=existing_result.confidence,
            detections=detections,
            processing_time_ms=existing_result.processing_time_ms,
            model_version=existing_result.model_version,
            message=existing_result.message,
        )

    # Si no existe, generar y guardar nuevo resultado
    # Simular procesamiento más realista (2-4 segundos)
    processing_time = random.uniform(2.0, 4.0)
    time.sleep(processing_time)

    # Generar resultados mock (usar seed basado en image_id para consistencia)
    random.seed(image_id)  # Esto hace que el mismo image_id siempre genere los mismos resultados
    detected = random.random() > 0.3  # 70% probabilidad de detección
    confidence = random.uniform(85.0, 98.0) if detected else random.uniform(92.0, 99.0)

    detections = []
    detections_data = []
    if detected:
        # Generar 1-3 detecciones aleatorias
        num_detections = random.randint(1, 3)
        for _ in range(num_detections):
            det_box = DetectionBox(
                x=random.uniform(0.1, 0.7),
                y=random.uniform(0.1, 0.7),
                width=random.uniform(0.1, 0.3),
                height=random.uniform(0.1, 0.3),
                confidence=random.uniform(confidence - 5, confidence) / 100,
                class_name="lesion_sospechosa",
            )
            detections.append(det_box)
            detections_data.append(det_box.model_dump())

    message = (
        f"Lesión sospechosa detectada con {confidence:.1f}% de confianza"
        if detected
        else f"No se detectaron lesiones sospechosas ({confidence:.1f}% de confianza)"
    )

    # Guardar resultado en BD
    nuevo_resultado = InferenceResult(
        image_id=image_id,
        detected=detected,
        confidence=round(confidence, 2),
        detections=detections_data,  # Guardar como JSON
        processing_time_ms=int(processing_time * 1000),
        model_version="placeholder-v1.0",
        message=message,
    )

    db.add(nuevo_resultado)
    db.commit()
    db.refresh(nuevo_resultado)

    return InferenceResultResponse(
        image_id=nuevo_resultado.image_id,
        detected=nuevo_resultado.detected,
        confidence=nuevo_resultado.confidence,
        detections=detections,
        processing_time_ms=nuevo_resultado.processing_time_ms,
        model_version=nuevo_resultado.model_version,
        message=nuevo_resultado.message,
    )
