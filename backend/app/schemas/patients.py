from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.rut import validate_rut


class PatientBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    birth_date: date
    sex: Literal["F", "M", "O"] | None = None
    medical_history: str | None = None
    family_history_first_degree: bool = False
    previous_breast_cancer: bool = False

    @field_validator("birth_date")
    @classmethod
    def _not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura")
        return v


class PatientCreate(PatientBase):
    rut: str
    consent_given: bool

    @field_validator("rut")
    @classmethod
    def _rut(cls, v: str) -> str:
        return validate_rut(v)

    @field_validator("consent_given")
    @classmethod
    def _consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Debe registrar el consentimiento informado del paciente")
        return v


class PatientUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    birth_date: date | None = None
    sex: Literal["F", "M", "O"] | None = None
    medical_history: str | None = None
    family_history_first_degree: bool | None = None
    previous_breast_cancer: bool | None = None
    consent_given: bool | None = None


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rut: str
    first_name: str
    last_name: str
    birth_date: date
    sex: str | None = None
    medical_history: str | None = None
    family_history_first_degree: bool
    previous_breast_cancer: bool
    consent_given: bool
    consent_at: datetime | None = None
    consent_registered_by: int | None = None
    created_by: int | None = None
    created_at: datetime | None = None
