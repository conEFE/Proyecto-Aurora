"""Toma de caso, revisión médica (cierre) y registro de reportes con metadatos tipo DICOM (SC-02)."""

from sqlalchemy.orm import Session

from app.db.models.case import Case, CaseStatus
from app.db.models.image import Image
from app.db.models.inference_result import InferenceResult
from app.db.models.review import AIValidation, ClinicalReview, Report
from app.db.models.user import User
from app.schemas.reviews import AIValidationIn, ReviewIn
from app.services import case_service, triage_service
from app.services.audit_service import audit
from app.services.errors import ConflictError, NotFoundError, ValidationError

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


def report_metadata(db: Session, case_id: int, actor: User) -> dict:
    case = _case(db, case_id)
    review = db.query(ClinicalReview).filter(ClinicalReview.case_id == case_id).first()
    if review is None or case.status != CaseStatus.CERRADO:
        raise ConflictError("El reporte se genera cuando el caso tiene revisión médica y está cerrado")
    medico = db.get(User, review.medico_id)
    return build_dicom_metadata(db, case, review, medico)


def register_report(
    db: Session, case_id: int, content_hash: str, actor: User, ip: str | None = None
) -> Report:
    metadata = report_metadata(db, case_id, actor)
    report = Report(
        case_id=case_id, generated_by=actor.id, dicom_metadata=metadata, content_hash=content_hash
    )
    db.add(report)
    db.flush()
    audit(
        db,
        actor,
        "EXPORT",
        "report",
        report.id,
        {"case_id": case_id, "sha256": content_hash},
        ip,
        commit=False,
    )
    db.commit()
    db.refresh(report)
    return report


def list_reports(db: Session, case_id: int) -> list[Report]:
    _case(db, case_id)
    return db.query(Report).filter(Report.case_id == case_id).order_by(Report.generated_at.desc()).all()
