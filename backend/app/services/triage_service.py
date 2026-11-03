"""Triage por caso: cálculo, persistencia con historial, override, cola, configuración y notificaciones.

La función pura de cálculo vive en `triage_engine.compute_triage` (se re-exporta aquí).
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import case as sql_case
from sqlalchemy.orm import Session

from app.db.models.case import Case, CaseStatus
from app.db.models.image import Image
from app.db.models.inference_result import InferenceResult
from app.db.models.patient import Patient
from app.db.models.triage import LEVEL_RANK, Notification, TriageConfig, TriageLevel, TriageResult
from app.db.models.user import User, UserRole
from app.schemas.triage import QueueItem, TriageParams
from app.services import case_service
from app.services.audit_service import audit
from app.services.errors import ConflictError, NotFoundError
from app.services.triage_engine import DEFAULT_PARAMS_V1, TriageOutput, compute_triage  # noqa: F401

logger = logging.getLogger("aurora.triage")

OPEN_STATUSES = (CaseStatus.ABIERTO, CaseStatus.PRIORIZADO, CaseStatus.EN_REVISION)


# --- Configuración -----------------------------------------------------------


def active_config(db: Session) -> TriageConfig:
    config = db.query(TriageConfig).filter(TriageConfig.is_active.is_(True)).first()
    if config is None:
        raise ConflictError("No hay una configuración de triage activa")
    return config


def list_configs(db: Session) -> list[TriageConfig]:
    return db.query(TriageConfig).order_by(TriageConfig.version.desc()).all()


def ensure_default_config(db: Session) -> TriageConfig:
    config = db.query(TriageConfig).filter(TriageConfig.is_active.is_(True)).first()
    if config is None:
        config = TriageConfig(
            version=1,
            params=DEFAULT_PARAMS_V1,
            is_active=True,
            created_by=None,
            change_reason="Configuración inicial v1 (propuesta técnica, pendiente de validación médica)",
        )
        db.add(config)
        db.commit()
    return config


def create_config(
    db: Session, params: TriageParams, change_reason: str, actor: User, ip: str | None = None
) -> tuple[TriageConfig, int]:
    """Crea una nueva versión activa y recalcula los casos no cerrados."""
    previous = active_config(db)
    last_version = db.query(TriageConfig.version).order_by(TriageConfig.version.desc()).limit(1).scalar() or 0
    previous.is_active = False
    db.flush()
    config = TriageConfig(
        version=last_version + 1,
        params=params.model_dump(mode="json"),
        is_active=True,
        created_by=actor.id,
        change_reason=change_reason.strip(),
    )
    db.add(config)
    db.flush()
    audit(
        db,
        actor,
        "CONFIG_CHANGE",
        "triage_config",
        config.id,
        {"version": config.version, "previous_version": previous.version},
        ip,
        commit=False,
    )
    db.commit()
    db.refresh(config)

    count = 0
    for case in db.query(Case).filter(Case.status.in_(OPEN_STATUSES)).all():
        recalculate(db, case, keep_override=True)
        count += 1
    return config, count


# --- Cálculo y persistencia --------------------------------------------------


def current_result(db: Session, case_id: int) -> TriageResult | None:
    return (
        db.query(TriageResult)
        .filter(TriageResult.case_id == case_id, TriageResult.is_current.is_(True))
        .first()
    )


def _inferences(db: Session, case_id: int) -> list[InferenceResult]:
    return db.query(InferenceResult).join(Image).filter(Image.case_id == case_id).all()


def recalculate(
    db: Session, case: Case, keep_override: bool = False, now: datetime | None = None
) -> TriageResult | None:
    """Calcula y guarda un nuevo triage vigente. Los anteriores quedan con is_current=false.

    keep_override=True (cambio de configuración, mismos datos clínicos): se conserva el override del médico.
    Si cambiaron los datos del caso (imágenes, síntomas, antecedentes) el override no se arrastra: el médico
    debe volver a evaluar con la información nueva.
    """
    if case.status == CaseStatus.CERRADO:
        return None
    config = active_config(db)
    params = TriageParams.model_validate(config.params)
    patient = db.get(Patient, case.patient_id)
    inferences = _inferences(db, case.id)
    output: TriageOutput = compute_triage(case, patient, inferences, params, now=now)
    output.breakdown["ai_is_simulated"] = any(i.is_simulated for i in inferences) if inferences else None
    output.breakdown["images_analyzed"] = len(inferences)

    previous = current_result(db, case.id)
    final_level, override_by, override_reason = output.computed_level, None, None
    if previous is not None:
        if keep_override and previous.override_by is not None:
            final_level = previous.final_level
            override_by, override_reason = previous.override_by, previous.override_reason
        previous.is_current = False
        db.flush()

    result = TriageResult(
        case_id=case.id,
        config_version=config.version,
        score=output.score,
        computed_level=output.computed_level,
        escalation_rule=output.escalation_rule,
        breakdown=output.breakdown,
        final_level=final_level,
        override_by=override_by,
        override_reason=override_reason,
        is_current=True,
    )
    db.add(result)
    if case.status == CaseStatus.ABIERTO:
        case_service.transition(case, CaseStatus.PRIORIZADO)
    db.flush()

    if previous is None and case.created_at is not None:
        created = case.created_at if case.created_at.tzinfo else case.created_at.replace(tzinfo=timezone.utc)
        elapsed = (datetime.now(timezone.utc) - created).total_seconds()
        logger.info("KPI creación→triage caso %s: %.1f s (meta ≤ 300 s)", case.code, elapsed)

    was_alta = previous is not None and previous.final_level == TriageLevel.ALTA
    if final_level == TriageLevel.ALTA and not was_alta:
        _notify_medicos(db, case, result)
    db.commit()
    db.refresh(result)
    return result


def recalculate_for_patient(db: Session, patient_id: int) -> None:
    for case in db.query(Case).filter(Case.patient_id == patient_id, Case.status.in_(OPEN_STATUSES)).all():
        case_service.mark_data_changed(case)
        recalculate(db, case)


def _notify_medicos(db: Session, case: Case, result: TriageResult) -> None:
    reason = f" (regla {result.escalation_rule})" if result.escalation_rule else ""
    message = f"Caso {case.code} priorizado como ALTA{reason}"
    for medico in db.query(User).filter(User.role == UserRole.MEDICO, User.is_active.is_(True)).all():
        db.add(Notification(user_id=medico.id, case_id=case.id, message=message))


# --- Lectura y override ------------------------------------------------------


def _case(db: Session, case_id: int) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise NotFoundError("Caso no encontrado")
    return case


def get_current(db: Session, case_id: int, actor: User, ip: str | None = None) -> TriageResult:
    _case(db, case_id)
    result = current_result(db, case_id)
    if result is None:
        raise NotFoundError("El caso aún no tiene triage")
    audit(db, actor, "VIEW", "triage", result.id, {"case_id": case_id}, ip)
    return result


def history(db: Session, case_id: int, actor: User, ip: str | None = None) -> list[TriageResult]:
    _case(db, case_id)
    items = (
        db.query(TriageResult)
        .filter(TriageResult.case_id == case_id)
        .order_by(TriageResult.computed_at.desc(), TriageResult.id.desc())
        .all()
    )
    audit(db, actor, "VIEW", "triage", None, {"case_id": case_id, "history": True}, ip)
    return items


def manual_recalculate(db: Session, case_id: int, actor: User, ip: str | None = None) -> TriageResult:
    case = _case(db, case_id)
    if case.status == CaseStatus.CERRADO:
        raise ConflictError("El caso está cerrado: su triage no se recalcula")
    result = recalculate(db, case, keep_override=True)
    audit(db, actor, "UPDATE", "triage", result.id, {"case_id": case_id, "manual": True}, ip)
    return result


def override(
    db: Session, case_id: int, level: TriageLevel, reason: str, actor: User, ip: str | None = None
) -> TriageResult:
    case = _case(db, case_id)
    if case.status == CaseStatus.CERRADO:
        raise ConflictError("El caso está cerrado y es de solo lectura")
    result = current_result(db, case_id)
    if result is None:
        raise ConflictError("El caso aún no tiene triage calculado")
    previous_level = result.final_level
    result.final_level = level
    result.override_by = actor.id
    result.override_reason = reason
    audit(
        db,
        actor,
        "OVERRIDE",
        "triage",
        result.id,
        {
            "case_id": case_id,
            "from": previous_level.value,
            "to": level.value,
            "computed": result.computed_level.value,
        },
        ip,
        commit=False,
    )
    if level == TriageLevel.ALTA and previous_level != TriageLevel.ALTA:
        _notify_medicos(db, case, result)
    db.commit()
    db.refresh(result)
    return result


# --- Cola priorizada -----------------------------------------------------------


def queue(
    db: Session,
    viewer: User,
    statuses: tuple[CaseStatus, ...] = (CaseStatus.PRIORIZADO, CaseStatus.EN_REVISION),
    ip: str | None = None,
) -> list[QueueItem]:
    """Orden: final_level (ALTA > MEDIA > BAJA), score descendente y antigüedad (created_at ascendente)."""
    level_order = sql_case(*[(TriageResult.final_level == lvl, rank) for lvl, rank in LEVEL_RANK.items()])
    rows = (
        db.query(Case, TriageResult)
        .join(TriageResult, (TriageResult.case_id == Case.id) & TriageResult.is_current.is_(True))
        .filter(Case.status.in_(statuses))
        .order_by(level_order, TriageResult.score.desc(), Case.created_at.asc(), Case.id.asc())
        .all()
    )
    now = datetime.now(timezone.utc)
    is_medico = viewer.role == UserRole.MEDICO
    items = []
    for case, result in rows:
        created = case.created_at if case.created_at.tzinfo else case.created_at.replace(tzinfo=timezone.utc)
        item = QueueItem(
            code=case.code,
            level=result.final_level,
            status=case.status,
            waiting_hours=round((now - created).total_seconds() / 3600, 1),
        )
        if is_medico:
            item.case_id = case.id
            item.score = float(result.score)
            item.escalation_rule = result.escalation_rule
            item.overridden = result.override_by is not None
            item.patient_name = f"{case.patient.first_name} {case.patient.last_name}"
            item.created_at = case.created_at
        items.append(item)
    audit(db, viewer, "VIEW", "triage", None, {"queue": True, "results": len(items)}, ip)
    return items


# --- Notificaciones ------------------------------------------------------------


def list_notifications(db: Session, user: User, unread_only: bool = False) -> list[Notification]:
    q = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only:
        q = q.filter(Notification.read_at.is_(None))
    return q.order_by(Notification.read_at.is_not(None), Notification.created_at.desc()).limit(50).all()


def mark_read(db: Session, notification_id: int, user: User) -> Notification:
    notification = db.get(Notification, notification_id)
    if notification is None or notification.user_id != user.id:
        raise NotFoundError("Notificación no encontrada")
    if notification.read_at is None:
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
    return notification
