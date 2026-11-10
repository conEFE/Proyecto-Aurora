"""Rota los secretos de backend/.env: SECRET_KEY, ENCRYPTION_KEY (vuelve a cifrar las imágenes) y, opcionalmente,
la contraseña del rol de PostgreSQL de DB_DSN.

Uso (desde backend/, con la API detenida):

    python -m scripts.rotate_secrets --dry-run         # solo verifica: no cambia nada
    python -m scripts.rotate_secrets                   # SECRET_KEY + ENCRYPTION_KEY
    python -m scripts.rotate_secrets --db-password     # además cambia la contraseña del rol de PostgreSQL

Es seguro reanudarlo: mientras dura la rotación, .env guarda la clave anterior en ENCRYPTION_KEY_PREVIOUS y la
API puede leer las imágenes con cualquiera de las dos. Al terminar, la clave anterior se borra de .env.

Los valores nuevos nunca se imprimen. Se deja una copia del .env anterior (.env.antes-de-rotar-FECHA) para
recuperar en caso de error: bórrela cuando confirme que todo funciona.
"""

import argparse
import os
import secrets
import shutil
import sys
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.storage.base import StorageBackend  # noqa: E402

PREVIOUS = "ENCRYPTION_KEY_PREVIOUS"


class RotationError(RuntimeError):
    pass


# --- .env -------------------------------------------------------------------------------------


