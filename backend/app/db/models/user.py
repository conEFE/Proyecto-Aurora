import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, func, text

from app.db.base import Base


class UserRole(enum.Enum):
    MEDICO = "MEDICO"
    ADMIN = "ADMIN"
    ADMINISTRATIVO = "ADMINISTRATIVO"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(12), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole, name="userrole"), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"), default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
