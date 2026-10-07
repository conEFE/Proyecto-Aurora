from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.bearer import get_current_user
from app.db.models.patient import Patient
from app.db.models.user import User
from app.deps import get_db

router = APIRouter()


class PatientCreate(BaseModel):
    rut: str
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    sex: str | None = None  # 'M', 'F', 'O'
    medical_history: str | None = None


class PatientResponse(BaseModel):
    id: int
    rut: str
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    sex: str | None = None
    medical_history: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=PatientResponse)
def create_patient(
    patient_data: PatientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Crea un nuevo paciente"""
    # Verificar si el RUT ya existe
    existing_patient = db.query(Patient).filter(Patient.rut == patient_data.rut).first()
    if existing_patient:
        raise HTTPException(status_code=400, detail="RUT ya registrado")

    nuevo_paciente = Patient(
        rut=patient_data.rut,
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        birth_date=patient_data.birth_date,
        sex=patient_data.sex,
        medical_history=patient_data.medical_history,
    )

    db.add(nuevo_paciente)
    db.commit()
    db.refresh(nuevo_paciente)

    return nuevo_paciente


@router.get("", response_model=list[PatientResponse])
def list_patients(
    search: str | None = Query(None, description="Buscar por RUT o nombre"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista pacientes con búsqueda opcional"""
    query = db.query(Patient)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Patient.rut.ilike(search_term))
            | (Patient.first_name.ilike(search_term))
            | (Patient.last_name.ilike(search_term))
        )

    patients = query.order_by(Patient.created_at.desc()).limit(50).all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Obtiene un paciente por ID"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient
