from PIL import Image
import io
from typing import Tuple, Dict, Any

def validate_image_quality(file_content: bytes) -> Tuple[bool, Dict[str, Any]]:
    """Valida la calidad básica de una imagen.
    
    Args:
        file_content: Contenido binario de la imagen
        
    Returns:
        Tuple[bool, dict]: (quality_ok, metadata)
            - quality_ok: True si pasa validaciones básicas
            - metadata: dict con width, height, size_bytes, mime, error
    """
    try:
        img = Image.open(io.BytesIO(file_content))
        width, height = img.size
        size_bytes = len(file_content)
        
        # Validaciones básicas
        quality_ok = (
            size_bytes < 10 * 1024 * 1024 and  # < 10MB
            width >= 100 and height >= 100      # dimensiones mínimas razonables
        )
        
        return quality_ok, {
            "width": width,
            "height": height,
            "size_bytes": size_bytes,
            "mime": img.format or "unknown",
            "error": None
        }
    except Exception as e:
        return False, {
            "width": None,
            "height": None,
            "size_bytes": len(file_content),
            "mime": None,
            "error": str(e)
        }