import enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class CaseStatus(enum.Enum):
    ABIERTO = "ABIERTO"
    PRIORIZADO = "PRIORIZADO"
    EN_REVISION = "EN_REVISION"
    CERRADO = "CERRADO"


class Case(Base):
    __tablename__ = "cases"
    __table_args__ = (CheckConstraint("birads_reported BETWEEN 0 AND 6", name="ck_cases_birads_reported"),)

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)  # Código anónimo AUR-AAAA-NNNNNN
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_medico_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(
        Enum(CaseStatus, name="casestatus"),
        nullable=False,
        server_default=CaseStatus.ABIERTO.value,
        default=CaseStatus.ABIERTO,
        index=True,
    )
    palpable_mass = Column(Boolean, nullable=False, server_default=text("false"), default=False)
    nipple_discharge = Column(Boolean, nullable=False, server_default=text("false"), default=False)
    skin_or_nipple_changes = Column(Boolean, nullable=False, server_default=text("false"), default=False)
    birads_reported = Column(SmallInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("Patient")
    creator = relationship("User", foreign_keys=[created_by])
    assigned_medico = relationship("User", foreign_keys=[assigned_medico_id])
    images = relationship("Image", back_populates="case", order_by="Image.id")
