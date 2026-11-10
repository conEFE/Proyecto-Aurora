from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.auth.security import create_access_token, hash_password, password_stamp, verify_password
from app.config import settings
from app.db.models.user import User
from app.services.audit_service import audit
from app.services.errors import DomainError, ValidationError
from app.services.password_policy import ensure_valid_password
from app.utils.rate_limit import login_limiter
from app.utils.rut import normalize_rut

# Hash de referencia para igualar el tiempo de respuesta cuando el RUT no existe
_DUMMY_HASH = hash_password("aurora-dummy-password-0")


class AuthError(Exception):
    pass


class AccountLockedError(DomainError):
    status_code = 423


class RateLimitedError(DomainError):
    status_code = 429

    def __init__(self, message: str, retry_after: int):
        super().__init__(message)
        self.retry_after = retry_after


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _locked_message(until: datetime) -> str:
    minutes = max(1, int((until - _now()).total_seconds() // 60) + 1)
    return (
        "Cuenta bloqueada temporalmente por intentos fallidos. "
        f"Intente nuevamente en {minutes} minuto{'s' if minutes != 1 else ''} o contacte al administrador"
    )


def _check_ip_limit(db: Session, ip: str | None) -> None:
    allowed, retry_after, first = login_limiter.hit(
        f"login:{ip or 'desconocida'}", settings.LOGIN_RATE_LIMIT_PER_MINUTE
    )
    if allowed:
        return
    if first:  # se audita una vez por ventana, no cada intento rechazado
        audit(db, None, "LOGIN_FAIL", "user", None, {"reason": "limite_ip"}, ip)
    raise RateLimitedError(
        f"Demasiados intentos de inicio de sesión. Espere {retry_after} segundos e intente nuevamente",
        retry_after,
    )


def authenticate(db: Session, rut: str, password: str, ip: str | None = None) -> User:
    _check_ip_limit(db, ip)
    user = db.query(User).filter(User.rut == normalize_rut(rut)).with_for_update().first()
    if user is None:
        verify_password(password, _DUMMY_HASH)
        # No se guarda el RUT intentado (dato personal)
        audit(db, None, "LOGIN_FAIL", "user", None, {"reason": "credenciales"}, ip)
        raise AuthError("RUT o contraseña incorrectos")

    if user.locked_until is not None and user.locked_until > _now():
        # Mientras dure el bloqueo no se evalúa la contraseña (no sirve para adivinarla)
        until = user.locked_until
        audit(db, user, "LOGIN_FAIL", "user", user.id, {"reason": "bloqueado"}, ip)
        raise AccountLockedError(_locked_message(until))

    if not verify_password(password, user.password_hash):
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= settings.LOGIN_MAX_FAILED_ATTEMPTS:
            until = _now() + timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
            user.locked_until = until
            user.failed_login_attempts = 0
            detail = {"reason": "bloqueo", "locked_minutes": settings.LOGIN_LOCKOUT_MINUTES}
            audit(db, user, "LOGIN_FAIL", "user", user.id, detail, ip)
            raise AccountLockedError(_locked_message(until))
        audit(db, user, "LOGIN_FAIL", "user", user.id, {"reason": "credenciales"}, ip)
        raise AuthError("RUT o contraseña incorrectos")

    if not user.is_active:
        audit(db, user, "LOGIN_FAIL", "user", user.id, {"reason": "inactivo"}, ip)
        raise AuthError("Usuario desactivado. Contacte al administrador")

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = _now()
    audit(db, user, "LOGIN_OK", "user", user.id, None, ip, commit=False)
    db.commit()
    return user


def issue_token(user: User) -> dict:
    return {
        "access_token": create_access_token(
            user.id, user.role.value, pwd_stamp=password_stamp(user.password_changed_at)
        ),
        "token_type": "bearer",
        "role": user.role.value,
        "full_name": user.full_name,
        "must_change_password": bool(user.must_change_password),
    }


def change_password(db: Session, user: User, current: str, new: str, ip: str | None = None) -> dict:
    allowed, retry_after, _ = login_limiter.hit(f"chpw:{user.id}", settings.LOGIN_MAX_FAILED_ATTEMPTS)
    if not allowed:
        raise RateLimitedError(
            f"Demasiados intentos de cambio de contraseña. Espere {retry_after} segundos", retry_after
        )
    if not verify_password(current, user.password_hash):
        audit(db, user, "PASSWORD_CHANGE_FAIL", "user", user.id, {"reason": "actual_incorrecta"}, ip)
        raise ValidationError("La contraseña actual no es correcta")
    try:
        ensure_valid_password(new, user.rut, user.password_hash)
    except ValidationError:
        audit(db, user, "PASSWORD_CHANGE_FAIL", "user", user.id, {"reason": "politica"}, ip)
        raise
    user.password_hash = hash_password(new)
    user.password_changed_at = _now()
    forced = bool(user.must_change_password)
    user.must_change_password = False
    audit(db, user, "PASSWORD_CHANGE", "user", user.id, {"forced": forced}, ip, commit=False)
    db.commit()
    db.refresh(user)
    # Los tokens anteriores quedan revocados; se entrega uno nuevo para seguir en la sesión
    return issue_token(user)
