from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import bcrypt
from app.deps import get_db
from app.auth.bearer import get_current_user
from app.auth.rbac import require_role
from app.db.models.user import User, UserRole
from app.db.models.case import Case
from app.db.models.patient import Patient
from app.db.models.image import Image
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class LoginRequest(BaseModel):
    rut: str
    password: str

class SignupRequest(BaseModel):
    rut: str
    email: str
    password: str
    role: str = "MEDICO"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    # bcrypt tiene límite de 72 bytes
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

@router.post("/signup")
def signup(user_data: SignupRequest, db: Session = Depends(get_db)):
    """Registra un nuevo usuario"""
    # Verificar si el RUT ya existe
    existing_user = db.query(User).filter(User.rut == user_data.rut).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="RUT ya registrado")
    
    # Verificar si el email ya existe
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Validar rol
    try:
        role = UserRole[user_data.role.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Rol invalido. Use MEDICO o ADMIN")
    
    # Crear nuevo usuario
    new_user = User(
        rut=user_data.rut,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "rut": new_user.rut,
        "email": new_user.email,
        "role": new_user.role.value,
        "message": "Usuario creado exitosamente"
    }

@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login con RUT y contraseña"""
    user = db.query(User).filter(User.rut == credentials.rut).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="RUT o contraseña incorrectos")
    
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="RUT o contraseña incorrectos")
    
    # Generar token simple (en producción usa JWT)
    token = f"{user.rut}-{user.role.value}"
    
    return {
        "token": token,
        "role": user.role.value,
        "rut": user.rut,
        "email": user.email
    }

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene la información del usuario actual"""
    return {
        "id": current_user.id,
        "rut": current_user.rut,
        "email": current_user.email,
        "role": current_user.role.value,
        "message": "Authentication successful"
    }