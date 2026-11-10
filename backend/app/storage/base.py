"""Interfaz de almacenamiento de archivos (D9): disco local o S3, siempre cifrado en la aplicación."""

import base64
from abc import ABC, abstractmethod
from collections.abc import Iterator

from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


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


def build_cipher(encryption_key: str, previous_key: str | None = None) -> MultiFernet:
    """Cifra con la clave actual y descifra con la actual o la anterior (para rotar sin cortar el servicio)."""
    if not encryption_key:
        # La v1.0 generaba una clave aleatoria en cada arranque y los archivos quedaban ilegibles al reiniciar.
        raise StorageConfigError("ENCRYPTION_KEY no está configurada; no se pueden guardar imágenes")
    keys = [Fernet(derive_fernet_key(encryption_key))]
    if previous_key:
        keys.append(Fernet(derive_fernet_key(previous_key)))
    return MultiFernet(keys)


class StorageBackend(ABC):
    """Guarda archivos cifrados con Fernet (AES-128-CBC + HMAC-SHA256) antes de que salgan de la aplicación."""

    def __init__(self, encryption_key: str, previous_key: str | None = None):
        self._cipher = build_cipher(encryption_key, previous_key)

    # --- operaciones sobre el contenido cifrado (las implementa cada backend) ---
    @abstractmethod
    def write_raw(self, key: str, data: bytes) -> None:
        """Escribe bytes ya cifrados."""

    @abstractmethod
    def read_raw(self, key: str) -> bytes:
        """Lee los bytes cifrados. Lanza FileNotFoundError si no existe."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Elimina el archivo si existe."""

    @abstractmethod
    def iter_keys(self) -> Iterator[str]:
        """Recorre las claves de todos los archivos guardados."""

    # --- operaciones con el contenido original ---
    def save(self, key: str, data: bytes) -> str:
        """Cifra y guarda `data` bajo `key`; devuelve la clave definitiva."""
        self.write_raw(key, self._cipher.encrypt(data))
        return key

    def load(self, key: str) -> bytes:
        """Devuelve el contenido original (descifrado)."""
        return self._cipher.decrypt(self.read_raw(key))

    def rotate(self, key: str) -> None:
        """Vuelve a cifrar un archivo con la clave actual (lo descifra con la actual o la anterior)."""
        self.write_raw(key, self._cipher.rotate(self.read_raw(key)))
