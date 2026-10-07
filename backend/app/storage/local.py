"""Almacenamiento local cifrado con Fernet (AES-128-CBC + HMAC-SHA256)."""

import base64
from functools import lru_cache
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import settings
from app.storage.base import StorageBackend


class StorageConfigError(RuntimeError):
    pass


def derive_fernet_key(raw: str) -> bytes:
    """Deriva la clave Fernet desde ENCRYPTION_KEY.

    Se conserva la derivación de la v1.0 para poder leer los archivos ya cifrados:
    - claves de menos de 32 caracteres: PBKDF2-SHA256;
    - claves de 32 o más caracteres: base64 de los primeros 32 bytes.
    """
    key = raw.encode()
    if len(key) < 32:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"medical_images_salt", iterations=100000)
        return base64.urlsafe_b64encode(kdf.derive(key))
    return base64.urlsafe_b64encode(key[:32])


class LocalEncryptedStorage(StorageBackend):
    def __init__(self, root: str, encryption_key: str):
        if not encryption_key:
            # La v1.0 generaba una clave aleatoria en cada arranque y los archivos quedaban ilegibles al reiniciar.
            raise StorageConfigError("ENCRYPTION_KEY no está configurada; no se pueden guardar imágenes")
        self.root = Path(root)
        self._fernet = Fernet(derive_fernet_key(encryption_key))

    def _path(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if self.root.resolve() not in path.parents:
            raise ValueError("Ruta de almacenamiento inválida")
        return path

    def save(self, key: str, data: bytes) -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self._fernet.encrypt(data))
        return key

    def load(self, key: str) -> bytes:
        path = self._path(key)
        if not path.exists():
            raise FileNotFoundError(key)
        return self._fernet.decrypt(path.read_bytes())

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)


@lru_cache
def get_storage() -> StorageBackend:
    return LocalEncryptedStorage(settings.FILES_DIR, settings.ENCRYPTION_KEY)
