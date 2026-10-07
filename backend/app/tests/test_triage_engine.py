"""Tests unitarios de compute_triage (sin BD)."""

import copy
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.db.models.triage import TriageLevel
from app.schemas.triage import TriageParams
from app.services.triage_engine import DEFAULT_PARAMS_V1, age_factor, level_for_score
from app.services.triage_service import compute_triage

NOW = datetime(2026, 10, 7, 12, 0, tzinfo=timezone.utc)


@dataclass
class FakeCase:
    birads_reported: int | None = None
    palpable_mass: bool = False
    nipple_discharge: bool = False
    skin_or_nipple_changes: bool = False
    created_at: datetime | None = NOW


@dataclass
class FakePatient:
    birth_date: date = date(1996, 1, 1)  # 30 años: fuera de las bandas
    family_history_first_degree: bool = False
    previous_breast_cancer: bool = False


@dataclass
class FakeInference:
    detected: bool
    confidence: float


def params(**changes) -> TriageParams:
    data = copy.deepcopy(DEFAULT_PARAMS_V1)
    for key, value in changes.items():
        data[key] = value
    return TriageParams.model_validate(data)


def born_years_ago(years: int) -> date:
    return date(NOW.year - years, 1, 1)


# --- Reglas de escalamiento -------------------------------------------------


@pytest.mark.parametrize("birads", [4, 5])
def test_r_birads_escalates_to_alta(birads):
    out = compute_triage(FakeCase(birads_reported=birads), FakePatient(), [], params(), now=NOW)
    assert out.computed_level == TriageLevel.ALTA
    assert out.escalation_rule == "R_BIRADS"
    assert out.score == Decimal("0.00")  # el puntaje no influye en el nivel


@pytest.mark.parametrize("birads", [0, 1, 2, 3, 6, None])
def test_birads_outside_rule_does_not_escalate(birads):
    out = compute_triage(FakeCase(birads_reported=birads), FakePatient(), [], params(), now=NOW)
    assert out.escalation_rule is None
    assert out.computed_level == TriageLevel.BAJA


@pytest.mark.parametrize("symptom", ["palpable_mass", "nipple_discharge", "skin_or_nipple_changes"])
def test_r_sintoma_escalates_each_symptom(symptom):
    out = compute_triage(FakeCase(**{symptom: True}), FakePatient(), [], params(), now=NOW)
    assert out.computed_level == TriageLevel.ALTA
    assert out.escalation_rule == "R_SINTOMA"


def test_r_sintoma_can_be_disabled():
    p = params(escalation={"birads_alta": [4, 5], "symptoms_alta": False})
    out = compute_triage(FakeCase(palpable_mass=True), FakePatient(), [], p, now=NOW)
    assert out.escalation_rule is None
    assert out.computed_level == TriageLevel.BAJA


def test_birads_rule_takes_precedence_over_symptoms():
    out = compute_triage(
        FakeCase(birads_reported=5, palpable_mass=True), FakePatient(), [], params(), now=NOW
    )
    assert out.escalation_rule == "R_BIRADS"


def test_configurable_birads_list():
    p = params(escalation={"birads_alta": [3], "symptoms_alta": True})
    assert (
        compute_triage(FakeCase(birads_reported=3), FakePatient(), [], p, now=NOW).escalation_rule
        == "R_BIRADS"
    )
    assert compute_triage(FakeCase(birads_reported=4), FakePatient(), [], p, now=NOW).escalation_rule is None


# --- Bandas de edad -----------------------------------------------------------


@pytest.mark.parametrize(
    "age,expected",
    [
        (39, 0.0),
        (40, 0.5),
        (45, 0.5),
        (49, 0.5),
        (50, 1.0),
        (60, 1.0),
        (69, 1.0),
        (70, 0.5),
        (85, 0.5),
        (120, 0.5),
        (25, 0.0),
    ],
)
def test_age_bands(age, expected):
    assert age_factor(age, params()) == expected


def test_age_contributes_weighted_points():
    out = compute_triage(FakeCase(), FakePatient(birth_date=born_years_ago(55)), [], params(), now=NOW)
    assert out.breakdown["age"]["points"] == 15.0
    out = compute_triage(FakeCase(), FakePatient(birth_date=born_years_ago(45)), [], params(), now=NOW)
    assert out.breakdown["age"]["points"] == 7.5


