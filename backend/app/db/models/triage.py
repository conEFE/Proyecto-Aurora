import enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class TriageLevel(enum.Enum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"


LEVEL_RANK = {TriageLevel.ALTA: 0, TriageLevel.MEDIA: 1, TriageLevel.BAJA: 2}


class TriageConfig(Base):
    __tablename__ = "triage_configs"
    __table_args__ = (
        # Solo una configuración activa a la vez
        Index("uq_triage_configs_active", "is_active", unique=True, postgresql_where=text("is_active")),
    )

    id = Column(Integer, primary_key=True)
    version = Column(Integer, unique=True, nullable=False)
    params = Column(JSONB, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("false"), default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL = configuración inicial
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    change_reason = Column(Text, nullable=False)


class TriageResult(Base):
    __tablename__ = "triage_results"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_triage_results_score"),
        CheckConstraint(
            "override_by IS NULL OR (override_reason IS NOT NULL AND length(trim(override_reason)) > 0)",
            name="ck_triage_results_override_reason",
        ),
        # Solo un resultado vigente por caso
        Index(
            "uq_triage_results_current",
            "case_id",
            unique=True,
            postgresql_where=text("is_current"),
        ),
    )

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, index=True)
    config_version = Column(Integer, ForeignKey("triage_configs.version"), nullable=False)
    score = Column(Numeric(5, 2), nullable=False)
    computed_level = Column(Enum(TriageLevel, name="triagelevel"), nullable=False)
    escalation_rule = Column(String(50), nullable=True)
    breakdown = Column(JSONB, nullable=True)
    final_level = Column(Enum(TriageLevel, name="triagelevel"), nullable=False)
    override_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    override_reason = Column(Text, nullable=True)
    is_current = Column(Boolean, nullable=False, server_default=text("true"), default=True)
    computed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    case = relationship("Case")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    message = Column(Text, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
