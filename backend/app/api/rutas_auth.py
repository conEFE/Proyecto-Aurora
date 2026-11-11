from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.auth.bearer import get_authenticated_user
from app.db.models.user import User
from app.deps import get_db
from app.services import auth_service
from app.services.audit_service import client_ip

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


def _me(user: User) -> MeResponse:
    return MeResponse(
        id=user.id,
        rut=user.rut,
        email=user.email,
        full_name=user.full_name,
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
