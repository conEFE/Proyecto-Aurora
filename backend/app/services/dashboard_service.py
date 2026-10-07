"""Métricas agregadas del dashboard (sin datos identificables)."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models.case import Case, CaseStatus
from app.db.models.review import ClinicalReview, RequestMetric
from app.db.models.triage import TriageLevel, TriageResult
from app.schemas.reviews import DashboardMetrics, WeekPoint


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def percentile(values: list[float], pct: float) -> float | None:
    """Percentil por el método del rango más cercano."""
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, int(-(-pct * len(ordered) // 100)))  # ceil(pct/100 * n)
    return round(ordered[rank - 1], 1)


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
    )
