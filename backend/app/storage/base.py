"""Interfaz de almacenamiento de archivos (D9). Hoy: disco local cifrado; en S7: S3 con SSE-KMS."""

from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes) -> str:
        """Guarda `data` bajo `key` y devuelve la clave definitiva."""

    @abstractmethod
    def load(self, key: str) -> bytes:
        """Devuelve el contenido original (descifrado). Lanza FileNotFoundError si no existe."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Elimina el archivo si existe."""
