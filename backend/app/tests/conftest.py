"""Fixtures de pruebas.

Usa una BD PostgreSQL aislada: `TEST_DB_DSN` si está definida; si no, levanta un
PostgreSQL embebido con `pgserver`. El esquema se crea con Alembic (no `create_all`).
"""

import os
import tempfile
import uuid
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_TMP = Path(tempfile.gettempdir())


def _resolve_test_dsn() -> str:
    dsn = os.getenv("TEST_DB_DSN")
    if dsn:
        return dsn
    import pgserver

    server = pgserver.get_server(str(_TMP / "aurora_pg_test"), cleanup_mode=None)
    db_name = f"aurora_test_{uuid.uuid4().hex[:8]}"
    server.psql(f'CREATE DATABASE "{db_name}";')
    return server.get_uri(db_name).replace("postgresql://", "postgresql+psycopg2://", 1)


# Configurar el entorno ANTES de importar la app
TEST_DSN = _resolve_test_dsn()
os.environ["DB_DSN"] = TEST_DSN
os.environ["SECRET_KEY"] = "clave-solo-para-tests"
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
os.environ["FILES_DIR"] = str(_TMP / f"aurora_files_{uuid.uuid4().hex[:8]}")
os.environ["INFERENCE_PROVIDER"] = "simulated"
os.environ["BCRYPT_ROUNDS"] = "4"

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.auth.security import hash_password  # noqa: E402
from app.db.models.user import User, UserRole  # noqa: E402
from app.deps import SessionLocal, engine  # noqa: E402


def alembic_config() -> Config:
    cfg = Config(str(_BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_DIR / "alembic"))
    cfg.attributes["db_dsn"] = TEST_DSN
    return cfg


@pytest.fixture(scope="session", autouse=True)
def _schema():
    command.upgrade(alembic_config(), "head")
    yield
    engine.dispose()


def truncate_all():
    with engine.begin() as conn:
        tables = (
            conn.execute(
                text(
                    "SELECT tablename FROM pg_tables WHERE schemaname='public' "
                    "AND tablename <> 'alembic_version'"
                )
            )
            .scalars()
            .all()
        )
        if tables:
            conn.execute(text(f"TRUNCATE {', '.join(tables)} RESTART IDENTITY CASCADE"))


@pytest.fixture(autouse=True)
def _clean_db(_schema):
    truncate_all()
    from app.services import seed_service

    if hasattr(seed_service, "ensure_reference_data"):
        with SessionLocal() as session:
            seed_service.ensure_reference_data(session)
    yield


@pytest.fixture
def db():
    with SessionLocal() as session:
        yield session


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


PASSWORD = "Clave-Prueba-123"


def make_user(db, role: UserRole, rut: str, email: str | None = None, **extra) -> User:
    fields = dict(
        rut=rut,
        email=email or f"{rut}@aurora.test",
        password_hash=hash_password(PASSWORD),
        role=role,
    )
    if hasattr(User, "full_name"):
        fields["full_name"] = f"Usuario {role.value.title()}"
    fields.update(extra)
    user = User(**fields)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(client, rut: str, password: str = PASSWORD) -> str:
    r = client.post("/auth/login", json={"rut": rut, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def users(db):
    """Un usuario por rol disponible."""
    created = {
        "MEDICO": make_user(db, UserRole.MEDICO, "11111111-1"),
        "ADMIN": make_user(db, UserRole.ADMIN, "22222222-2"),
    }
    if "ADMINISTRATIVO" in UserRole.__members__:
        created["ADMINISTRATIVO"] = make_user(db, UserRole["ADMINISTRATIVO"], "33333333-3")
    return created


@pytest.fixture
def tokens(client, users):
    return {role: login(client, u.rut) for role, u in users.items()}
