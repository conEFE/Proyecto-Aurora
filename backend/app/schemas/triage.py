from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.db.models.case import CaseStatus
from app.db.models.triage import TriageLevel

AgeRange = tuple[int, int]


class EscalationParams(BaseModel):
    birads_alta: list[int] = Field(default_factory=lambda: [4, 5])
    symptoms_alta: bool = True

    @field_validator("birads_alta")
    @classmethod
    def _birads_range(cls, v: list[int]) -> list[int]:
        if any(b < 0 or b > 6 for b in v):
            raise ValueError("Los valores BI-RADS deben estar entre 0 y 6")
        return sorted(set(v))


class Weights(BaseModel):
    ai: float = Field(ge=0, le=100)
    age: float = Field(ge=0, le=100)
    family_history: float = Field(ge=0, le=100)
    previous_cancer: float = Field(ge=0, le=100)
    wait_time: float = Field(ge=0, le=100)

    def total(self) -> float:
        return self.ai + self.age + self.family_history + self.previous_cancer + self.wait_time


class AgeBands(BaseModel):
    high: AgeRange
    medium: list[AgeRange] = Field(default_factory=list)

    @model_validator(mode="after")
    def _ranges(self):
        for lo, hi in [self.high, *self.medium]:
            if lo < 0 or hi < lo:
                raise ValueError("Cada banda de edad debe ser [desde, hasta] con desde ≤ hasta")
        return self


class Thresholds(BaseModel):
    alta: float = Field(gt=0, le=100)
    media: float = Field(ge=0, le=100)


class TriageParams(BaseModel):
    escalation: EscalationParams
    weights: Weights
    age_bands: AgeBands
    max_wait_days: float = Field(gt=0, le=365)
    thresholds: Thresholds

    @model_validator(mode="after")
    def _consistency(self):
        total = round(self.weights.total(), 6)
        if total != 100:
            raise ValueError(f"Los pesos deben sumar 100 (suman {total:g})")
        if not self.thresholds.alta > self.thresholds.media:
            raise ValueError("El umbral ALTA debe ser mayor que el umbral MEDIA")
        return self


class TriageConfigIn(BaseModel):
    params: TriageParams
    change_reason: str = Field(min_length=5, max_length=1000)


class TriageConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version: int
    params: dict[str, Any]
    is_active: bool
    created_by: int | None
    created_at: datetime | None
    change_reason: str


class TriageConfigChangeOut(BaseModel):
    config: TriageConfigOut
    recalculated_cases: int


class OverrideIn(BaseModel):
    level: TriageLevel
    reason: str = Field(min_length=5, max_length=2000)

    @field_validator("reason")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El motivo del cambio de nivel es obligatorio")
        return v.strip()


class TriageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    config_version: int
    score: float
    computed_level: TriageLevel
    escalation_rule: str | None
    breakdown: dict[str, Any] | None
    final_level: TriageLevel
    override_by: int | None
    override_reason: str | None
    is_current: bool
    computed_at: datetime


class QueueItem(BaseModel):
    """Para ADMINISTRATIVO solo se completan code, level, status y waiting_hours."""

    code: str
    level: TriageLevel
    status: CaseStatus
    waiting_hours: float
    case_id: int | None = None
    score: float | None = None
    escalation_rule: str | None = None
    overridden: bool | None = None
    patient_name: str | None = None
    created_at: datetime | None = None


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    message: str
    read_at: datetime | None
    created_at: datetime | None
