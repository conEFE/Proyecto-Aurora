"""Validación básica de imágenes subidas (formato y dimensiones mínimas)."""

import io
from dataclasses import dataclass

from PIL import Image, UnidentifiedImageError

ALLOWED_FORMATS = {"PNG": "image/png", "JPEG": "image/jpeg"}
MIN_SIDE_PX = 100


@dataclass
class ImageInfo:
    width: int
    height: int
    mime_type: str


class ImageValidationError(ValueError):
    def __init__(self, message: str, status_code: int = 422):
        super().__init__(message)
        self.status_code = status_code


def inspect_image(content: bytes) -> ImageInfo:
    try:
        with Image.open(io.BytesIO(content)) as img:
            fmt = img.format
            width, height = img.size
            img.verify()
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ImageValidationError("El archivo no es una imagen válida", 415) from exc
    if fmt not in ALLOWED_FORMATS:
        raise ImageValidationError("Formato no soportado: solo se aceptan PNG y JPEG", 415)
    if width < MIN_SIDE_PX or height < MIN_SIDE_PX:
        raise ImageValidationError(f"La imagen debe medir al menos {MIN_SIDE_PX}×{MIN_SIDE_PX} píxeles")
    return ImageInfo(width=width, height=height, mime_type=ALLOWED_FORMATS[fmt])
