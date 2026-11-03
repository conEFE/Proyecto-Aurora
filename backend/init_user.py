"""Crea el primer usuario ADMIN de la plataforma.

Las credenciales se leen SIEMPRE de variables de entorno (o de backend/.env), nunca del código:

    AURORA_ADMIN_RUT=12345678-5
    AURORA_ADMIN_EMAIL=admin@hospital.cl
    AURORA_ADMIN_NAME="Administrador Aurora"
    AURORA_ADMIN_PASSWORD=...        # mínimo 8 caracteres

Uso (desde backend/, con las migraciones aplicadas):
    python init_user.py
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), encoding="utf-8")

from app.auth.security import hash_password  # noqa: E402
from app.db.models.user import User, UserRole  # noqa: E402
from app.deps import SessionLocal  # noqa: E402
from app.utils.rut import validate_rut  # noqa: E402

REQUIRED = ("AURORA_ADMIN_RUT", "AURORA_ADMIN_EMAIL", "AURORA_ADMIN_NAME", "AURORA_ADMIN_PASSWORD")


def main() -> int:
    missing = [name for name in REQUIRED if not os.getenv(name)]
    if missing:
        print(f"Faltan variables de entorno: {', '.join(missing)}")
        return 1
    try:
        rut = validate_rut(os.environ["AURORA_ADMIN_RUT"])
    except ValueError as exc:
        print(exc)
        return 1
    password = os.environ["AURORA_ADMIN_PASSWORD"]
    if len(password) < 8:
        print("La contraseña debe tener al menos 8 caracteres")
        return 1

    with SessionLocal() as db:
        if db.query(User).filter(User.role == UserRole.ADMIN).first():
            print("Ya existe un usuario ADMIN; no se crea otro.")
            return 0
        if db.query(User).filter(User.rut == rut).first():
            print("Ya existe un usuario con ese RUT.")
            return 1
        db.add(
            User(
                rut=rut,
                email=os.environ["AURORA_ADMIN_EMAIL"].strip(),
                full_name=os.environ["AURORA_ADMIN_NAME"].strip(),
                password_hash=hash_password(password),
                role=UserRole.ADMIN,
                is_active=True,
            )
        )
        db.commit()
    print(f"Usuario ADMIN creado (RUT {rut}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
