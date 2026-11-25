"""Métricas agregadas del dashboard (sin datos identificables)."""

import math
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models.case import Case, CaseStatus
from app.db.models.error_log import ErrorLog
from app.db.models.image import Image
from app.db.models.review import (
    AI_VERDICTS,
    TRIAGE_ASSESSMENTS,
    AIValidation,
    ClinicalReview,
    ReportSignature,
    RequestMetric,
)
from app.db.models.triage import TriageLevel, TriageResult
from app.db.models.user import MedicalSpecialty, User, UserRole
from app.schemas.reviews import (
    DashboardCase,
    DashboardMetrics,
    DoctorComparison,
    DoctorStats,
    ModelPerformanceReport,
    ModelVersionPerformance,
    Reviewer,
    WeekPoint,
)

# KPI K5: exactitud del modelo ≥ 90 %, evaluada solo con resultados reales y una muestra mínima
K5_TARGET = 0.85
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


def _cases_query(
    db: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    level: TriageLevel | None = None,
    medico_id: int | None = None,
):
    """Casos del período, con filtros opcionales por nivel vigente y por médico que los revisa o revisó."""
    q = db.query(Case)
    if date_from:
        q = q.filter(Case.created_at >= date_from)
    if date_to:
        q = q.filter(Case.created_at <= date_to)
    if level is not None:
        q = q.join(
            TriageResult, (TriageResult.case_id == Case.id) & TriageResult.is_current.is_(True)
        ).filter(TriageResult.final_level == level)
    if medico_id is not None:
        reviewed = select(ClinicalReview.case_id).where(ClinicalReview.medico_id == medico_id)
        q = q.filter(or_(Case.assigned_medico_id == medico_id, Case.id.in_(reviewed)))
    return q


def metrics(
    db: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    alta_pending_hours: int | None = None,
    now: datetime | None = None,
    level: TriageLevel | None = None,
    medico_id: int | None = None,
) -> DashboardMetrics:
    now = now or datetime.now(timezone.utc)
    hours = alta_pending_hours if alta_pending_hours is not None else settings.ALTA_PENDING_HOURS

    cases = _cases_query(db, date_from, date_to, level, medico_id).all()
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

    # Errores 5xx del servidor (KPI K9)
    errors_q = db.query(func.count(ErrorLog.id))
    if date_from:
        errors_q = errors_q.filter(ErrorLog.occurred_at >= date_from)
    if date_to:
        errors_q = errors_q.filter(ErrorLog.occurred_at <= date_to)
    server_errors = errors_q.scalar() or 0

    weeks: list[WeekPoint] = []
    if case_ids:
        week_col = func.date_trunc("week", Case.created_at).label("week")
        rows = db.query(week_col, Case.id).filter(Case.id.in_(case_ids)).order_by(week_col).all()
        per_week: dict[str, dict] = {}
        for w, case_id in rows:
            point = per_week.setdefault(
                w.date().isoformat(), {"cases": 0, "by_level": {lvl.value: 0 for lvl in TriageLevel}}
            )
            point["cases"] += 1
            if case_id in current:
                point["by_level"][current[case_id].final_level.value] += 1
        weeks = [WeekPoint(week_start=k, **v) for k, v in per_week.items()]

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
        server_errors=server_errors,
        server_error_rate=round(server_errors / len(durations), 4) if durations else None,
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


def reviewers(db: Session) -> list[Reviewer]:
    """Médicos (activos o no) para filtrar el dashboard por quien revisa."""
    rows = db.query(User).filter(User.role == UserRole.MEDICO).order_by(User.full_name).all()
    return [
        Reviewer(
            id=u.id, full_name=u.full_name, is_active=u.is_active,
            specialty=u.specialty.value if u.specialty else None,
        )
        for u in rows
    ]


