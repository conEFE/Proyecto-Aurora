from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.db.models.user import UserRole
from app.utils.rut import validate_rut


class UserCreate(BaseModel):
    rut: str
    email: EmailStr
    full_name: str = Field(min_length=3, max_length=150)
    # La política de contraseñas se valida en el servicio (largo mínimo configurable, letras y números, etc.)
    password: str = Field(min_length=1, max_length=200)
    role: UserRole

    @field_validator("rut")
    @classmethod
    def _rut(cls, v: str) -> str:
        return validate_rut(v)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=3, max_length=150)
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    # Restablecer la contraseña obliga al usuario a cambiarla en su próximo ingreso
    password: str | None = Field(default=None, min_length=1, max_length=200)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rut: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime | None = None
    last_login_at: datetime | None = None
    must_change_password: bool = False
    locked_until: datetime | None = None
