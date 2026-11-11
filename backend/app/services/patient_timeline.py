"""Línea de tiempo del paciente: registro, consentimiento, casos, imágenes, triage y revisión médica.

Respeta la matriz de permisos: el ADMINISTRATIVO ve los hitos administrativos (casos, imágenes, cierre y
consentimiento), pero no el override del triage ni el resultado de la revisión médica, que son solo del MEDICO.
"""

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.case import Case
from app.db.models.image import Image
from app.db.models.patient import Patient
from app.db.models.privacy import ConsentEvent, ConsentText
from app.db.models.review import ClinicalReview
from app.db.models.triage import TriageResult
from app.db.models.user import User, UserRole
from app.schemas.patients import TimelineEvent
from app.services.audit_service import audit
from app.services.errors import NotFoundError

_ORDER = [
    "PATIENT_REGISTERED",
    "CONSENT_GRANTED",
    "CONSENT_WITHDRAWN",
    "PATIENT_BLOCKED",
    "CASE_CREATED",
    "IMAGES_UPLOADED",
    "TRIAGE_OVERRIDE",
    "REVIEW_REGISTERED",
    "CASE_CLOSED",
]


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def patient_timeline(db: Session, patient_id: int, actor: User, ip: str | None = None) -> list[TimelineEvent]:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise NotFoundError("Paciente no encontrado")
    is_medico = actor.role == UserRole.MEDICO
    names: dict[int, str] = {}

    def name(user_id: int | None) -> str | None:
        if user_id is None:
            return None
        if user_id not in names:
            user = db.get(User, user_id)
            names[user_id] = user.full_name if user else None
        return names[user_id]

    events: list[TimelineEvent] = []
    if patient.created_at:
        events.append(
            TimelineEvent(
                kind="PATIENT_REGISTERED", at=patient.created_at, actor_name=name(patient.created_by)
            )
        )

    consents = (
        db.query(ConsentEvent, ConsentText.version)
        .outerjoin(ConsentText, ConsentText.id == ConsentEvent.consent_text_id)
        .filter(ConsentEvent.patient_id == patient.id)
        .all()
    )
    for event, version in consents:
        detail = {"version": version}
        if event.note:
            detail["note"] = event.note
        events.append(
            TimelineEvent(
                kind="CONSENT_GRANTED" if event.action == "OTORGADO" else "CONSENT_WITHDRAWN",
                at=event.occurred_at,
                actor_name=name(event.registered_by),
                detail=detail,
            )
        )

    if patient.blocked_at:
        events.append(
            TimelineEvent(
                kind="PATIENT_BLOCKED",
                at=patient.blocked_at,
                actor_name=name(patient.blocked_by),
                detail={"reason": patient.block_reason} if patient.block_reason else {},
            )
        )

    cases = db.query(Case).filter(Case.patient_id == patient.id).all()
    case_ids = [c.id for c in cases]
    current_level: dict[int, str] = {}
    images: dict[int, tuple[int, datetime | None]] = {}
    if case_ids:
        for case_id, level in (
            db.query(TriageResult.case_id, TriageResult.final_level)
            .filter(TriageResult.case_id.in_(case_ids), TriageResult.is_current.is_(True))
            .all()
        ):
            current_level[case_id] = level.value
        for case_id, count, first in (
            db.query(Image.case_id, func.count(Image.id), func.min(Image.uploaded_at))
            .filter(Image.case_id.in_(case_ids))
            .group_by(Image.case_id)
            .all()
        ):
            images[case_id] = (count, first)

    for case in cases:
        ref = {"case_id": case.id, "case_code": case.code}
        symptoms = [
            label
            for flag, label in (
                (case.palpable_mass, "masa palpable"),
                (case.nipple_discharge, "secreción por el pezón"),
                (case.skin_or_nipple_changes, "cambios en la piel o el pezón"),
            )
            if flag
        ]
        events.append(
            TimelineEvent(
                kind="CASE_CREATED",
                at=case.created_at,
                actor_name=name(case.created_by),
                detail={"triage_level": current_level.get(case.id), "symptoms": symptoms},
                **ref,
            )
        )
        if case.id in images and images[case.id][1] is not None:
            count, first = images[case.id]
            events.append(TimelineEvent(kind="IMAGES_UPLOADED", at=first, detail={"count": count}, **ref))
        if case.closed_at:
            events.append(TimelineEvent(kind="CASE_CLOSED", at=case.closed_at, **ref))

    if is_medico and case_ids:
        codes = {c.id: c.code for c in cases}
        for result in (
            db.query(TriageResult)
            .filter(TriageResult.case_id.in_(case_ids), TriageResult.override_by.isnot(None))
            .all()
        ):
            events.append(
                TimelineEvent(
                    kind="TRIAGE_OVERRIDE",
                    at=result.computed_at,
                    case_id=result.case_id,
                    case_code=codes[result.case_id],
                    actor_name=name(result.override_by),
                    detail={
                        "computed_level": result.computed_level.value,
                        "final_level": result.final_level.value,
                        "reason": result.override_reason,
                    },
                )
            )
        for review in db.query(ClinicalReview).filter(ClinicalReview.case_id.in_(case_ids)).all():
            events.append(
                TimelineEvent(
                    kind="REVIEW_REGISTERED",
                    at=review.created_at,
                    case_id=review.case_id,
                    case_code=codes[review.case_id],
                    actor_name=name(review.medico_id),
                    detail={"birads_final": review.birads_final, "recommendation": review.recommendation},
                )
            )

    audit(db, actor, "VIEW", "patient", patient.id, {"timeline": True}, ip)
    events = [e for e in events if e.at is not None]
    # Del más reciente al más antiguo; con la misma hora, según el orden natural del proceso
    events.sort(key=lambda e: (_aware(e.at), _ORDER.index(e.kind)), reverse=True)
    return events
