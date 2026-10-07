"""Obtiene el usuario autenticado a partir del JWT, siempre consultando la BD."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.security import InvalidTokenError, decode_access_token
from app.db.models.user import User
from app.deps import get_db

_bearer = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Sesión inválida o expirada",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _UNAUTHORIZED
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (InvalidTokenError, ValueError, TypeError):
        raise _UNAUTHORIZED

    user = db.get(User, user_id)
    if user is None or not getattr(user, "is_active", True):
        raise _UNAUTHORIZED
    return user
