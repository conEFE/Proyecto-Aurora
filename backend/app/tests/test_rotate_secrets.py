"""Rotación de los secretos expuestos (scripts/rotate_secrets.py)."""

import uuid

import pytest
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import text
from sqlalchemy.engine import make_url

from app.deps import engine
from app.storage.local import LocalEncryptedStorage
from app.tests.conftest import TEST_DSN
from scripts.rotate_secrets import PREVIOUS, RotationError, read_env, render_env, rotate

OLD_SECRET = "demo-clave-corta"  # como la clave expuesta de la v1.0 (menos de 32 caracteres)


def _setup(tmp_path, files=3, dsn="postgresql+psycopg2://x:y@localhost/z"):
    old_key = Fernet.generate_key().decode()
    env = tmp_path / ".env"
    env.write_text(
        "# configuración local\n"
        f"DB_DSN={dsn}\n"
        f"SECRET_KEY={OLD_SECRET}\n"
        f"ENCRYPTION_KEY={old_key}\n"
        "FILES_DIR=./data/images\n"
        "ALLOWED_ORIGINS=http://localhost:5173\n",
        encoding="utf-8",
    )
    storage = LocalEncryptedStorage(str(tmp_path / "data" / "images"), old_key)
    contents = {f"case_{i}/{uuid.uuid4().hex}.png.enc": f"imagen-{i}".encode() for i in range(files)}
    for key, data in contents.items():
        storage.save(key, data)
    return env, old_key, contents


def _quiet(*_):
    pass


def test_render_env_preserves_comments_and_order():
    lines = ["# comentario", "A=1", "B=2", "", "C=3"]
    out = render_env(lines, {"B": "nuevo", "C": None, "D": "4"})
    assert out == "# comentario\nA=1\nB=nuevo\n\nD=4\n"


def test_rotation_reencrypts_files_and_replaces_secrets(tmp_path):
    env_path, old_key, contents = _setup(tmp_path)
    result = rotate(env_path, log=_quiet)
    assert result["files"] == 3

    _, env = read_env(env_path)
    assert env["SECRET_KEY"] != OLD_SECRET and len(env["SECRET_KEY"]) >= 32
    assert env["ENCRYPTION_KEY"] != old_key
    assert PREVIOUS not in env
    assert env["ALLOWED_ORIGINS"] == "http://localhost:5173"  # el resto no se toca
    assert env_path.read_text().startswith("# configuración local\n")

    root = str(tmp_path / "data" / "images")
    new_storage = LocalEncryptedStorage(root, env["ENCRYPTION_KEY"])
    old_storage = LocalEncryptedStorage(root, old_key)
    for key, data in contents.items():
        assert new_storage.load(key) == data
        with pytest.raises(InvalidToken):
            old_storage.load(key)

    # Copia de respaldo con los valores anteriores, solo legible por el dueño
    backups = list(tmp_path.glob(".env.antes-de-rotar-*"))
    assert len(backups) == 1 and OLD_SECRET in backups[0].read_text()
    assert oct(backups[0].stat().st_mode)[-3:] == "600"


def test_dry_run_changes_nothing(tmp_path):
    env_path, _, contents = _setup(tmp_path)
    before = env_path.read_text()
    result = rotate(env_path, dry_run=True, log=_quiet)
    assert result == {"files": 3, "dry_run": True}
    assert env_path.read_text() == before
    assert not list(tmp_path.glob(".env.antes-de-rotar-*"))


def test_unreadable_file_aborts_before_changing(tmp_path):
    env_path, _, _ = _setup(tmp_path)
    other = LocalEncryptedStorage(str(tmp_path / "data" / "images"), Fernet.generate_key().decode())
    other.save("case_x/ajeno.png.enc", b"otra clave")
    before = env_path.read_text()
    with pytest.raises(RotationError, match="no se pueden descifrar"):
        rotate(env_path, log=_quiet)
    assert env_path.read_text() == before


def test_interrupted_rotation_can_resume(tmp_path):
    """Si se corta a la mitad, .env tiene ambas claves y la segunda ejecución termina el trabajo."""
    env_path, old_key, contents = _setup(tmp_path, files=4)
    new_key = Fernet.generate_key().decode()
    lines, _ = read_env(env_path)
    env_path.write_text(render_env(lines, {"ENCRYPTION_KEY": new_key, PREVIOUS: old_key}))
    # La mitad de los archivos ya se volvió a cifrar
    half = LocalEncryptedStorage(str(tmp_path / "data" / "images"), new_key, old_key)
    for key in list(contents)[:2]:
        half.rotate(key)
    # Mientras tanto, la API lee todo con ambas claves
    assert all(half.load(k) == v for k, v in contents.items())

    result = rotate(env_path, log=_quiet)
    assert result["resumed"] is True
    _, env = read_env(env_path)
    assert env["ENCRYPTION_KEY"] == new_key and PREVIOUS not in env
    final = LocalEncryptedStorage(str(tmp_path / "data" / "images"), new_key)
    assert all(final.load(k) == v for k, v in contents.items())


def test_rotation_without_previous_key_and_no_files(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("SECRET_KEY=corta\nENCRYPTION_KEY=\n")
    assert rotate(env_path, log=_quiet)["files"] == 0
    _, env = read_env(env_path)
    assert len(env["ENCRYPTION_KEY"]) == 44 and len(env["SECRET_KEY"]) >= 32


def test_rotation_changes_postgres_password(tmp_path):
    role = f"aurora_rot_{uuid.uuid4().hex[:6]}"
    with engine.begin() as conn:
        conn.execute(text(f"CREATE ROLE {role} LOGIN PASSWORD 'clave-vieja-expuesta'"))
        conn.execute(text(f'GRANT CONNECT ON DATABASE "{make_url(TEST_DSN).database}" TO {role}'))
    try:
        dsn = make_url(TEST_DSN).set(username=role, password="clave-vieja-expuesta")
        env_path, _, _ = _setup(tmp_path, files=1, dsn=dsn.render_as_string(hide_password=False))
        with engine.connect() as conn:
            before = conn.execute(
                text("SELECT rolpassword FROM pg_authid WHERE rolname = :r"), {"r": role}
            ).scalar()

        result = rotate(env_path, db_password=True, log=_quiet)
        assert result["db_password"] is True

        _, env = read_env(env_path)
        new_url = make_url(env["DB_DSN"])
        assert new_url.username == role and new_url.password != "clave-vieja-expuesta"
        assert len(new_url.password) >= 32
        with engine.connect() as conn:
            after = conn.execute(
                text("SELECT rolpassword FROM pg_authid WHERE rolname = :r"), {"r": role}
            ).scalar()
        assert after != before
    finally:
        with engine.begin() as conn:
            conn.execute(text(f'REVOKE CONNECT ON DATABASE "{make_url(TEST_DSN).database}" FROM {role}'))
            conn.execute(text(f"DROP ROLE IF EXISTS {role}"))


def test_missing_env_file(tmp_path):
    with pytest.raises(RotationError, match="No existe"):
        rotate(tmp_path / "no-existe.env", log=_quiet)
