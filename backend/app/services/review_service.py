"""Toma de caso, revisión médica (cierre), firma del médico y registro de reportes con metadatos tipo DICOM (SC-02)."""

import hashlib
import hmac
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.auth.security import verify_password
from app.config import settings
from app.db.models.case import Case, CaseStatus
from app.db.models.image import Image
from app.db.models.inference_result import InferenceResult
from app.db.models.review import AIValidation, ClinicalReview, Report, ReportSignature
from app.db.models.user import User
from app.schemas.reviews import AIValidationIn, ReviewIn, SignatureOut
from app.services import case_service, triage_service
from app.services.audit_service import audit
from app.services.errors import ConflictError, ForbiddenError, NotFoundError, ValidationError

RECOMMENDATION_LABELS = {
    "CONTROL_RUTINA": "Control de rutina",
    "CONTROL_6_MESES": "Control en 6 meses",
    "ESTUDIO_COMPLEMENTARIO": "Estudio complementario",
    "BIOPSIA": "Biopsia",
    "DERIVACION": "Derivación a especialista",
}


def _case(db: Session, case_id: int) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise NotFoundError("Caso no encontrado")
    return case


def take_case(db: Session, case_id: int, actor: User, ip: str | None = None) -> Case:
    """PRIORIZADO → EN_REVISION, asignando al médico."""
    case = _case(db, case_id)
    case_service.transition(case, CaseStatus.EN_REVISION)
    case.assigned_medico_id = actor.id
    audit(db, actor, "UPDATE", "case", case.id, {"status": "EN_REVISION", "assigned": True}, ip, commit=False)
    db.commit()
    db.refresh(case)
    return case


AI_VERDICT_LABELS = {
    "CONCORDANTE": "Concordante",
    "FALSO_POSITIVO": "Falso positivo",
    "FALSO_NEGATIVO": "Falso negativo",
    "NO_EVALUABLE": "No evaluable",
}
TRIAGE_ASSESSMENT_LABELS = {
    "APROPIADO": "Apropiado",
    "SOBREESTIMADO": "Sobreestimado (prioridad mayor a la necesaria)",
    "SUBESTIMADO": "Subestimado (prioridad menor a la necesaria)",
}


def validate_ai(
    db: Session, case_id: int, image_id: int, data: AIValidationIn, actor: User, ip: str | None = None
) -> AIValidation:
    """El médico aprueba (concordante) o rechaza (falso positivo/negativo) el resultado de IA de una imagen.

    Se puede corregir mientras el caso no esté cerrado. Queda auditado.
    """
    case = _case(db, case_id)
    if case.status == CaseStatus.CERRADO:
        raise ConflictError("El caso está cerrado: la validación ya no se puede modificar")
    image = db.query(Image).filter(Image.id == image_id, Image.case_id == case_id).first()
    if image is None:
        raise NotFoundError("Imagen no encontrada")
    result = image.inference_result
    if result is None:
        raise ConflictError("La imagen aún no tiene resultado de IA para validar")
    if data.verdict == "FALSO_POSITIVO" and not result.detected:
        raise ValidationError("Falso positivo solo aplica si la IA informó un hallazgo")
    if data.verdict == "FALSO_NEGATIVO" and result.detected:
        raise ValidationError("Falso negativo solo aplica si la IA no informó hallazgos")

    validation = db.query(AIValidation).filter(AIValidation.image_id == image.id).first()
    previous = validation.verdict if validation else None
    if validation is None:
        validation = AIValidation(image_id=image.id)
        db.add(validation)
    validation.inference_result_id = result.id
    validation.medico_id = actor.id
    validation.verdict = data.verdict
    validation.comment = (data.comment or "").strip() or None
    validation.ai_detected = result.detected
    validation.ai_model_version = result.model_version
    validation.ai_was_simulated = result.is_simulated
    db.flush()
    audit(
        db,
        actor,
        "UPDATE" if previous else "CREATE",
        "image",
        image.id,
        {"ai_validation": data.verdict, "previous": previous, "ai_simulated": result.is_simulated},
        ip,
        commit=False,
    )
    db.commit()
    db.refresh(validation)
    return validation


def pending_validations(db: Session, case_id: int) -> list[int]:
    """Imágenes con resultado de IA que el médico aún no valida."""
    rows = (
        db.query(Image.id)
        .join(InferenceResult, InferenceResult.image_id == Image.id)
        .outerjoin(AIValidation, AIValidation.image_id == Image.id)
        .filter(Image.case_id == case_id, AIValidation.id.is_(None))
        .all()
    )
    return [r[0] for r in rows]


