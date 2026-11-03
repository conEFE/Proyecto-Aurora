from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.bearer import get_current_user
from app.db.models.user import User
from app.deps import get_db
from app.services import auth_service
from app.services.audit_service import client_ip

router = APIRouter()


class LoginRequest(BaseModel):
    rut: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str | None = None


class MeResponse(BaseModel):
    id: int
    rut: str
    email: str
    full_name: str
    role: str


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Login con RUT y contraseña. Devuelve un JWT firmado (HS256)."""
    try:
        user = auth_service.authenticate(db, credentials.rut, credentials.password, client_ip(request))
    except auth_service.AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return auth_service.issue_token(user)


@router.get("/me", response_model=MeResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Información del usuario autenticado."""
    return MeResponse(
        id=current_user.id,
        rut=current_user.rut,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
    )
