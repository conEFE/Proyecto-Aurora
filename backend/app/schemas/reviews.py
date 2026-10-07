from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Recommendation = Literal[
    "CONTROL_RUTINA", "CONTROL_6_MESES", "ESTUDIO_COMPLEMENTARIO", "BIOPSIA", "DERIVACION"
]


class ReviewIn(BaseModel):
    birads_final: int = Field(ge=0, le=6)
    findings: str = Field(min_length=5, max_length=5000)
    recommendation: Recommendation

    @field_validator("findings")
    @classmethod
    def _strip(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Los hallazgos son obligatorios")
        return v.strip()


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    medico_id: int
    birads_final: int
    findings: str
    recommendation: str
    created_at: datetime | None


class ReportIn(BaseModel):
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$", description="SHA-256 (hex, minúsculas) del PDF")


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    generated_by: int
    generated_at: datetime | None
    dicom_metadata: dict[str, Any]
    content_hash: str


class LevelCount(BaseModel):
    level: str
    count: int


class WeekPoint(BaseModel):
    week_start: str
    cases: int


class DashboardMetrics(BaseModel):
    date_from: datetime | None
    date_to: datetime | None
    total_cases: int
    cases_by_status: dict[str, int]
    cases_by_level: dict[str, int]
    avg_creation_to_triage_seconds: float | None
    kpi_creation_to_triage_target_seconds: int = 300
    avg_triage_to_review_hours_by_level: dict[str, float | None]
    alta_pending_over_hours: int
    alta_pending_threshold_hours: int
    api_p95_ms: float | None
    api_requests: int
    kpi_api_p95_target_ms: int = 3000
    override_ratio: float | None
    triage_total: int
    triage_overrides: int
    cases_per_week: list[WeekPoint]
