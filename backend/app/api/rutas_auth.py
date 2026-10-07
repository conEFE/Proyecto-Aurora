from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.bearer import get_current_user
from app.auth.security import hash_password
from app.db.models.user import User, UserRole
from app.deps import get_db
from app.services import auth_service

router = APIRouter()


class LoginRequest(BaseModel):
    rut: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str | None = None


class SignupRequest(BaseModel):
    rut: str
    email: str
    password: str
    role: str = "MEDICO"


@router.post("/signup")
def signup(user_data: SignupRequest, db: Session = Depends(get_db)):
    """Registro heredado de la v1.0 (se reemplaza por /admin/users en el Sprint 2)."""
    if db.query(User).filter(User.rut == user_data.rut).first():
        raise HTTPException(status_code=400, detail="RUT ya registrado")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    try:
        role = UserRole[user_data.role.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Rol inválido")
    user = User(
        rut=user_data.rut,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "rut": user.rut, "email": user.email, "role": user.role.value}


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login con RUT y contraseña. Devuelve un JWT firmado (HS256)."""
    try:
        user = auth_service.authenticate(db, credentials.rut, credentials.password)
    except auth_service.AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return auth_service.issue_token(user)


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Información del usuario autenticado."""
    return {
        "id": current_user.id,
        "rut": current_user.rut,
        "email": current_user.email,
        "role": current_user.role.value,
    }
