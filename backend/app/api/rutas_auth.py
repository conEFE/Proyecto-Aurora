from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.auth.bearer import get_authenticated_user, get_current_user
from app.config import settings
from app.db.models.user import User
from app.deps import get_db
from app.schemas.users import ActivateRequest, ActivationPreview
from app.services import activation_service, auth_service
from app.services.audit_service import client_ip
from app.services.auth_service import RateLimitedError
from app.utils.rate_limit import login_limiter

router = APIRouter()


class LoginRequest(BaseModel):
    rut: str = Field(max_length=20)
    password: str = Field(max_length=200)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str | None = None
    must_change_password: bool = False


class MeResponse(BaseModel):
    id: int
    rut: str
    email: str
    full_name: str
    first_name: str = ""
    last_name: str = ""
    specialty: str | None = None
    email_verified: bool = False
    role: str
    must_change_password: bool = False
    created_at: datetime | None = None
    last_login_at: datetime | None = None
    password_changed_at: datetime | None = None


class ChangeEmailRequest(BaseModel):
    email: EmailStr
    current_password: str = Field(min_length=1, max_length=200)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=1, max_length=200)


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Login con RUT y contraseña. Devuelve un JWT firmado (HS256).

    Límite de intentos por IP (429) y bloqueo temporal de la cuenta tras varios fallos seguidos (423).
    """
    try:
        user = auth_service.authenticate(db, credentials.rut, credentials.password, client_ip(request))
    except auth_service.AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return auth_service.issue_token(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(current_user: User = Depends(get_current_user)):
    """Renueva el token de una sesión válida (la interfaz lo pide mientras hay actividad).

    Sin actividad, la interfaz deja de pedirlo y la sesión vence sola. Un cambio de contraseña o la desactivación de
    la cuenta invalidan el token actual, así que tampoco se puede renovar.
    """
    return auth_service.issue_token(current_user)


def _me(user: User) -> MeResponse:
    return MeResponse(
        id=user.id,
        rut=user.rut,
        email=user.email,
        full_name=user.full_name,
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        specialty=user.specialty.value if user.specialty else None,
        email_verified=user.email_verified_at is not None,
        role=user.role.value,
        must_change_password=bool(user.must_change_password),
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        password_changed_at=user.password_changed_at,
    )


@router.get("/me", response_model=MeResponse)
def get_me(current_user: User = Depends(get_authenticated_user)):
    """Información del usuario autenticado (incluye si debe cambiar su contraseña)."""
    return _me(current_user)


@router.put("/me/email", response_model=MeResponse)
def change_email(
    data: ChangeEmailRequest,
    request: Request,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    """Mi perfil: el usuario corrige su propio email confirmando con su contraseña actual."""
    user = auth_service.change_email(db, current_user, data.email, data.current_password, client_ip(request))
    return _me(user)


@router.post("/change-password", response_model=TokenResponse)
def change_password(
    data: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    """Cambia la contraseña del usuario autenticado. Revoca los tokens anteriores y entrega uno nuevo."""
    return auth_service.change_password(
        db, current_user, data.current_password, data.new_password, client_ip(request)
    )


def _activation_limit(request: Request) -> None:
    allowed, retry_after, _ = login_limiter.hit(
        f"activate:{client_ip(request) or 'desconocida'}", settings.LOGIN_RATE_LIMIT_PER_MINUTE
    )
    if not allowed:
        raise RateLimitedError(f"Demasiados intentos. Espere {retry_after} segundos", retry_after)


@router.get("/activation", response_model=ActivationPreview)
def activation_preview(token: str, request: Request, db: Session = Depends(get_db)):
    """Valida un link de activación (sin consumirlo) y devuelve el nombre y email para la pantalla."""
    _activation_limit(request)
    user = activation_service.preview(db, token)
    return ActivationPreview(first_name=user.first_name, email=user.email)


@router.post("/activate", response_model=TokenResponse)
def activate(data: ActivateRequest, request: Request, db: Session = Depends(get_db)):
    """Activa la cuenta desde el link del email: verifica el email, define la contraseña e inicia sesión."""
    _activation_limit(request)
    user = activation_service.activate(db, data.token, data.password, client_ip(request))
    return auth_service.issue_token(user)
