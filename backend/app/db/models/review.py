from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base

RECOMMENDATIONS = (
    "CONTROL_RUTINA",
    "CONTROL_6_MESES",
    "ESTUDIO_COMPLEMENTARIO",
    "BIOPSIA",
    "DERIVACION",
)


class ClinicalReview(Base):
    __tablename__ = "clinical_reviews"
    __table_args__ = (
        CheckConstraint("birads_final BETWEEN 0 AND 6", name="ck_clinical_reviews_birads"),
        CheckConstraint(
            "recommendation IN ('CONTROL_RUTINA','CONTROL_6_MESES','ESTUDIO_COMPLEMENTARIO','BIOPSIA','DERIVACION')",
            name="ck_clinical_reviews_recommendation",
        ),
    )

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, unique=True)
    medico_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    birads_final = Column(SmallInteger, nullable=False)
    findings = Column(Text, nullable=False)
    recommendation = Column(String(30), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, index=True)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    dicom_metadata = Column(JSONB, nullable=False)
    content_hash = Column(String(64), nullable=False)


class RequestMetric(Base):
    """Duración de cada request (insumo del p95 del dashboard)."""

    __tablename__ = "request_metrics"

    id = Column(BigInteger, primary_key=True)
    method = Column(String(10), nullable=False)
    path = Column(String(200), nullable=False)  # plantilla de la ruta, sin ids
    status_code = Column(Integer, nullable=False)
    duration_ms = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