def case_rows(
    db: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    level: TriageLevel | None = None,
    medico_id: int | None = None,
    alta_pending_hours: int | None = None,
    now: datetime | None = None,
    limit: int = 500,
) -> list[DashboardCase]:
    """Casos de un período (solo el código anónimo, sin datos del paciente), con su espera y si están atrasados.

    Atrasado = la misma regla del indicador: ALTA vigente, sin cerrar y creado hace más de `alta_pending_hours`.
    """
    now = now or datetime.now(timezone.utc)
    hours = alta_pending_hours if alta_pending_hours is not None else settings.ALTA_PENDING_HOURS
    cases = _cases_query(db, date_from, date_to, level, medico_id).order_by(Case.created_at).limit(limit).all()
    ids = [c.id for c in cases]
    if not ids:
        return []
    current = {
        r.case_id: r
        for r in db.query(TriageResult).filter(TriageResult.case_id.in_(ids), TriageResult.is_current.is_(True))
    }
    first = dict(
        db.query(TriageResult.case_id, func.min(TriageResult.computed_at))
        .filter(TriageResult.case_id.in_(ids))
        .group_by(TriageResult.case_id)
        .all()
    )
    reviews = {rv.case_id: rv for rv in db.query(ClinicalReview).filter(ClinicalReview.case_id.in_(ids))}
    medico_ids = {rv.medico_id for rv in reviews.values()} | {c.assigned_medico_id for c in cases if c.assigned_medico_id}
    names = dict(db.query(User.id, User.full_name).filter(User.id.in_(medico_ids)).all()) if medico_ids else {}
    cutoff = now - timedelta(hours=hours)
    rows = []
    for c in cases:
        cur = current.get(c.id)
        rv = reviews.get(c.id)
        created = _aware(c.created_at)
        end = _aware(rv.created_at) if rv and rv.created_at else now
        reviewer_id = rv.medico_id if rv else c.assigned_medico_id
        rows.append(
            DashboardCase(
                id=c.id,
                code=c.code,
                level=cur.final_level.value if cur else None,
                status=c.status.value,
                created_at=c.created_at,
                triaged_at=first.get(c.id),
                reviewed_at=rv.created_at if rv else None,
                reviewer=names.get(reviewer_id) if reviewer_id else None,
                waiting_hours=round((end - created).total_seconds() / 3600, 1),
                late=bool(
                    cur
                    and cur.final_level == TriageLevel.ALTA
                    and c.status != CaseStatus.CERRADO
                    and created < cutoff
                ),
            )
        )
    rows.sort(key=lambda r: (not r.late, -r.waiting_hours))
    return rows


def _in_range(col, date_from: datetime | None, date_to: datetime | None):
    conds = []
    if date_from:
        conds.append(col >= date_from)
    if date_to:
        conds.append(col <= date_to)
    return conds


