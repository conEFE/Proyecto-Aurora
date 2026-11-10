"""Obtiene el usuario autenticado a partir del JWT, siempre consultando la BD."""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.security import InvalidTokenError, decode_access_token, password_stamp
from app.db.models.user import User
from app.deps import get_db

_bearer = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Sesión inválida o expirada",
    headers={"WWW-Authenticate": "Bearer"},
)

PASSWORD_CHANGE_REQUIRED = "Debe cambiar su contraseña antes de continuar"


def get_authenticated_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Usuario con token válido, aunque tenga pendiente el cambio obligatorio de contraseña."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _UNAUTHORIZED
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
        token_stamp = int(payload.get("pwd", 0))
    except (InvalidTokenError, ValueError, TypeError):
        raise _UNAUTHORIZED

    user = db.get(User, user_id)
    if user is None or not getattr(user, "is_active", True):
        raise _UNAUTHORIZED
    # Un cambio o restablecimiento de contraseña revoca los tokens emitidos antes
    if token_stamp != password_stamp(user.password_changed_at):
        raise _UNAUTHORIZED
    request.state.user_id = user.id  # para el registro de errores
    return user


def get_current_user(user: User = Depends(get_authenticated_user)) -> User:
    """Usuario autenticado y habilitado: con el cambio obligatorio de contraseña pendiente solo puede cambiarla."""
    if user.must_change_password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=PASSWORD_CHANGE_REQUIRED)
    return user
