"""Métricas agregadas del dashboard (sin datos identificables)."""

import math
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models.case import Case, CaseStatus
from app.db.models.image import Image
from app.db.models.review import AI_VERDICTS, TRIAGE_ASSESSMENTS, AIValidation, ClinicalReview, RequestMetric
from app.db.models.triage import TriageLevel, TriageResult
from app.schemas.reviews import (
    DashboardMetrics,
    ModelPerformanceReport,
    ModelVersionPerformance,
    WeekPoint,
)

# KPI K5: exactitud del modelo ≥ 90 %, evaluada solo con resultados reales y una muestra mínima
K5_TARGET = 0.90
K5_MIN_SAMPLE = 30
REFERENCE_STANDARD = (
    "Validación del médico revisor sobre cada imagen (no reemplaza la confirmación histológica)"
)


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def percentile(values: list[float], pct: float) -> float | None:
    """Percentil por el método del rango más cercano."""
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, int(-(-pct * len(ordered) // 100)))  # ceil(pct/100 * n)
    return round(ordered[rank - 1], 1)


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Intervalo de confianza de Wilson (95 %) para una proporción; se comporta bien con muestras chicas."""
    if n == 0:
        return None
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)


def _ratio(num: int, den: int) -> float | None:
    return round(num / den, 4) if den else None


def model_performance(
    db: Session, date_from: datetime | None = None, date_to: datetime | None = None
) -> ModelPerformanceReport:
    """Matriz de confusión y métricas por versión del modelo, usando la validación médica como referencia.

    VP = concordante con hallazgo informado; VN = concordante sin hallazgo; FP y FN según el veredicto.
    Se usa la copia guardada en cada validación (versión, hallazgo, simulado), así un cambio de modelo
    no altera las métricas de las versiones anteriores.
    """
    q = (
        db.query(
            AIValidation.ai_model_version,
            AIValidation.ai_was_simulated,
            AIValidation.ai_detected,
            AIValidation.verdict,
        )
        .join(Image, Image.id == AIValidation.image_id)
        .join(Case, Case.id == Image.case_id)
    )
    if date_from:
        q = q.filter(Case.created_at >= date_from)
    if date_to:
        q = q.filter(Case.created_at <= date_to)

    groups: dict[tuple[str, bool], dict[str, int]] = {}
    for version, simulated, detected, verdict in q.all():
        g = groups.setdefault((version, simulated), {"tp": 0, "tn": 0, "fp": 0, "fn": 0, "ne": 0})
        if verdict == "CONCORDANTE":
            g["tp" if detected else "tn"] += 1
        elif verdict == "FALSO_POSITIVO":
            g["fp"] += 1
        elif verdict == "FALSO_NEGATIVO":
            g["fn"] += 1
        else:
            g["ne"] += 1

    versions = []
    for (version, simulated), g in sorted(groups.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        tp, tn, fp, fn = g["tp"], g["tn"], g["fp"], g["fn"]
        evaluable = tp + tn + fp + fn
        accuracy = _ratio(tp + tn, evaluable)
        meets = None
        if not simulated and evaluable >= K5_MIN_SAMPLE and accuracy is not None:
            meets = accuracy >= K5_TARGET
        versions.append(
            ModelVersionPerformance(
                model_version=version,
                is_simulated=simulated,
                validations=evaluable + g["ne"],
                evaluable=evaluable,
                not_evaluable=g["ne"],
                true_positives=tp,
                true_negatives=tn,
                false_positives=fp,
                false_negatives=fn,
                accuracy=accuracy,
                accuracy_ci95=wilson_interval(tp + tn, evaluable),
                sensitivity=_ratio(tp, tp + fn),
                sensitivity_ci95=wilson_interval(tp, tp + fn),
                specificity=_ratio(tn, tn + fp),
                specificity_ci95=wilson_interval(tn, tn + fp),
                ppv=_ratio(tp, tp + fp),
                npv=_ratio(tn, tn + fn),
                meets_k5=meets,
            )
        )
    return ModelPerformanceReport(
        date_from=date_from,
        date_to=date_to,
        k5_target=K5_TARGET,
        min_sample=K5_MIN_SAMPLE,
        reference_standard=REFERENCE_STANDARD,
        versions=versions,
    )


def metrics(
    db: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    alta_pending_hours: int | None = None,
    now: datetime | None = None,
) -> DashboardMetrics:
    now = now or datetime.now(timezone.utc)
    hours = alta_pending_hours if alta_pending_hours is not None else settings.ALTA_PENDING_HOURS

    cases_q = db.query(Case)
    if date_from:
        cases_q = cases_q.filter(Case.created_at >= date_from)
    if date_to:
        cases_q = cases_q.filter(Case.created_at <= date_to)
    cases = cases_q.all()
    case_ids = [c.id for c in cases]

    by_status = {s.value: 0 for s in CaseStatus}
    for c in cases:
        by_status[c.status.value] += 1

    current = {}
    first_triage: dict[int, datetime] = {}
    triage_total = overrides = 0
    if case_ids:
        for r in db.query(TriageResult).filter(TriageResult.case_id.in_(case_ids)).all():
            triage_total += 1
            if r.override_by is not None:
                overrides += 1
            if r.is_current:
                current[r.case_id] = r
            prev = first_triage.get(r.case_id)
            if prev is None or r.computed_at < prev:
                first_triage[r.case_id] = r.computed_at

    by_level = {lvl.value: 0 for lvl in TriageLevel}
    for r in current.values():
        by_level[r.final_level.value] += 1

    deltas = [
        (_aware(first_triage[c.id]) - _aware(c.created_at)).total_seconds()
        for c in cases
        if c.id in first_triage and c.created_at
    ]
    avg_creation_to_triage = round(sum(deltas) / len(deltas), 1) if deltas else None

    reviews = {
        rv.case_id: rv
        for rv in (
            db.query(ClinicalReview).filter(ClinicalReview.case_id.in_(case_ids)).all() if case_ids else []
        )
    }
    review_hours: dict[str, list[float]] = {lvl.value: [] for lvl in TriageLevel}
    for case_id, rv in reviews.items():
        if case_id in first_triage and case_id in current and rv.created_at:
            h = (_aware(rv.created_at) - _aware(first_triage[case_id])).total_seconds() / 3600
            review_hours[current[case_id].final_level.value].append(h)
    avg_review = {lvl: (round(sum(v) / len(v), 2) if v else None) for lvl, v in review_hours.items()}

    cutoff = now - timedelta(hours=hours)
    alta_pending = sum(
        1
        for c in cases
        if c.status != CaseStatus.CERRADO
        and c.id in current
        and current[c.id].final_level == TriageLevel.ALTA
        and c.created_at
        and _aware(c.created_at) < cutoff
    )

    metric_q = db.query(RequestMetric.duration_ms)
    if date_from:
        metric_q = metric_q.filter(RequestMetric.created_at >= date_from)
    if date_to:
        metric_q = metric_q.filter(RequestMetric.created_at <= date_to)
    durations = [d for (d,) in metric_q.all()]

    weeks: list[WeekPoint] = []
    if case_ids:
        week_col = func.date_trunc("week", Case.created_at).label("week")
        rows = (
            db.query(week_col, func.count(Case.id))
            .filter(Case.id.in_(case_ids))
            .group_by(week_col)
            .order_by(week_col)
            .all()
        )
        weeks = [WeekPoint(week_start=w.date().isoformat(), cases=n) for w, n in rows]

    # Validación médica de la IA (por imagen) y del triage (por revisión)
    verdicts = {v: 0 for v in AI_VERDICTS}
    simulated_validations = 0
    if case_ids:
        rows = (
            db.query(AIValidation.verdict, AIValidation.ai_was_simulated)
            .join(Image, Image.id == AIValidation.image_id)
            .filter(Image.case_id.in_(case_ids))
            .all()
        )
        for verdict, simulated in rows:
            verdicts[verdict] += 1
            simulated_validations += 1 if simulated else 0
    evaluable = sum(n for v, n in verdicts.items() if v != "NO_EVALUABLE")
    assessments = {a: 0 for a in TRIAGE_ASSESSMENTS}
    for rv in reviews.values():
        if rv.triage_assessment in assessments:
            assessments[rv.triage_assessment] += 1
    assessed = sum(assessments.values())

    return DashboardMetrics(
        date_from=date_from,
        date_to=date_to,
        total_cases=len(cases),
        cases_by_status=by_status,
        cases_by_level=by_level,
        avg_creation_to_triage_seconds=avg_creation_to_triage,
        avg_triage_to_review_hours_by_level=avg_review,
        alta_pending_over_hours=alta_pending,
        alta_pending_threshold_hours=hours,
        api_p95_ms=percentile(durations, 95),
        api_requests=len(durations),
        override_ratio=round(overrides / triage_total, 4) if triage_total else None,
        triage_total=triage_total,
        triage_overrides=overrides,
        cases_per_week=weeks,
        ai_validations_total=sum(verdicts.values()),
        ai_validations_by_verdict=verdicts,
        ai_agreement_rate=round(verdicts["CONCORDANTE"] / evaluable, 4) if evaluable else None,
        ai_validations_simulated=simulated_validations,
        triage_assessments_total=assessed,
        triage_assessments_by_value=assessments,
        triage_agreement_rate=round(assessments["APROPIADO"] / assessed, 4) if assessed else None,
    )
