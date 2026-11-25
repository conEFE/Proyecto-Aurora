import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, event, func, text

from app.db.base import Base


class UserRole(enum.Enum):
    MEDICO = "MEDICO"
    ADMIN = "ADMIN"
    ADMINISTRATIVO = "ADMINISTRATIVO"
    # Jefatura y finanzas: dashboard de gestión y comparador de médicos, sin acceso a datos clínicos
    JEFATURA = "JEFATURA"


class MedicalSpecialty(enum.Enum):
    MEDICINA_GENERAL = "MEDICINA_GENERAL"
    GINECOLOGIA = "GINECOLOGIA"
    ONCOLOGIA = "ONCOLOGIA"
    MASTOLOGIA = "MASTOLOGIA"
    RADIOLOGIA = "RADIOLOGIA"
    CIRUGIA_GENERAL = "CIRUGIA_GENERAL"
    MEDICINA_FAMILIAR = "MEDICINA_FAMILIAR"
    OTRA = "OTRA"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(12), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    # full_name = "first_name last_name"; lo recalcula el servicio al crear o editar
    full_name = Column(String(150), nullable=False)
    first_name = Column(String(75), nullable=False)
    last_name = Column(String(75), nullable=False, server_default="", default="")
    specialty = Column(Enum(MedicalSpecialty, name="medicalspecialty"), nullable=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole, name="userrole"), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"), default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    # Seguridad de cuentas (E6)
    must_change_password = Column(Boolean, nullable=False, server_default=text("false"), default=False)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, nullable=False, server_default=text("0"), default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)


def split_full_name(full_name: str) -> tuple[str, str]:
    """Divide "Nombre Apellido(s)" en el primer espacio (misma regla que la migración)."""
    parts = (full_name or "").strip().split(" ", 1)
    return parts[0], (parts[1].strip() if len(parts) > 1 else "")


def compose_full_name(first_name: str, last_name: str) -> str:
    return " ".join(p for p in ((first_name or "").strip(), (last_name or "").strip()) if p)


@event.listens_for(User, "before_insert")
def _fill_names(_mapper, _conn, user: User) -> None:
    """Mantiene coherentes full_name y nombre/apellido aunque el llamador entregue solo uno de los dos."""
    if not user.first_name and user.full_name:
        user.first_name, user.last_name = split_full_name(user.full_name)
    elif user.first_name and not user.full_name:
        user.full_name = compose_full_name(user.first_name, user.last_name)
    if user.last_name is None:
        user.last_name = ""
