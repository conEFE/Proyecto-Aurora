from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.bearer import get_current_user
from app.db.models.case import Case
from app.db.models.image import Image
from app.db.models.user import User
from app.deps import get_db
from app.storage.fs import load_image_file, save_image_file
from app.utils.quality import validate_image_quality

router = APIRouter()


class ImageResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    mime_type: str
    width: int | None = None
    height: int | None = None
    size_kb: int | None = None
    uploaded_at: datetime
    case_id: int

    class Config:
        from_attributes = True


@router.post("/{case_id}/images", response_model=ImageResponse)
async def upload_image(
    case_id: int,
    file: UploadFile = File(...),
    tipo_imagen: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sube una imagen médica para un caso"""
    # Verificar que el caso exista
    caso = db.query(Case).filter(Case.id == case_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    # Verificar permisos
    if caso.medico_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="No tienes acceso a este caso")

    # Leer contenido del archivo
    file_content = await file.read()

    # Validar calidad
    quality_ok, metadata = validate_image_quality(file_content)

    if not quality_ok:
        raise HTTPException(
            status_code=400,
            detail=f"Image quality validation failed: {metadata.get('error', 'Invalid image')}",
        )

    # Guardar archivo en filesystem
    try:
        relative_path = save_image_file(str(case_id), file.filename or "image", file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")

    # Guardar en BD
    nueva_imagen = Image(
        case_id=case_id,
        filename=file.filename or "image",
        filepath=relative_path,
        mime_type=metadata.get("mime", "unknown"),
        width=metadata.get("width"),
        height=metadata.get("height"),
        size_kb=metadata.get("size_bytes", 0) // 1024,
    )

    db.add(nueva_imagen)
    db.commit()
    db.refresh(nueva_imagen)

    return nueva_imagen


@router.get("/{case_id}/images", response_model=list[ImageResponse])
def get_case_images(
    case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Obtiene todas las imágenes de un caso"""
    # Verificar que el caso exista
    caso = db.query(Case).filter(Case.id == case_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    # Verificar permisos
    if caso.medico_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="No tienes acceso a este caso")

    # Obtener imágenes del caso
    imagenes = db.query(Image).filter(Image.case_id == case_id).order_by(Image.uploaded_at.desc()).all()

    return imagenes


@router.get("/{case_id}/images/{image_id}/file")
async def get_image_file(
    case_id: int, image_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Sirve una imagen desencriptada"""
    # Verificar que el caso exista
    caso = db.query(Case).filter(Case.id == case_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    # Verificar permisos
    if caso.medico_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="No tienes acceso a este caso")

    # Obtener imagen de BD
    imagen = db.query(Image).filter(Image.id == image_id, Image.case_id == case_id).first()
    if not imagen:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    try:
        # Cargar y desencriptar imagen
        image_content = load_image_file(imagen.filepath)

        # Devolver imagen con el tipo MIME correcto
        return Response(content=image_content, media_type=imagen.mime_type or "image/jpeg")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo de imagen no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar imagen: {str(e)}")
