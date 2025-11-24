from fastapi import Header, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session
from app.deps import get_db
from app.db.models.user import User

def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "").strip()
    return token

def get_user_from_token(token: str, db: Session) -> User:
    # Token formato: "RUT-ROLE" (el RUT puede tener guiones, ej: "19291836-7-MEDICO")
    try:
        # Dividir desde la derecha para separar el rol del RUT
        # El RUT puede tener guiones (ej: "19291836-7"), así que tomamos todo excepto la última parte
        parts = token.rsplit("-", 1)
        if len(parts) != 2:
            raise HTTPException(status_code=403, detail="Invalid token format")
        
        rut = parts[0]  # Todo antes del último guión (ej: "19291836-7")
        role = parts[1]  # La última parte (ej: "MEDICO")
        
        user = db.query(User).filter(User.rut == rut).first()
        if not user:
            raise HTTPException(status_code=403, detail="Invalid token")
        return user
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid token format")

def get_current_user_role(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
) -> str:
    user = get_user_from_token(token, db)
    return user.role.value

def get_role_from_token(token: str) -> str:
    # Token formato: "RUT-ROLE" (el RUT puede tener guiones)
    try:
        # Dividir desde la derecha para obtener el rol
        _, role = token.rsplit("-", 1)
        return role
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid token format")

def get_current_user_role(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
) -> str:
    user = get_user_from_token(token, db)
    return user.role.value

def get_current_user(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
) -> User:
    """Obtiene el usuario actual desde el token"""
    return get_user_from_token(token, db)