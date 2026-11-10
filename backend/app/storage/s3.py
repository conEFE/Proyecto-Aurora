"""Almacenamiento en Amazon S3: cifrado en la aplicación (Fernet) y además en el servidor con SSE-KMS."""

from collections.abc import Iterator

from app.storage.base import StorageBackend


class S3EncryptedStorage(StorageBackend):
    def __init__(
        self,
        bucket: str,
        encryption_key: str,
        previous_key: str | None = None,
        prefix: str = "images/",
        kms_key_id: str | None = None,
        region: str | None = None,
        client=None,
    ):
        super().__init__(encryption_key, previous_key)
        if not bucket:
            from app.storage.base import StorageConfigError

            raise StorageConfigError("S3_BUCKET no está configurado")
        if client is None:
            import boto3

            client = boto3.client("s3", region_name=region)
        self.client = client
        self.bucket = bucket
        self.prefix = prefix.strip("/") + "/" if prefix.strip("/") else ""
        self.kms_key_id = kms_key_id

    def _object_key(self, key: str) -> str:
        if ".." in key.split("/") or key.startswith("/"):
            raise ValueError("Ruta de almacenamiento inválida")
        return f"{self.prefix}{key}"

    def write_raw(self, key: str, data: bytes) -> None:
        extra = {"ServerSideEncryption": "aws:kms"}
        if self.kms_key_id:
            extra["SSEKMSKeyId"] = self.kms_key_id
        self.client.put_object(
            Bucket=self.bucket,
            Key=self._object_key(key),
            Body=data,
            ContentType="application/octet-stream",
            **extra,
        )

    def read_raw(self, key: str) -> bytes:
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=self._object_key(key))
        except self.client.exceptions.NoSuchKey as exc:
            raise FileNotFoundError(key) from exc
        return obj["Body"].read()

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=self._object_key(key))

    def iter_keys(self) -> Iterator[str]:
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=self.prefix):
            for item in page.get("Contents", []):
                yield item["Key"][len(self.prefix) :]
