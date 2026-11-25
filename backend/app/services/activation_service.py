"""Activación de cuentas por email: token de un solo uso que verifica el email y define la contraseña."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.config import settings
from app.db.models.email_token import PURPOSE_ACTIVATION, EmailToken
from app.db.models.user import User
from app.services import email_service
from app.services.audit_service import audit
from app.services.errors import NotFoundError, ValidationError
from app.services.password_policy import ensure_valid_password

INVALID_LINK = "El link de activación no es válido o ya fue usado. Pida al administrador que lo reenvíe"
EXPIRED_LINK = "El link de activación venció. Pida al administrador que lo reenvíe"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def issue_activation_token(db: Session, user: User) -> str:
    """Crea un token nuevo e invalida los anteriores sin usar. Devuelve el token en claro (solo para el email)."""
    now = _now()
    db.query(EmailToken).filter(
        EmailToken.user_id == user.id,
        EmailToken.purpose == PURPOSE_ACTIVATION,
        EmailToken.used_at.is_(None),
    ).update({EmailToken.used_at: now}, synchronize_session=False)
    token = secrets.token_urlsafe(32)
    db.add(
        EmailToken(
            user_id=user.id,
            purpose=PURPOSE_ACTIVATION,
            token_hash=_hash(token),
            expires_at=now + timedelta(hours=settings.ACTIVATION_TOKEN_HOURS),
        )
    )
    db.flush()
    return token


def send_activation(user_email: str, first_name: str, token: str) -> bool:
    return email_service.send(email_service.activation_email(user_email, first_name, token))


def _valid_token(db: Session, token: str) -> EmailToken:
    row = (
        db.query(EmailToken)
        .filter(EmailToken.token_hash == _hash(token or ""), EmailToken.purpose == PURPOSE_ACTIVATION)
        .with_for_update()
        .first()
    )
    if row is None or row.used_at is not None:
        raise ValidationError(INVALID_LINK)
    if _aware(row.expires_at) < _now():
        raise ValidationError(EXPIRED_LINK)
    return row


def preview(db: Session, token: str) -> User:
    """Datos mínimos para la pantalla de activación (nombre y email), sin consumir el token."""
    row = _valid_token(db, token)
    user = db.get(User, row.user_id)
    if user is None or not user.is_active:
        raise ValidationError(INVALID_LINK)
    db.rollback()  # libera el bloqueo de la fila
    return user


def activate(db: Session, token: str, password: str, ip: str | None = None) -> User:
    row = _valid_token(db, token)
    user = db.get(User, row.user_id)
    if user is None or not user.is_active:
        raise ValidationError(INVALID_LINK)
    ensure_valid_password(password, user.rut)
    now = _now()
    user.password_hash = hash_password(password)
    user.password_changed_at = now
    user.must_change_password = False
    user.failed_login_attempts = 0
    user.locked_until = None
    user.email_verified_at = now
    row.used_at = now
    audit(db, user, "ACCOUNT_ACTIVATE", "user", user.id, None, ip, commit=False)
    db.commit()
    db.refresh(user)
    return user


def resend(db: Session, user_id: int, actor: User, ip: str | None = None) -> tuple[User, str]:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("Usuario no encontrado")
    if not user.is_active:
        raise ValidationError("El usuario está desactivado: actívelo antes de reenviar el link")
    if user.email_verified_at is not None:
        raise ValidationError("El usuario ya verificó su email")
    token = issue_activation_token(db, user)
    audit(db, actor, "ACTIVATION_RESEND", "user", user.id, None, ip, commit=False)
    db.commit()
    db.refresh(user)
    return user, token
