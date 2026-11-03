"""Cálculo de triage: función pura, sin BD (sección 5 de la especificación).

Es una propuesta técnica para el prototipo, NO un criterio clínico validado.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Protocol

from app.db.models.triage import TriageLevel
from app.schemas.triage import TriageParams

DEFAULT_PARAMS_V1: dict[str, Any] = {
    "escalation": {"birads_alta": [4, 5], "symptoms_alta": True},
    "weights": {"ai": 40, "age": 15, "family_history": 15, "previous_cancer": 20, "wait_time": 10},
    "age_bands": {"high": [50, 69], "medium": [[40, 49], [70, 120]]},
    "max_wait_days": 30,
    "thresholds": {"alta": 60, "media": 30},
}


class CaseLike(Protocol):
    birads_reported: int | None
    palpable_mass: bool
    nipple_discharge: bool
    skin_or_nipple_changes: bool
    created_at: datetime | None


class PatientLike(Protocol):
    birth_date: date
    family_history_first_degree: bool
    previous_breast_cancer: bool


class InferenceLike(Protocol):
    detected: bool
    confidence: float


@dataclass
class TriageOutput:
    score: Decimal
    computed_level: TriageLevel
    escalation_rule: str | None
    breakdown: dict[str, Any] = field(default_factory=dict)


def age_at(birth: date, today: date) -> int:
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def age_factor(age: int, params: TriageParams) -> float:
    lo, hi = params.age_bands.high
    if lo <= age <= hi:
        return 1.0
    if any(m_lo <= age <= m_hi for m_lo, m_hi in params.age_bands.medium):
        return 0.5
    return 0.0


def level_for_score(score: Decimal, params: TriageParams) -> TriageLevel:
    if score >= Decimal(str(params.thresholds.alta)):
        return TriageLevel.ALTA
    if score >= Decimal(str(params.thresholds.media)):
        return TriageLevel.MEDIA
    return TriageLevel.BAJA


def escalation_rule(case: CaseLike, params: TriageParams) -> str | None:
    if case.birads_reported is not None and case.birads_reported in params.escalation.birads_alta:
        return "R_BIRADS"
    if params.escalation.symptoms_alta and (
        case.palpable_mass or case.nipple_discharge or case.skin_or_nipple_changes
    ):
        return "R_SINTOMA"
    return None


def _q(value: float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_triage(
    case: CaseLike,
    patient: PatientLike,
    inferences: list[InferenceLike],
    params: TriageParams | dict[str, Any],
    now: datetime | None = None,
) -> TriageOutput:
    """Paso 1: reglas de escalamiento. Paso 2: puntaje ponderado 0–100. Paso 3: umbrales.

    Si se dispara una regla de escalamiento el nivel es ALTA sin importar el puntaje. El puntaje se calcula
    igual y se guarda como dato informativo (y para ordenar la cola dentro del nivel).
    """
    if not isinstance(params, TriageParams):
        params = TriageParams.model_validate(params)
    now = now or datetime.now(timezone.utc)
    w = params.weights

    detected = [i.confidence for i in inferences if i.detected]
    ai_raw = max(detected) if detected else 0.0
    ai_norm = min(max(ai_raw / 100.0, 0.0), 1.0)

    age = age_at(patient.birth_date, now.date())
    age_norm = age_factor(age, params)

    family_norm = 1.0 if patient.family_history_first_degree else 0.0
    previous_norm = 1.0 if patient.previous_breast_cancer else 0.0

    created = case.created_at or now
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    wait_days = max((now - created).total_seconds() / 86400.0, 0.0)
    wait_norm = min(wait_days / params.max_wait_days, 1.0)

    factors = {
        "ai": (ai_raw, ai_norm, w.ai),
        "age": (age, age_norm, w.age),
        "family_history": (bool(family_norm), family_norm, w.family_history),
        "previous_cancer": (bool(previous_norm), previous_norm, w.previous_cancer),
        "wait_time": (round(wait_days, 2), wait_norm, w.wait_time),
    }
    breakdown: dict[str, Any] = {}
    total = Decimal("0")
    for name, (raw, norm, weight) in factors.items():
        points = _q(norm * weight)
        total += points
        breakdown[name] = {
            "value": raw,
            "normalized": round(norm, 4),
            "weight": weight,
            "points": float(points),
        }
    score = min(max(total, Decimal("0")), Decimal("100"))

    rule = escalation_rule(case, params)
    level = TriageLevel.ALTA if rule else level_for_score(score, params)
    breakdown["escalation_rule"] = rule
    breakdown["ai_is_simulated"] = None  # se completa al persistir (depende de los resultados guardados)
    return TriageOutput(score=score, computed_level=level, escalation_rule=rule, breakdown=breakdown)
