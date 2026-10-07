from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.auth.security import create_access_token, verify_password
from app.db.models.user import User
from app.services.audit_service import audit
from app.utils.rut import normalize_rut


class AuthError(Exception):
    pass


def authenticate(db: Session, rut: str, password: str, ip: str | None = None) -> User:
    user = db.query(User).filter(User.rut == normalize_rut(rut)).first()
    if user is None or not verify_password(password, user.password_hash):
        # No se guarda el RUT intentado (dato personal); solo el id si el usuario existe
        audit(db, user, "LOGIN_FAIL", "user", user.id if user else None, {"reason": "credenciales"}, ip)
        raise AuthError("RUT o contraseña incorrectos")
    if not user.is_active:
        audit(db, user, "LOGIN_FAIL", "user", user.id, {"reason": "inactivo"}, ip)
        raise AuthError("Usuario desactivado. Contacte al administrador")
    user.last_login_at = datetime.now(timezone.utc)
    audit(db, user, "LOGIN_OK", "user", user.id, None, ip, commit=False)
    db.commit()
    return user


def issue_token(user: User) -> dict:
    return {
        "access_token": create_access_token(user.id, user.role.value),
        "token_type": "bearer",
        "role": user.role.value,
        "full_name": user.full_name,
    }
