"""Elige el backend de almacenamiento según STORAGE_BACKEND (local o s3)."""

from functools import lru_cache

from app.config import settings
from app.storage.base import StorageBackend, StorageConfigError


def build_storage(config=settings) -> StorageBackend:
    backend = (config.STORAGE_BACKEND or "local").lower()
    previous = config.ENCRYPTION_KEY_PREVIOUS or None
    if backend == "local":
        from app.storage.local import LocalEncryptedStorage

        return LocalEncryptedStorage(config.FILES_DIR, config.ENCRYPTION_KEY, previous)
    if backend == "s3":
        from app.storage.s3 import S3EncryptedStorage

        return S3EncryptedStorage(
            bucket=config.S3_BUCKET,
            encryption_key=config.ENCRYPTION_KEY,
            previous_key=previous,
            prefix=config.S3_PREFIX,
            kms_key_id=config.S3_KMS_KEY_ID or None,
            region=config.AWS_REGION or None,
        )
    raise StorageConfigError(f"STORAGE_BACKEND desconocido: {backend} (use local o s3)")


@lru_cache
def get_storage() -> StorageBackend:
    return build_storage()
