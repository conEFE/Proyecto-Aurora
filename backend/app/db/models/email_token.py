from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.db.base import Base

# Propósitos de token: activación de cuenta (verifica el email y define la contraseña)
PURPOSE_ACTIVATION = "ACTIVATION"


class EmailToken(Base):
    """Token de un solo uso enviado por email. Solo se guarda su hash SHA-256, nunca el token."""

    __tablename__ = "email_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    purpose = Column(String(20), nullable=False)
    token_hash = Column(String(64), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