def get_review(db: Session, case_id: int, actor: User, ip: str | None = None) -> ClinicalReview:
    _case(db, case_id)
    review = db.query(ClinicalReview).filter(ClinicalReview.case_id == case_id).first()
    if review is None:
        raise NotFoundError("El caso no tiene revisión médica")
    audit(db, actor, "VIEW", "case", case_id, {"review": True}, ip)
    return review


def create_review(
    db: Session, case_id: int, data: ReviewIn, actor: User, ip: str | None = None
) -> ClinicalReview:
    """Registra la revisión y cierra el caso. Solo desde EN_REVISION: un caso se cierra únicamente con revisión."""
    case = _case(db, case_id)
    if db.query(ClinicalReview).filter(ClinicalReview.case_id == case_id).first():
        raise ConflictError("El caso ya tiene una revisión médica registrada")
    if case.status != CaseStatus.EN_REVISION:
        raise ConflictError("Solo se puede registrar la revisión de un caso EN_REVISION (tómelo primero)")
    pending = pending_validations(db, case_id)
    if pending:
        raise ConflictError(
            f"Falta validar el resultado de IA de {len(pending)} imagen(es) antes de cerrar el caso"
        )
    triage = triage_service.current_result(db, case_id)
    review = ClinicalReview(
        case_id=case.id,
        medico_id=actor.id,
        birads_final=data.birads_final,
        findings=data.findings,
        recommendation=data.recommendation,
        triage_assessment=data.triage_assessment,
        triage_comment=(data.triage_comment or "").strip() or None,
        triage_level_at_review=triage.final_level.value if triage else None,
        triage_config_version_at_review=triage.config_version if triage else None,
    )
    db.add(review)
    case_service.transition(case, CaseStatus.CERRADO)
    if case.assigned_medico_id is None:
        case.assigned_medico_id = actor.id
    db.flush()
    audit(
        db,
        actor,
        "CREATE",
        "case",
        case.id,
        {
            "review_id": review.id,
            "status": "CERRADO",
            "recommendation": data.recommendation,
            "triage_assessment": data.triage_assessment,
        },
        ip,
        commit=False,
    )
    db.commit()
    db.refresh(review)
    return review


def build_dicom_metadata(db: Session, case: Case, review: ClinicalReview, medico: User) -> dict:
    """Metadatos tipo DICOM (SC-02). PatientID = código anónimo del caso, nunca el RUT."""
    images = db.query(Image).filter(Image.case_id == case.id).order_by(Image.uploaded_at).all()
    study_date = (images[0].uploaded_at if images else case.created_at).strftime("%Y%m%d")
    inferences = db.query(InferenceResult).join(Image).filter(Image.case_id == case.id).all()
    triage = triage_service.current_result(db, case.id)
    return {
        "PatientID": case.code,
        "StudyDate": study_date,
        "Modality": "MG",
        "StudyDescription": "Mamografía - apoyo a la priorización (Proyecto Aurora)",
        "NumberOfStudyRelatedInstances": len(images),
        "ReferringPhysicianName": medico.full_name,
        "Findings": review.findings,
        "BIRADSFinal": review.birads_final,
        "Recommendation": review.recommendation,
        "RecommendationLabel": RECOMMENDATION_LABELS[review.recommendation],
        "TriageLevel": triage.final_level.value if triage else None,
        "TriageScore": float(triage.score) if triage else None,
        "TriageConfigVersion": triage.config_version if triage else None,
        "AIModelVersions": sorted({i.model_version for i in inferences}),
        "AIIsSimulated": any(i.is_simulated for i in inferences) if inferences else None,
        "ReviewDate": review.created_at.strftime("%Y%m%d") if review.created_at else None,
        "TriageAssessment": review.triage_assessment,
        "AIValidation": ai_validation_summary(db, case.id),
    }


def ai_validation_summary(db: Session, case_id: int) -> str | None:
    """Resumen de la validación médica de la IA, p. ej. 'CONCORDANTE x2; FALSO_POSITIVO x1'."""
    rows = (
        db.query(AIValidation.verdict)
        .join(Image, Image.id == AIValidation.image_id)
        .filter(Image.case_id == case_id)
        .all()
    )
    if not rows:
        return None
    counts: dict[str, int] = {}
    for (verdict,) in rows:
        counts[verdict] = counts.get(verdict, 0) + 1
    return "; ".join(f"{v} x{n}" for v, n in sorted(counts.items()))


def _closed_case_with_review(db: Session, case_id: int) -> tuple[Case, ClinicalReview]:
    case = _case(db, case_id)
    review = db.query(ClinicalReview).filter(ClinicalReview.case_id == case_id).first()
    if review is None or case.status != CaseStatus.CERRADO:
        raise ConflictError("El reporte se genera cuando el caso tiene revisión médica y está cerrado")
    return case, review