def compare_doctors(
    db: Session,
    medico_ids: list[int] | None = None,
    specialty: MedicalSpecialty | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    alta_pending_hours: int | None = None,
    include_inactive: bool = False,
    now: datetime | None = None,
) -> DoctorComparison:
    """Comparador de médicos para jefatura y finanzas: productividad, tiempos, carga y concordancia.

    La actividad (revisiones, firmas, cierres, overrides, validaciones) se cuenta por la fecha en que ocurrió;
    la carga (asignados abiertos y ALTA atrasados) es la de ahora. No expone datos de pacientes.
    """
    now = now or datetime.now(timezone.utc)
    hours = alta_pending_hours if alta_pending_hours is not None else settings.ALTA_PENDING_HOURS

    q = db.query(User).filter(User.role == UserRole.MEDICO)
    if not include_inactive and not medico_ids:
        q = q.filter(User.is_active.is_(True))
    if specialty is not None:
        q = q.filter(User.specialty == specialty)
    if medico_ids:
        q = q.filter(User.id.in_(medico_ids))
    doctors = q.order_by(User.full_name).all()
    ids = [d.id for d in doctors]

    start = _aware(date_from) if date_from else None
    if start is None and ids:
        first = (
            db.query(func.min(ClinicalReview.created_at)).filter(ClinicalReview.medico_id.in_(ids)).scalar()
        )
        start = _aware(first) if first else None
    end = _aware(date_to) if date_to else now
    weeks = max(1.0, (end - start).total_seconds() / (7 * 86400)) if start else 1.0

    def empty() -> dict:
        return {
            "reviews": 0, "signed": 0, "closed": 0, "overrides": 0, "hours": [],
            "open": 0, "late": 0, "val": 0, "val_ok": 0, "val_eval": 0, "ta": 0, "ta_ok": 0,
        }

    acc = {i: empty() for i in ids}
    if ids:
        reviews = (
            db.query(ClinicalReview)
            .filter(ClinicalReview.medico_id.in_(ids), *_in_range(ClinicalReview.created_at, date_from, date_to))
            .all()
        )
        case_ids = {rv.case_id for rv in reviews}
        first_triage: dict[int, datetime] = {}
        if case_ids:
            for case_id, first in (
                db.query(TriageResult.case_id, func.min(TriageResult.computed_at))
                .filter(TriageResult.case_id.in_(case_ids))
                .group_by(TriageResult.case_id)
                .all()
            ):
                first_triage[case_id] = first
        for rv in reviews:
            a = acc[rv.medico_id]
            a["reviews"] += 1
            if rv.case_id in first_triage and rv.created_at:
                a["hours"].append((_aware(rv.created_at) - _aware(first_triage[rv.case_id])).total_seconds() / 3600)
            if rv.triage_assessment in TRIAGE_ASSESSMENTS:
                a["ta"] += 1
                a["ta_ok"] += 1 if rv.triage_assessment == "APROPIADO" else 0

        for medico_id, n in (
            db.query(ReportSignature.medico_id, func.count(ReportSignature.id))
            .filter(ReportSignature.medico_id.in_(ids), *_in_range(ReportSignature.signed_at, date_from, date_to))
            .group_by(ReportSignature.medico_id)
            .all()
        ):
            acc[medico_id]["signed"] = n

        for medico_id, n in (
            db.query(TriageResult.override_by, func.count(TriageResult.id))
            .filter(TriageResult.override_by.in_(ids), *_in_range(TriageResult.computed_at, date_from, date_to))
            .group_by(TriageResult.override_by)
            .all()
        ):
            acc[medico_id]["overrides"] = n

        for medico_id, verdict in (
            db.query(AIValidation.medico_id, AIValidation.verdict)
            .filter(AIValidation.medico_id.in_(ids), *_in_range(AIValidation.created_at, date_from, date_to))
            .all()
        ):
            a = acc[medico_id]
            a["val"] += 1
            if verdict != "NO_EVALUABLE":
                a["val_eval"] += 1
                a["val_ok"] += 1 if verdict == "CONCORDANTE" else 0

        # Cierres del período: casos asignados al médico o revisados por él
        reviewed_by = dict(
            db.query(ClinicalReview.case_id, ClinicalReview.medico_id)
            .filter(ClinicalReview.medico_id.in_(ids))
            .all()
        )
        closed = (
            db.query(Case.id, Case.assigned_medico_id)
            .filter(Case.status == CaseStatus.CERRADO, *_in_range(Case.closed_at, date_from, date_to))
            .filter(or_(Case.assigned_medico_id.in_(ids), Case.id.in_(list(reviewed_by) or [-1])))
            .all()
        )
        for case_id, assigned in closed:
            owner = reviewed_by.get(case_id) or assigned
            if owner in acc:
                acc[owner]["closed"] += 1

        # Carga actual
        cutoff = now - timedelta(hours=hours)
        open_cases = (
            db.query(Case.id, Case.assigned_medico_id, Case.created_at)
            .filter(Case.assigned_medico_id.in_(ids), Case.status != CaseStatus.CERRADO)
            .all()
        )
        levels = {}
        if open_cases:
            levels = dict(
                db.query(TriageResult.case_id, TriageResult.final_level)
                .filter(TriageResult.case_id.in_([c.id for c in open_cases]), TriageResult.is_current.is_(True))
                .all()
            )
        for case_id, medico_id, created_at in open_cases:
            a = acc[medico_id]
            a["open"] += 1
            if levels.get(case_id) == TriageLevel.ALTA and created_at and _aware(created_at) < cutoff:
                a["late"] += 1

    def build(base: dict, a: dict, divisor: int = 1) -> DoctorStats:
        hrs = a["hours"]
        return DoctorStats(
            **base,
            reviews=round(a["reviews"] / divisor) if divisor > 1 else a["reviews"],
            reports_signed=round(a["signed"] / divisor) if divisor > 1 else a["signed"],
            cases_closed=round(a["closed"] / divisor) if divisor > 1 else a["closed"],
            overrides=round(a["overrides"] / divisor) if divisor > 1 else a["overrides"],
            reviews_per_week=round(a["reviews"] / divisor / weeks, 2),
            avg_review_hours=round(sum(hrs) / len(hrs), 2) if hrs else None,
            p95_review_hours=percentile(hrs, 95),
            open_assigned=round(a["open"] / divisor) if divisor > 1 else a["open"],
            alta_late=round(a["late"] / divisor) if divisor > 1 else a["late"],
            ai_validations=round(a["val"] / divisor) if divisor > 1 else a["val"],
            ai_agreement_rate=_ratio(a["val_ok"], a["val_eval"]),
            triage_agreement_rate=_ratio(a["ta_ok"], a["ta"]),
        )

    rows = [
        build(
            {
                "id": d.id, "full_name": d.full_name, "is_active": d.is_active,
                "specialty": d.specialty.value if d.specialty else None,
            },
            acc[d.id],
        )
        for d in doctors
    ]
    team = None
    if doctors:
        total = empty()
        for a in acc.values():
            for k, v in a.items():
                total[k] = total[k] + v
        team = build(
            {"id": 0, "full_name": "Promedio del equipo", "is_active": True, "specialty": None}, total, len(doctors)
        )
    return DoctorComparison(
        date_from=date_from,
        date_to=date_to,
        weeks=round(weeks, 2),
        alta_pending_threshold_hours=hours,
        doctors=rows,
        team=team,
    )
