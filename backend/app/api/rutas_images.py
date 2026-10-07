from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth.rbac import require_roles
from app.db.models.image import ExamType
from app.db.models.user import User, UserRole
from app.deps import get_db
from app.schemas.images import ImageOut, InferenceOut
from app.services import image_service
from app.services.audit_service import client_ip

router = APIRouter()
clinical_staff = require_roles(UserRole.ADMINISTRATIVO, UserRole.MEDICO)
medico_only = require_roles(UserRole.MEDICO)


@router.post("/{case_id}/images", response_model=ImageOut, status_code=201)
async def upload_image(
    case_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    exam_type: ExamType = Form(ExamType.MAMOGRAFIA),
    laterality: Literal["L", "R"] | None = Form(None),
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Sube una imagen (PNG o JPEG, máx. MAX_UPLOAD_MB). La inferencia corre en segundo plano."""
    content = await file.read()
    image = image_service.upload_image(
        db, case_id, file.filename or "imagen", content, exam_type, laterality, actor, client_ip(request)
    )
    background_tasks.add_task(image_service.run_inference_task, image.id)
    return image_service.to_out(image, actor)


@router.get("/{case_id}/images", response_model=list[ImageOut])
def list_images(
    case_id: int,
    actor: User = Depends(clinical_staff),
    db: Session = Depends(get_db),
):
    """Metadatos de las imágenes del caso. El resultado de IA solo se incluye para el rol MEDICO."""
    return image_service.list_images(db, case_id, actor)


@router.get("/{case_id}/images/{image_id}/file")
def get_image_file(
    case_id: int,
    image_id: int,
    request: Request,
    actor: User = Depends(medico_only),
    db: Session = Depends(get_db),
):
    """Devuelve la imagen descifrada (solo MEDICO; queda registrado como VIEW)."""
    content, mime = image_service.get_image_file(db, case_id, image_id, actor, client_ip(request))
    return Response(content=content, media_type=mime, headers={"Cache-Control": "no-store"})


@router.get("/{case_id}/images/{image_id}/inference", response_model=InferenceOut)
def get_inference(
    case_id: int,
    image_id: int,
    request: Request,
    actor: User = Depends(medico_only),
    db: Session = Depends(get_db),
):
    """Resultado de la inferencia de una imagen (solo MEDICO)."""
    return image_service.get_inference(db, case_id, image_id, actor, client_ip(request))
