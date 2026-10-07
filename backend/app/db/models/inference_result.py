from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class InferenceResult(Base):
    __tablename__ = "inference_results"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False, unique=True)
    detected = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)  # Confianza general (0-100)
    detections = Column(JSON, nullable=True)  # Lista de detecciones con coordenadas
    processing_time_ms = Column(Integer, nullable=False)
    model_version = Column(String, default="placeholder-v1.0")
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con imagen
    image = relationship("Image", back_populates="inference_result")
