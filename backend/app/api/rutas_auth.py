from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
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


@router.get("/me", response_model=MeResponse)
def get_me(current_user: User = Depends(get_authenticated_user)):
    """Información del usuario autenticado (incluye si debe cambiar su contraseña)."""
    return MeResponse(
        id=current_user.id,
        rut=current_user.rut,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        must_change_password=bool(current_user.must_change_password),
    )


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
