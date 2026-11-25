from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.db.models.user import MedicalSpecialty, UserRole, split_full_name
from app.utils.rut import validate_rut

NAME_MAX = 75


def _clean_name(v: str | None) -> str | None:
    return " ".join(v.split()) if isinstance(v, str) else v


class UserCreate(BaseModel):
    rut: str
    email: EmailStr
    # Nombre y apellido por separado. `full_name` se acepta por compatibilidad (se divide en el primer espacio).
    first_name: str | None = Field(default=None, max_length=NAME_MAX)
    last_name: str | None = Field(default=None, max_length=NAME_MAX)
    full_name: str | None = Field(default=None, min_length=3, max_length=150)
    # Sin contraseña: el usuario la define desde el link de activación que recibe por email.
    # La política de contraseñas se valida en el servicio (largo mínimo configurable, letras y números, etc.)
    password: str | None = Field(default=None, min_length=1, max_length=200)
    role: UserRole
    # Obligatoria para médicos; se ignora en los demás roles
    specialty: MedicalSpecialty | None = None
    # Enviar el link de activación (verifica el email). Si no hay contraseña, se envía siempre.
    send_activation: bool = True

    @field_validator("rut")
    @classmethod
    def _rut(cls, v: str) -> str:
        return validate_rut(v)

    @field_validator("first_name", "last_name", "full_name")
    @classmethod
    def _names(cls, v: str | None) -> str | None:
        return _clean_name(v)

    @model_validator(mode="after")
    def _check(self) -> "UserCreate":
        if not self.first_name and self.full_name:
            self.first_name, self.last_name = split_full_name(self.full_name)
        if not self.first_name or len(self.first_name) < 2:
            raise ValueError("Ingrese el nombre (mínimo 2 caracteres)")
        if not self.last_name or len(self.last_name) < 2:
            raise ValueError("Ingrese el apellido (mínimo 2 caracteres)")
        if self.role == UserRole.MEDICO and self.specialty is None:
            raise ValueError("Seleccione la especialidad del médico")
        if self.role != UserRole.MEDICO:
            self.specialty = None
        return self


class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=2, max_length=NAME_MAX)
    last_name: str | None = Field(default=None, min_length=2, max_length=NAME_MAX)
    full_name: str | None = Field(default=None, min_length=3, max_length=150)
    email: EmailStr | None = None
    role: UserRole | None = None
    specialty: MedicalSpecialty | None = None
    is_active: bool | None = None
    # Restablecer la contraseña obliga al usuario a cambiarla en su próximo ingreso
    password: str | None = Field(default=None, min_length=1, max_length=200)

    @field_validator("first_name", "last_name", "full_name")
    @classmethod
    def _names(cls, v: str | None) -> str | None:
        return _clean_name(v)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rut: str
    email: str
    full_name: str
    first_name: str = ""
    last_name: str = ""
    role: UserRole
    specialty: MedicalSpecialty | None = None
    is_active: bool
    created_at: datetime | None = None
    last_login_at: datetime | None = None
    must_change_password: bool = False
    locked_until: datetime | None = None
    email_verified_at: datetime | None = None


class UserCreated(UserOut):
    # Si se intentó enviar el link de activación y si el envío funcionó
    activation_sent: bool | None = None


class ActivationPreview(BaseModel):
    first_name: str
    email: str


class ActivateRequest(BaseModel):
    token: str = Field(min_length=10, max_length=200)
    password: str = Field(min_length=1, max_length=200)


class ResendResult(BaseModel):
    sent: bool
