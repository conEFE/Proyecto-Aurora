import os
from pathlib import Path
from app.config import settings
from app.storage.encryption import encrypt_data, decrypt_data

def ensure_case_directory(case_id: str) -> Path:
    """Crea el directorio para un caso si no existe"""
    case_dir = Path(settings.FILES_DIR) / f"case_{case_id}"
    case_dir.mkdir(parents=True, exist_ok=True)
    return case_dir

def save_image_file(case_id: str, filename: str, file_content: bytes) -> str:
    """Guarda un archivo de imagen encriptado en el directorio del caso.
    
    Returns:
        str: Ruta relativa al FILES_DIR donde se guardó el archivo
    """
    case_dir = ensure_case_directory(case_id)
    safe_filename = "".join(c for c in filename if c.isalnum() or c in ".-_")
    file_path = case_dir / safe_filename
    
    # Encriptar el contenido antes de guardar
    encrypted_content = encrypt_data(file_content)
    
    file_path.write_bytes(encrypted_content)
    return str(file_path.relative_to(Path(settings.FILES_DIR)))

def load_image_file(relative_path: str) -> bytes:
    """Carga y desencripta un archivo de imagen.
    
    Args:
        relative_path: Ruta relativa al FILES_DIR
        
    Returns:
        bytes: Contenido desencriptado de la imagen
    """
    file_path = Path(settings.FILES_DIR) / relative_path
    
    if not file_path.exists():
        raise FileNotFoundError(f"Image file not found: {relative_path}")
    
    # Leer contenido encriptado
    encrypted_content = file_path.read_bytes()
    
    # Desencriptar
    decrypted_content = decrypt_data(encrypted_content)
    
    return decrypted_content