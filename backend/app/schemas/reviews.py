from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Recommendation = Literal[
    "CONTROL_RUTINA", "CONTROL_6_MESES", "ESTUDIO_COMPLEMENTARIO", "BIOPSIA", "DERIVACION"
]


AIVerdict = Literal["CONCORDANTE", "FALSO_POSITIVO", "FALSO_NEGATIVO", "NO_EVALUABLE"]
TriageAssessment = Literal["APROPIADO", "SOBREESTIMADO", "SUBESTIMADO"]


class AIValidationIn(BaseModel):
    verdict: AIVerdict
    comment: str | None = Field(default=None, max_length=2000)


class AIValidationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    image_id: int
    inference_result_id: int
    medico_id: int
    verdict: str
    comment: str | None
    ai_detected: bool
    ai_model_version: str
    ai_was_simulated: bool
    created_at: datetime | None
    updated_at: datetime | None


class ReviewIn(BaseModel):
    birads_final: int = Field(ge=0, le=6)
    findings: str = Field(min_length=5, max_length=5000)
    recommendation: Recommendation
    # El médico aprueba o no el nivel de triage vigente
    triage_assessment: TriageAssessment
    triage_comment: str | None = Field(default=None, max_length=2000)

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
    triage_assessment: str | None = None
    triage_comment: str | None = None
    triage_level_at_review: str | None = None
    triage_config_version_at_review: int | None = None
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
    # Validación médica: concordancia IA–médico y aprobación del triage
    ai_validations_total: int = 0
    ai_validations_by_verdict: dict[str, int] = {}
    ai_agreement_rate: float | None = None
    ai_validations_simulated: int = 0
    triage_assessments_total: int = 0
    triage_assessments_by_value: dict[str, int] = {}
    triage_agreement_rate: float | None = None
