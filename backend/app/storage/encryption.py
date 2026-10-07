import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import settings


def get_encryption_key() -> bytes:
    """Obtiene o genera la clave de encriptación"""
    if settings.ENCRYPTION_KEY:
        # Si hay una clave en el .env, usarla
        key = settings.ENCRYPTION_KEY.encode()
        # Asegurar que tenga 32 bytes (Fernet requiere 32 bytes base64)
        if len(key) < 32:
            # Si es muy corta, derivarla con PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"medical_images_salt",  # En producción, usar salt único por instalación
                iterations=100000,
                backend=default_backend(),
            )
            key = base64.urlsafe_b64encode(kdf.derive(key))
        else:
            # Si es suficientemente larga, convertir a base64
            key = base64.urlsafe_b64encode(key[:32])
        return key
    else:
        # Generar una clave nueva (solo para desarrollo)
        # En producción, siempre debe estar en .env
        key = Fernet.generate_key()
        print("WARNING: Encryption key generated automatically. Set ENCRYPTION_KEY in .env for production!")
        return key


# Inicializar Fernet con la clave
_fernet = None


def get_fernet() -> Fernet:
    """Obtiene la instancia de Fernet (singleton)"""
    global _fernet
    if _fernet is None:
        key = get_encryption_key()
        _fernet = Fernet(key)
    return _fernet


def encrypt_data(data: bytes) -> bytes:
    """Encripta datos binarios"""
    fernet = get_fernet()
    return fernet.encrypt(data)


def decrypt_data(encrypted_data: bytes) -> bytes:
    """Desencripta datos binarios"""
    fernet = get_fernet()
    return fernet.decrypt(encrypted_data)
