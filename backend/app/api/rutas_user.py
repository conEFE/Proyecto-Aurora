from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from app.deps import get_db
from app.auth.bearer import get_current_user
from app.db.models.user import User
from app.db.models.case import Case
from app.db.models.patient import Patient
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class UserInfoResponse(BaseModel):
    id: int
    rut: str
    email: str
    role: str

    class Config:
        from_attributes = True

class UserPatientResponse(BaseModel):
    id: int
    rut: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True

class SupportTicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_at: str

@router.get("/info", response_model=UserInfoResponse)
def get_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene la información del usuario actual"""
    return UserInfoResponse(
        id=current_user.id,
        rut=current_user.rut,
        email=current_user.email,
        role=current_user.role.value
    )

@router.get("/patients", response_model=List[UserPatientResponse])
def get_user_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene los pacientes asociados al médico actual"""
    # Obtener todos los casos del médico
    cases = db.query(Case).filter(Case.medico_id == current_user.id).all()
    
    # Extraer los IDs de pacientes únicos
    patient_ids = set()
    for case in cases:
        if case.patient_id:
            patient_ids.add(case.patient_id)
    
    # Obtener los pacientes
    if not patient_ids:
        return []
    
    patients = db.query(Patient).filter(Patient.id.in_(patient_ids)).all()
    
    return [
        UserPatientResponse(
            id=patient.id,
            rut=patient.rut,
            first_name=patient.first_name,
            last_name=patient.last_name
        )
        for patient in patients
    ]

@router.get("/tickets", response_model=List[SupportTicketResponse])
def get_support_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene los tickets de soporte del usuario actual"""
    # Por ahora retornamos una lista vacía o mock
    # En el futuro se puede crear un modelo SupportTicket
    # Por ahora, retornamos datos mock
    return [
        SupportTicketResponse(
            id=1,
            title="Problema con carga de imágenes",
            description="No puedo subir imágenes mayores a 5MB",
            status="open",
            created_at="2025-01-15T10:00:00Z"
        ),
        SupportTicketResponse(
            id=2,
            title="Consulta sobre resultados",
            description="¿Cómo interpreto los niveles de confianza?",
            status="resolved",
            created_at="2025-01-10T14:30:00Z"
        )
    ]
