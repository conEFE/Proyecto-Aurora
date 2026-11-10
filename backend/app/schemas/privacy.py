from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

RequestType = Literal["ACCESO", "RECTIFICACION", "SUPRESION", "OPOSICION", "PORTABILIDAD", "BLOQUEO"]
RequestStatus = Literal["RECIBIDA", "EN_PROCESO", "RESUELTA", "RECHAZADA"]


class ConsentTextOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version: str
    body: str
    is_active: bool
    created_at: datetime | None = None


class ConsentGrant(BaseModel):
    consent_text_version: str = Field(min_length=1, max_length=20)


class ConsentWithdraw(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class ConsentEventOut(BaseModel):
    id: int
    action: str
    consent_text_version: str | None
    occurred_at: datetime
    registered_by: int | None
    note: str | None


class BlockRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


class DataSubjectRequestCreate(BaseModel):
    request_type: RequestType
    detail: str | None = Field(default=None, max_length=1000)
    # Fecha en que la solicitud llegó al establecimiento (por defecto, ahora); el plazo corre desde ella
    received_at: datetime | None = None


class DataSubjectRequestUpdate(BaseModel):
    status: RequestStatus
    resolution: str | None = Field(default=None, max_length=1000)


class DataSubjectRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    patient_name: str | None = None
    patient_rut: str | None = None
    request_type: str
    status: str
    detail: str | None
    received_at: datetime
    due_at: datetime
    overdue: bool = False
    registered_by: int
    resolved_at: datetime | None
    resolved_by: int | None
    resolution: str | None


class PatientExport(BaseModel):
    """Copia de los datos del paciente (derecho de acceso y portabilidad), en JSON estructurado."""

    generated_at: datetime
    generated_by: int
    format_version: str = "1.0"
    patient: dict[str, Any]
    consent_events: list[ConsentEventOut]
    cases: list[dict[str, Any]]
    data_subject_requests: list[dict[str, Any]]
    note: str
