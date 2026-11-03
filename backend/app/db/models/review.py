from sqlalchemy import (
    BigInteger,
    Boolean,
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
        CheckConstraint(
            "triage_assessment IN ('APROPIADO','SOBREESTIMADO','SUBESTIMADO')",
            name="ck_clinical_reviews_triage_assessment",
        ),
    )

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, unique=True)
    medico_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    birads_final = Column(SmallInteger, nullable=False)
    findings = Column(Text, nullable=False)
    recommendation = Column(String(30), nullable=False)
    # Evaluación del triage por el médico (obligatoria en la API desde 2.1.0)
    triage_assessment = Column(String(15), nullable=True)
    triage_comment = Column(Text, nullable=True)
    triage_level_at_review = Column(String(5), nullable=True)
    triage_config_version_at_review = Column(Integer, nullable=True)
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


AI_VERDICTS = ("CONCORDANTE", "FALSO_POSITIVO", "FALSO_NEGATIVO", "NO_EVALUABLE")
TRIAGE_ASSESSMENTS = ("APROPIADO", "SOBREESTIMADO", "SUBESTIMADO")


class AIValidation(Base):
    """Validación médica del resultado de IA de una imagen (concordancia IA–médico)."""

    __tablename__ = "ai_validations"
    __table_args__ = (
        CheckConstraint(
            "verdict IN ('CONCORDANTE','FALSO_POSITIVO','FALSO_NEGATIVO','NO_EVALUABLE')",
            name="ck_ai_validations_verdict",
        ),
    )

    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False, unique=True)
    inference_result_id = Column(Integer, ForeignKey("inference_results.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    verdict = Column(String(20), nullable=False)
    comment = Column(Text, nullable=True)
    # Copia de lo evaluado, para que las métricas no cambien si cambia el modelo
    ai_detected = Column(Boolean, nullable=False)
    ai_model_version = Column(String, nullable=False)
    ai_was_simulated = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
