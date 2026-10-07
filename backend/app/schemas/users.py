from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.db.models.user import UserRole
from app.utils.rut import validate_rut


class UserCreate(BaseModel):
    rut: str
    email: EmailStr
    full_name: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=8, max_length=72)
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
    password: str | None = Field(default=None, min_length=8, max_length=72)


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