def _content_hash(metadata: dict) -> str:
    """SHA-256 del contenido del reporte en JSON canónico, sin el bloque de firma."""
    content = {k: v for k, v in metadata.items() if k != "MedicalSignature"}
    raw = json.dumps(content, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _hmac(case_id: int, medico_id: int, signed_at: datetime, content_hash: str) -> str:
    message = f"{case_id}|{medico_id}|{_utc_iso(signed_at)}|{content_hash}"
    return hmac.new(settings.SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()


def _verification_code(signature: str) -> str:
    code = signature[:16].upper()
    return "-".join(code[i : i + 4] for i in range(0, 16, 4))


def _signature(db: Session, case_id: int) -> ReportSignature | None:
    return db.query(ReportSignature).filter(ReportSignature.case_id == case_id).first()


def signature_out(db: Session, sig: ReportSignature) -> SignatureOut:
    """Firma con su verificación: el HMAC coincide y el contenido actual del reporte es el que se firmó."""
    case, review = _closed_case_with_review(db, sig.case_id)
    medico = db.get(User, sig.medico_id)
    current = _content_hash(build_dicom_metadata(db, case, review, db.get(User, review.medico_id)))
    expected = _hmac(sig.case_id, sig.medico_id, sig.signed_at, sig.content_hash)
    return SignatureOut(
        id=sig.id,
        case_id=sig.case_id,
        medico_id=sig.medico_id,
        medico_name=medico.full_name,
        signed_at=sig.signed_at,
        content_hash=sig.content_hash,
        verification_code=_verification_code(sig.signature),
        valid=hmac.compare_digest(expected, sig.signature) and current == sig.content_hash,
    )


def sign_report(db: Session, case_id: int, password: str, actor: User, ip: str | None = None) -> SignatureOut:
    """El médico que revisó el caso firma su conformidad con el contenido del reporte, confirmando su contraseña."""
    case, review = _closed_case_with_review(db, case_id)
    if review.medico_id != actor.id:
        raise ForbiddenError("Solo el médico que registró la revisión puede firmar el reporte")
    if _signature(db, case_id):
        raise ConflictError("El reporte de este caso ya está firmado")
    if not verify_password(password, actor.password_hash):
        audit(db, actor, "SIGN_FAIL", "case", case_id, {"reason": "password"}, ip)
        raise ValidationError("Contraseña incorrecta: la firma no se registró")

    content_hash = _content_hash(build_dicom_metadata(db, case, review, actor))
    signed_at = datetime.now(timezone.utc)
    sig = ReportSignature(
        case_id=case_id,
        medico_id=actor.id,
        signed_at=signed_at,
        content_hash=content_hash,
        signature=_hmac(case_id, actor.id, signed_at, content_hash),
    )
    db.add(sig)
    db.flush()
    audit(
        db,
        actor,
        "SIGN",
        "case",
        case_id,
        {"signature_id": sig.id, "content_sha256": content_hash},
        ip,
        commit=False,
    )
    db.commit()
    db.refresh(sig)
    return signature_out(db, sig)


def get_signature(db: Session, case_id: int) -> SignatureOut:
    sig = _signature(db, case_id)
    if sig is None:
        raise NotFoundError("El reporte de este caso aún no está firmado")
    return signature_out(db, sig)


def report_metadata(db: Session, case_id: int, actor: User) -> dict:
    case, review = _closed_case_with_review(db, case_id)
    medico = db.get(User, review.medico_id)
    metadata = build_dicom_metadata(db, case, review, medico)
    sig = _signature(db, case_id)
    if sig is not None:
        signer = db.get(User, sig.medico_id)
        metadata["MedicalSignature"] = {
            "SignedBy": signer.full_name,
            "SignedAt": _utc_iso(sig.signed_at),
            "VerificationCode": _verification_code(sig.signature),
            "ContentSHA256": sig.content_hash,
        }
    return metadata


def register_report(
    db: Session, case_id: int, content_hash: str, actor: User, ip: str | None = None
) -> Report:
    metadata = report_metadata(db, case_id, actor)
    sig = _signature(db, case_id)
    if sig is None:
        raise ConflictError("El médico debe firmar el reporte antes de emitirlo")
    report = Report(
        case_id=case_id,
        generated_by=actor.id,
        dicom_metadata=metadata,
        content_hash=content_hash,
        signature_id=sig.id,
    )
    db.add(report)
    db.flush()
    audit(
        db,
        actor,
        "EXPORT",
        "report",
        report.id,
        {"case_id": case_id, "sha256": content_hash, "signature_id": sig.id},
        ip,
        commit=False,
    )
    db.commit()
    db.refresh(report)
    return report


def list_reports(db: Session, case_id: int) -> list[Report]:
    _case(db, case_id)
    return db.query(Report).filter(Report.case_id == case_id).order_by(Report.generated_at.desc()).all()
