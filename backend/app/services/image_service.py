"""Carga de imágenes, almacenamiento cifrado e inferencia automática."""

import hashlib
import logging
import uuid

from sqlalchemy.orm import Session

from app.config import settings
from app.db.models.case import Case, CaseStatus
from app.db.models.image import ExamType, Image
from app.db.models.inference_result import InferenceResult
from app.db.models.user import User, UserRole
from app.inference.providers import get_provider
from app.schemas.images import ImageOut, InferenceOut
from app.services import case_service
from app.services.audit_service import audit
from app.services.errors import ConflictError, DomainError, NotFoundError, ValidationError
from app.storage.local import get_storage
from app.utils.quality import ImageValidationError, inspect_image

logger = logging.getLogger("aurora.images")


class PayloadTooLarge(DomainError):
    status_code = 413


class UnsupportedMedia(DomainError):
    status_code = 415


def _case(db: Session, case_id: int) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise NotFoundError("Caso no encontrado")
    return case


def _image(db: Session, case_id: int, image_id: int) -> Image:
    image = db.query(Image).filter(Image.id == image_id, Image.case_id == case_id).first()
    if image is None:
        raise NotFoundError("Imagen no encontrada")
    return image


def to_out(image: Image, viewer: User) -> ImageOut:
    out = ImageOut.model_validate(image)
    out.inference_status = "LISTO" if image.inference_result is not None else "PENDIENTE"
    if viewer.role == UserRole.MEDICO and image.inference_result is not None:
        out.inference = InferenceOut.model_validate(image.inference_result)
    return out


def upload_image(
    db: Session,
    case_id: int,
    filename: str,
    content: bytes,
    exam_type: ExamType,
    laterality: str | None,
    actor: User,
    ip: str | None = None,
) -> Image:
    case = _case(db, case_id)
    if case.status == CaseStatus.CERRADO:
        raise ConflictError("El caso está cerrado: no se pueden agregar imágenes")
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise PayloadTooLarge(f"La imagen supera el máximo permitido de {settings.MAX_UPLOAD_MB} MB")
    if not content:
        raise UnsupportedMedia("El archivo está vacío")
    try:
        info = inspect_image(content)
    except ImageValidationError as exc:
        if exc.status_code == 415:
            raise UnsupportedMedia(str(exc)) from exc
        raise ValidationError(str(exc)) from exc
    if exam_type is None:
        exam_type = ExamType.MAMOGRAFIA

    sha256 = hashlib.sha256(content).hexdigest()
    extension = "png" if info.mime_type == "image/png" else "jpg"
    # Nombre aleatorio en disco: el nombre original puede contener datos del paciente
    key = f"case_{case.id}/{uuid.uuid4().hex}.{extension}.enc"
    get_storage().save(key, content)

    image = Image(
        case_id=case.id,
        filename=(filename or "imagen")[:255],
        filepath=key,
        mime_type=info.mime_type,
        width=info.width,
        height=info.height,
        size_kb=len(content) // 1024,
        exam_type=exam_type,
        laterality=laterality,
        uploaded_by=actor.id,
        sha256=sha256,
    )
    db.add(image)
    # Datos nuevos: un caso priorizado vuelve a ABIERTO hasta recalcular el triage
    case_service.mark_data_changed(case)
    db.flush()
    audit(
        db,
        actor,
        "CREATE",
        "image",
        image.id,
        {"case_id": case.id, "exam_type": exam_type.value, "size_kb": image.size_kb},
        ip,
        commit=False,
    )
    db.commit()
    db.refresh(image)
    return image


def run_inference(db: Session, image_id: int) -> InferenceResult | None:
    """Ejecuta la inferencia de una imagen (idempotente) y dispara el recálculo del triage del caso."""
    image = db.get(Image, image_id)
    if image is None:
        return None
    if image.inference_result is not None:
        return image.inference_result
    content = get_storage().load(image.filepath)
    output = get_provider().analyze(content)
    result = InferenceResult(
        image_id=image.id,
        detected=output.detected,
        confidence=output.confidence,
        detections=output.detections,
        processing_time_ms=output.processing_time_ms,
        model_version=output.model_version,
        is_simulated=output.is_simulated,
        message=output.message,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    on_inference_completed(db, image.case_id)
    return result


def run_inference_task(image_id: int) -> None:
    """Tarea en segundo plano: abre su propia sesión de BD."""
    from app.deps import SessionLocal

    with SessionLocal() as db:
        try:
            run_inference(db, image_id)
        except Exception:  # la carga ya quedó registrada; se puede reintentar luego
            logger.exception("Falló la inferencia de la imagen %s", image_id)


def on_inference_completed(db: Session, case_id: int) -> None:
    """Hook: recalcula el triage del caso al terminar la inferencia (se conecta en S5)."""


def list_images(db: Session, case_id: int, viewer: User) -> list[ImageOut]:
    case = _case(db, case_id)
    return [to_out(img, viewer) for img in case.images]


def get_image_file(
    db: Session, case_id: int, image_id: int, actor: User, ip: str | None = None
) -> tuple[bytes, str]:
    image = _image(db, case_id, image_id)
    try:
        content = get_storage().load(image.filepath)
    except FileNotFoundError as exc:
        raise NotFoundError("Archivo de imagen no encontrado") from exc
    audit(db, actor, "VIEW", "image", image.id, {"case_id": case_id}, ip)
    return content, image.mime_type


def get_inference(
    db: Session, case_id: int, image_id: int, actor: User, ip: str | None = None
) -> InferenceResult:
    image = _image(db, case_id, image_id)
    if image.inference_result is None:
        raise NotFoundError("La inferencia de esta imagen aún no está disponible")
    audit(db, actor, "VIEW", "image", image.id, {"case_id": case_id, "inference": True}, ip)
    return image.inference_result
