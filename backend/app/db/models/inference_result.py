from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.orm import relationship

from app.db.base import Base


class InferenceResult(Base):
    __tablename__ = "inference_results"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False, unique=True)
    detected = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)  # confianza general (0-100)
    detections = Column(JSON, nullable=True)  # cajas normalizadas (0-1)
    processing_time_ms = Column(Integer, nullable=False)
    model_version = Column(String, nullable=False)
    # Todo resultado del proveedor simulado queda marcado (nunca se presenta como clínico real)
    is_simulated = Column(Boolean, nullable=False, server_default=text("true"), default=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    image = relationship("Image", back_populates="inference_result")
