"""S3EncryptedStorage con S3 y KMS simulados (moto): cifrado en la aplicación + SSE-KMS en el servidor."""

import boto3
import pytest
from cryptography.fernet import Fernet, InvalidToken
from moto import mock_aws

from app.config import Settings
from app.storage.base import StorageConfigError
from app.storage.factory import build_storage
from app.storage.s3 import S3EncryptedStorage

REGION = "sa-east-1"
BUCKET = "aurora-test-images"


@pytest.fixture
def aws(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", REGION)
    with mock_aws():
        s3 = boto3.client("s3", region_name=REGION)
        s3.create_bucket(Bucket=BUCKET, CreateBucketConfiguration={"LocationConstraint": REGION})
        kms_key = boto3.client("kms", region_name=REGION).create_key()["KeyMetadata"]["KeyId"]
        yield s3, kms_key


def test_save_and_load_with_sse_kms(aws):
    s3, kms_key = aws
    key = Fernet.generate_key().decode()
    storage = S3EncryptedStorage(BUCKET, key, kms_key_id=kms_key, region=REGION, client=s3)
    storage.save("case_1/a.png.enc", b"imagen de prueba")

    obj = s3.get_object(Bucket=BUCKET, Key="images/case_1/a.png.enc")
    assert obj["ServerSideEncryption"] == "aws:kms"
    assert kms_key in obj["SSEKMSKeyId"]
    # En S3 nunca queda el contenido en claro: está cifrado también por la aplicación
    assert b"imagen de prueba" not in obj["Body"].read()
    assert storage.load("case_1/a.png.enc") == b"imagen de prueba"
    assert list(storage.iter_keys()) == ["case_1/a.png.enc"]

    storage.delete("case_1/a.png.enc")
    with pytest.raises(FileNotFoundError):
        storage.load("case_1/a.png.enc")


def test_rotate_in_s3(aws):
    s3, _ = aws
    old, new = Fernet.generate_key().decode(), Fernet.generate_key().decode()
    S3EncryptedStorage(BUCKET, old, client=s3).save("k.enc", b"datos")
    rotating = S3EncryptedStorage(BUCKET, new, previous_key=old, client=s3)
    rotating.rotate("k.enc")
    assert S3EncryptedStorage(BUCKET, new, client=s3).load("k.enc") == b"datos"
    with pytest.raises(InvalidToken):
        S3EncryptedStorage(BUCKET, old, client=s3).load("k.enc")


def test_s3_rejects_path_traversal(aws):
    s3, _ = aws
    storage = S3EncryptedStorage(BUCKET, Fernet.generate_key().decode(), client=s3)
    with pytest.raises(ValueError):
        storage.save("../fuera.bin", b"x")


def test_factory_selects_backend(aws, tmp_path):
    base = {
        "DB_DSN": "postgresql://x",
        "SECRET_KEY": "x" * 40,
        "ENCRYPTION_KEY": Fernet.generate_key().decode(),
    }
    local = build_storage(Settings(**base, FILES_DIR=str(tmp_path)))
    assert type(local).__name__ == "LocalEncryptedStorage"
    s3 = build_storage(Settings(**base, STORAGE_BACKEND="s3", S3_BUCKET=BUCKET, AWS_REGION=REGION))
    assert isinstance(s3, S3EncryptedStorage)
    with pytest.raises(StorageConfigError):
        build_storage(Settings(**base, STORAGE_BACKEND="s3", S3_BUCKET=""))
    with pytest.raises(StorageConfigError):
        build_storage(Settings(**base, STORAGE_BACKEND="ftp"))