def read_env(path: Path) -> tuple[list[str], dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    values = {}
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            name, value = stripped.split("=", 1)
            values[name.strip()] = value.strip().strip('"').strip("'")
    return lines, values


def render_env(lines: list[str], updates: dict[str, str | None]) -> str:
    """Reemplaza las variables indicadas conservando el resto del archivo; None elimina la línea."""
    pending = dict(updates)
    out = []
    for line in lines:
        stripped = line.strip()
        name = stripped.split("=", 1)[0].strip() if "=" in stripped and not stripped.startswith("#") else None
        if name in pending:
            value = pending.pop(name)
            if value is not None:
                out.append(f"{name}={value}")
            continue
        out.append(line)
    for name, value in pending.items():
        if value is not None:
            out.append(f"{name}={value}")
    return "\n".join(out) + "\n"


def write_env(path: Path, content: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


# --- almacenamiento ---------------------------------------------------------------------------


def storage_from_env(env: dict[str, str], key: str, previous: str | None, base_dir: Path) -> StorageBackend:
    backend = env.get("STORAGE_BACKEND", "local").lower()
    if backend == "s3":
        from app.storage.s3 import S3EncryptedStorage

        return S3EncryptedStorage(
            bucket=env.get("S3_BUCKET", ""),
            encryption_key=key,
            previous_key=previous,
            prefix=env.get("S3_PREFIX", "images/"),
            kms_key_id=env.get("S3_KMS_KEY_ID") or None,
            region=env.get("AWS_REGION") or None,
        )
    from app.storage.local import LocalEncryptedStorage

    root = Path(env.get("FILES_DIR", "./data/images"))
    if not root.is_absolute():
        root = base_dir / root
    return LocalEncryptedStorage(str(root), key, previous)


def verify_readable(storage: StorageBackend) -> int:
    """Comprueba que todos los archivos se puedan descifrar antes de tocar nada."""
    keys = list(storage.iter_keys())
    unreadable = []
    for key in keys:
        try:
            storage.load(key)
        except InvalidToken:
            unreadable.append(key)
    if unreadable:
        raise RotationError(
            f"{len(unreadable)} archivo(s) no se pueden descifrar con la clave actual (por ejemplo {unreadable[0]}). "
            "No se cambió nada. Revise ENCRYPTION_KEY antes de rotar."
        )
    return len(keys)


# --- PostgreSQL -------------------------------------------------------------------------------


def alter_db_password(dsn: str):
    """Cambia la contraseña del rol de DB_DSN dentro de una transacción. Devuelve (conexión, DSN nuevo).

    La transacción queda abierta: quien llama hace commit cuando .env ya tiene el DSN nuevo.
    """
    import psycopg2
    from psycopg2 import sql
    from sqlalchemy.engine import make_url

    url = make_url(dsn)
    if not url.username:
        raise RotationError("DB_DSN no indica el usuario de PostgreSQL")
    new_password = secrets.token_urlsafe(32)
    new_dsn = url.set(password=new_password).render_as_string(hide_password=False)
    conn = psycopg2.connect(url.set(drivername="postgresql").render_as_string(hide_password=False))
    conn.autocommit = False
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("ALTER ROLE {} WITH PASSWORD {}").format(
                sql.Identifier(url.username), sql.Literal(new_password)
            )
        )
    return conn, new_dsn


def check_db(dsn: str) -> None:
    from sqlalchemy import create_engine, text

    engine = create_engine(dsn)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    finally:
        engine.dispose()


# --- rotación ---------------------------------------------------------------------------------


def rotate(env_path: Path, db_password: bool = False, dry_run: bool = False, log=print) -> dict:
    if not env_path.exists():
        raise RotationError(f"No existe {env_path}")
    base_dir = env_path.resolve().parent
    lines, env = read_env(env_path)

    resuming = bool(env.get(PREVIOUS))
    if resuming:
        new_key, old_key = env["ENCRYPTION_KEY"], env[PREVIOUS]
        log("Se encontró una rotación sin terminar: se reanuda con las claves de .env.")
    else:
        old_key = env.get("ENCRYPTION_KEY", "")
        new_key = Fernet.generate_key().decode()

    total = 0
    if old_key:
        total = verify_readable(storage_from_env(env, new_key if resuming else old_key, old_key, base_dir))
    log(f"Archivos cifrados encontrados: {total}")
    if dry_run:
        log("Simulación: todos los archivos se pueden descifrar. No se cambió nada.")
        return {"files": total, "dry_run": True}

    backup = env_path.with_name(f"{env_path.name}.antes-de-rotar-{datetime.now():%Y%m%d-%H%M%S}")
    shutil.copy2(env_path, backup)
    os.chmod(backup, 0o600)

    # 1) .env con las claves nuevas y la anterior (para descifrar mientras se vuelve a cifrar)
    updates: dict[str, str | None] = {"ENCRYPTION_KEY": new_key}
    if old_key and old_key != new_key:
        updates[PREVIOUS] = old_key
    if not resuming:
        updates["SECRET_KEY"] = secrets.token_urlsafe(48)
    content = render_env(lines, updates)
    write_env(env_path, content)
    lines, env = read_env(env_path)

    # 2) Contraseña de PostgreSQL: el cambio se confirma solo después de guardar el DSN nuevo en .env
    if db_password:
        if not env.get("DB_DSN"):
            raise RotationError("DB_DSN no está definido en .env")
        conn, new_dsn = alter_db_password(env["DB_DSN"])
        try:
            write_env(env_path, render_env(lines, {"DB_DSN": new_dsn}))
            conn.commit()
        except Exception:
            conn.rollback()
            write_env(env_path, render_env(lines, {}))
            raise
        finally:
            conn.close()
        check_db(new_dsn)
        lines, env = read_env(env_path)
        log("Contraseña del rol de PostgreSQL cambiada y verificada.")

    # 3) Volver a cifrar todos los archivos con la clave nueva
    rotated = 0
    if old_key:
        storage = storage_from_env(env, new_key, old_key, base_dir)
        for key in storage.iter_keys():
            storage.rotate(key)
            rotated += 1
        # 4) Verificar que todo se lee solo con la clave nueva
        verify_readable(storage_from_env(env, new_key, None, base_dir))
    log(f"Archivos cifrados de nuevo: {rotated}")

    # 5) Quitar la clave anterior
    write_env(env_path, render_env(lines, {PREVIOUS: None}))
    return {"files": rotated, "backup": str(backup), "db_password": db_password, "resumed": resuming}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rota los secretos de backend/.env")
    parser.add_argument(
        "--env-file", default=str(BACKEND_DIR / ".env"), help="Ruta del .env (por defecto backend/.env)"
    )
    parser.add_argument(
        "--db-password", action="store_true", help="Cambiar también la contraseña del rol de PostgreSQL"
    )
    parser.add_argument("--dry-run", action="store_true", help="Solo verificar, sin cambiar nada")
    args = parser.parse_args(argv)
    try:
        result = rotate(Path(args.env_file), args.db_password, args.dry_run)
    except RotationError as exc:
        print(f"ERROR: {exc}")
        return 1
    if not result.get("dry_run"):
        print()
        print("Rotación completa. Valores nuevos guardados en .env (no se muestran).")
        print(
            "- SECRET_KEY nueva: todas las sesiones abiertas se cerraron; los usuarios deben volver a ingresar."
        )
        print("- ENCRYPTION_KEY nueva: las imágenes quedaron cifradas con ella.")
        if result["db_password"]:
            print("- Contraseña de PostgreSQL nueva (DB_DSN actualizado).")
        print(f"- Copia del .env anterior: {result['backup']}")
        print(
            "  Inicie la API, compruebe que puede ver una imagen y luego BORRE esa copia: contiene los secretos viejos."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
