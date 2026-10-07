from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)  # Código anónimo
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con paciente
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    patient = relationship("Patient")

    # Relación con médico
    medico_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medico = relationship("User")

    # Relación con imágenes
    images = relationship("Image", back_populates="case")
