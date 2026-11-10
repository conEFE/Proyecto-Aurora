"""Almacenamiento en disco local, cifrado en la aplicación."""

import os
from collections.abc import Iterator
from pathlib import Path

from app.storage.base import StorageBackend, StorageConfigError, derive_fernet_key  # noqa: F401 (reexport)


class LocalEncryptedStorage(StorageBackend):
    def __init__(self, root: str, encryption_key: str, previous_key: str | None = None):
        super().__init__(encryption_key, previous_key)
        self.root = Path(root)

    def _path(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if self.root.resolve() not in path.parents:
            raise ValueError("Ruta de almacenamiento inválida")
        return path

    def write_raw(self, key: str, data: bytes) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Escritura atómica: nunca queda un archivo a medio escribir
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, path)

    def read_raw(self, key: str) -> bytes:
        path = self._path(key)
        if not path.exists():
            raise FileNotFoundError(key)
        return path.read_bytes()

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)

    def iter_keys(self) -> Iterator[str]:
        if not self.root.exists():
            return
        for path in sorted(self.root.rglob("*")):
            if path.is_file() and not path.name.endswith(".tmp"):
                yield path.relative_to(self.root).as_posix()
