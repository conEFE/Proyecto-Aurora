from sqlalchemy.orm import Session

from app.auth.security import create_access_token, verify_password
from app.db.models.user import User


class AuthError(Exception):
    pass


def authenticate(db: Session, rut: str, password: str) -> User:
    user = db.query(User).filter(User.rut == rut.strip()).first()
    if user is None or not verify_password(password, user.password_hash):
        raise AuthError("RUT o contraseña incorrectos")
    if not getattr(user, "is_active", True):
        raise AuthError("Usuario desactivado")
    return user


def issue_token(user: User) -> dict:
    return {
        "access_token": create_access_token(user.id, user.role.value),
        "token_type": "bearer",
        "role": user.role.value,
        "full_name": getattr(user, "full_name", None) or user.email,
    }
