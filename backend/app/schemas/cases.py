from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.case import CaseStatus


class CaseSymptoms(BaseModel):
    palpable_mass: bool = False
    nipple_discharge: bool = False
    skin_or_nipple_changes: bool = False
    birads_reported: int | None = Field(default=None, ge=0, le=6)


class CaseCreate(CaseSymptoms):
    patient_id: int


class CaseUpdate(BaseModel):
    palpable_mass: bool | None = None
    nipple_discharge: bool | None = None
    skin_or_nipple_changes: bool | None = None
    birads_reported: int | None = Field(default=None, ge=0, le=6)


class PatientSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rut: str
    first_name: str
    last_name: str
    birth_date: date
    family_history_first_degree: bool
    previous_breast_cancer: bool


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    status: CaseStatus
    patient_id: int
    patient: PatientSummary | None = None
    created_by: int
    assigned_medico_id: int | None = None
    palpable_mass: bool
    nipple_discharge: bool
    skin_or_nipple_changes: bool
    birads_reported: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    closed_at: datetime | None = None
    image_count: int = 0
    triage_level: str | None = None


class CasePage(BaseModel):
    items: list[CaseOut]
    total: int
    page: int
    size: int
