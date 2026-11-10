from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, func

from app.db.base import Base


class ErrorLog(Base):
    """Errores 5xx del servidor (insumo del KPI K9). Nunca guarda datos personales ni clínicos."""

    __tablename__ = "error_log"

    id = Column(BigInteger, primary_key=True)
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    path = Column(String(200), nullable=False)  # plantilla de la ruta, sin ids
    status_code = Column(Integer, nullable=False)
    error_type = Column(String(120), nullable=False, index=True)
    message = Column(String(500), nullable=True)  # mensaje saneado
    location = Column(String(200), nullable=True)  # archivo:línea en app/ donde ocurrió
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    request_id = Column(String(32), nullable=False, index=True)
