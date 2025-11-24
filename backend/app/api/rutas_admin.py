from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.deps import get_db
from app.auth.bearer import get_current_user
from app.auth.rbac import require_role
from app.db.models.user import User
from app.db.models.case import Case
from app.db.models.patient import Patient
from app.db.models.image import Image
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

class AdminStatsResponse(BaseModel):
    total_users: int
    total_cases: int
    total_patients: int
    active_sessions: int  # Por ahora retornamos 0, se puede implementar con sesiones reales

class RecentUserResponse(BaseModel):
    id: int
    rut: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene estadísticas generales del sistema (solo ADMIN)"""
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Solo administradores pueden acceder a estas estadísticas")
    
    total_users = db.query(User).count()
    total_cases = db.query(Case).count()
    total_patients = db.query(Patient).count()
    # Por ahora, active_sessions es 0. Se puede implementar con un sistema de sesiones
    active_sessions = 0
    
    return AdminStatsResponse(
        total_users=total_users,
        total_cases=total_cases,
        total_patients=total_patients,
        active_sessions=active_sessions
    )

@router.get("/users/recent", response_model=List[RecentUserResponse])
def get_recent_users(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene los usuarios más recientes (solo ADMIN)"""
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Solo administradores pueden acceder a esta información")
    
    # Necesitamos agregar created_at al modelo User si no existe
    # Por ahora, simplemente retornamos los últimos usuarios por ID
    users = db.query(User).order_by(User.id.desc()).limit(limit).all()
    
    return [
        RecentUserResponse(
            id=user.id,
            rut=user.rut,
            email=user.email,
            role=user.role.value,
            created_at=datetime.now()  # Temporal, hasta que agreguemos created_at al modelo
        )
        for user in users
    ]
