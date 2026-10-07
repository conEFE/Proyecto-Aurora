from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class AuditLog(Base):
    """Bitácora append-only (un trigger en la BD bloquea UPDATE y DELETE)."""

    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(40), nullable=False, index=True)
    entity = Column(String(30), nullable=False)
    entity_id = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)
    detail = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