# --- Factores del puntaje ---------------------------------------------------------


def test_ai_uses_max_confidence_of_detected_only():
    inferences = [FakeInference(True, 80.0), FakeInference(True, 50.0), FakeInference(False, 99.0)]
    out = compute_triage(FakeCase(), FakePatient(), inferences, params(), now=NOW)
    assert out.breakdown["ai"]["value"] == 80.0
    assert out.breakdown["ai"]["points"] == 32.0  # 0.8 * 40


def test_ai_is_zero_without_detection():
    out = compute_triage(FakeCase(), FakePatient(), [FakeInference(False, 95.0)], params(), now=NOW)
    assert out.breakdown["ai"]["points"] == 0.0


def test_wait_time_is_capped():
    case = FakeCase(created_at=NOW - timedelta(days=15))
    assert compute_triage(case, FakePatient(), [], params(), now=NOW).breakdown["wait_time"]["points"] == 5.0
    case = FakeCase(created_at=NOW - timedelta(days=90))
    assert compute_triage(case, FakePatient(), [], params(), now=NOW).breakdown["wait_time"]["points"] == 10.0


def test_full_score_example():
    # IA 90% (36) + edad 55 (15) + antecedente familiar (15) + cáncer previo (20) + 30 días (10) = 96
    case = FakeCase(created_at=NOW - timedelta(days=30))
    patient = FakePatient(
        birth_date=born_years_ago(55), family_history_first_degree=True, previous_breast_cancer=True
    )
    out = compute_triage(case, patient, [FakeInference(True, 90.0)], params(), now=NOW)
    assert out.score == Decimal("96.00")
    assert out.computed_level == TriageLevel.ALTA
    assert out.escalation_rule is None
    assert set(out.breakdown) >= {"ai", "age", "family_history", "previous_cancer", "wait_time"}


# --- Límites de umbral ---------------------------------------------------------------


@pytest.mark.parametrize(
    "score,expected",
    [
        ("59.99", TriageLevel.MEDIA),
        ("60", TriageLevel.ALTA),
        ("60.00", TriageLevel.ALTA),
        ("29.99", TriageLevel.BAJA),
        ("30", TriageLevel.MEDIA),
        ("30.00", TriageLevel.MEDIA),
        ("0", TriageLevel.BAJA),
        ("100", TriageLevel.ALTA),
    ],
)
def test_threshold_boundaries(score, expected):
    assert level_for_score(Decimal(score), params()) == expected


def _single_factor_params(ai_weight: float) -> TriageParams:
    """Solo el factor IA pesa (los demás en 0) para obtener puntajes exactos."""
    return params(weights={"ai": 100, "age": 0, "family_history": 0, "previous_cancer": 0, "wait_time": 0})


@pytest.mark.parametrize(
    "confidence,expected",
    [
        (59.99, TriageLevel.MEDIA),
        (60.0, TriageLevel.ALTA),
        (29.99, TriageLevel.BAJA),
        (30.0, TriageLevel.MEDIA),
    ],
)
def test_threshold_boundaries_through_compute(confidence, expected):
    out = compute_triage(
        FakeCase(), FakePatient(), [FakeInference(True, confidence)], _single_factor_params(100), now=NOW
    )
    assert out.score == Decimal(str(confidence)).quantize(Decimal("0.01"))
    assert out.computed_level == expected


# --- Validación de parámetros -----------------------------------------------------------


def test_weights_must_sum_100():
    with pytest.raises(ValidationError, match="sumar 100"):
        params(weights={"ai": 50, "age": 15, "family_history": 15, "previous_cancer": 20, "wait_time": 10})


def test_alta_threshold_must_exceed_media():
    with pytest.raises(ValidationError, match="ALTA debe ser mayor"):
        params(thresholds={"alta": 30, "media": 30})


def test_invalid_age_band():
    with pytest.raises(ValidationError):
        params(age_bands={"high": [69, 50], "medium": []})


def test_default_params_are_valid():
    p = TriageParams.model_validate(DEFAULT_PARAMS_V1)
    assert p.weights.total() == 100
