"""Cumplimiento de la Ley 21.719 / 19.628: consentimiento versionado y solicitudes de los titulares."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)

from app.db.base import Base

CONSENT_ACTIONS = ("OTORGADO", "RETIRADO")
REQUEST_TYPES = ("ACCESO", "RECTIFICACION", "SUPRESION", "OPOSICION", "PORTABILIDAD", "BLOQUEO")
REQUEST_STATUSES = ("RECIBIDA", "EN_PROCESO", "RESUELTA", "RECHAZADA")


class ConsentText(Base):
    """Versión del texto de consentimiento informado. Las versiones no se modifican: se crea una nueva."""

    __tablename__ = "consent_texts"
    __table_args__ = (
        Index("uq_consent_texts_active", "is_active", unique=True, postgresql_where=text("is_active")),
    )

    id = Column(Integer, primary_key=True)
    version = Column(String(20), unique=True, nullable=False)
    body = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("false"), default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ConsentEvent(Base):
    """Historial del consentimiento de cada paciente (otorgamiento y retiro), con el texto aceptado."""

    __tablename__ = "patient_consent_events"
    __table_args__ = (
        CheckConstraint("action IN ('OTORGADO','RETIRADO')", name="ck_patient_consent_events_action"),
    )

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    action = Column(String(10), nullable=False)
    consent_text_id = Column(
        Integer, ForeignKey("consent_texts.id"), nullable=True
    )  # NULL: registro anterior
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    registered_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    note = Column(String(500), nullable=True)


class DataSubjectRequest(Base):
    """Solicitud de un titular (acceso, rectificación, supresión, oposición, portabilidad o bloqueo)."""

    __tablename__ = "data_subject_requests"
    __table_args__ = (
        CheckConstraint(
            "request_type IN ('ACCESO','RECTIFICACION','SUPRESION','OPOSICION','PORTABILIDAD','BLOQUEO')",
            name="ck_data_subject_requests_type",
        ),
        CheckConstraint(
            "status IN ('RECIBIDA','EN_PROCESO','RESUELTA','RECHAZADA')",
            name="ck_data_subject_requests_status",
        ),
    )

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    request_type = Column(String(20), nullable=False)
    status = Column(String(12), nullable=False, server_default=text("'RECIBIDA'"), default="RECIBIDA")
    detail = Column(String(1000), nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=False, index=True)
    registered_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution = Column(String(1000), nullable=True)
