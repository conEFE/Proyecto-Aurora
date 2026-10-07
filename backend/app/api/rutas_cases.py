from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.bearer import get_current_user
from app.db.models.case import Case
from app.db.models.patient import Patient
from app.db.models.user import User
from app.deps import get_db

router = APIRouter()


# Schemas temporales - se reemplazarán cuando lleguen los modelos de BD
class CaseCreate(BaseModel):
    patient_code_anon: str
    patient_id: int | None = None  # ID del paciente si ya existe
    descripcion: str | None = None


class CaseResponse(BaseModel):
    id: int
    code: str
    created_at: datetime
    medico_id: int
    patient_id: int | None = None
    descripcion: str | None = None
    patient: dict | None = None  # Información del paciente si existe

    class Config:
        from_attributes = True


@router.post("", response_model=CaseResponse)
def create_case(
    case_data: CaseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Crea un nuevo caso clínico"""
    # Verificar que el código no exista
    existing_case = db.query(Case).filter(Case.code == case_data.patient_code_anon).first()
    if existing_case:
        raise HTTPException(status_code=400, detail="Código de paciente ya existe")

    # Verificar que el paciente existe si se proporciona patient_id
    patient_id = None
    if case_data.patient_id:
        patient = db.query(Patient).filter(Patient.id == case_data.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        patient_id = case_data.patient_id

    nuevo_caso = Case(code=case_data.patient_code_anon, medico_id=current_user.id, patient_id=patient_id)

    db.add(nuevo_caso)
    db.commit()
    db.refresh(nuevo_caso)

    # Construir respuesta manualmente
    response_data = {
        "id": nuevo_caso.id,
        "code": nuevo_caso.code,
        "created_at": nuevo_caso.created_at,
        "medico_id": nuevo_caso.medico_id,
        "patient_id": nuevo_caso.patient_id,
        "descripcion": getattr(nuevo_caso, "descripcion", None),
    }

    # Agregar información del paciente si existe
    if nuevo_caso.patient:
        response_data["patient"] = {
            "id": nuevo_caso.patient.id,
            "rut": nuevo_caso.patient.rut,
            "first_name": nuevo_caso.patient.first_name,
            "last_name": nuevo_caso.patient.last_name,
        }

    return CaseResponse(**response_data)


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Obtiene un caso clínico por ID"""
    caso = db.query(Case).filter(Case.id == case_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    # Verificar que el usuario tenga acceso (es el médico del caso o es ADMIN)
    if caso.medico_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="No tienes acceso a este caso")

    # Construir respuesta manualmente
    case_data = {
        "id": caso.id,
        "code": caso.code,
        "created_at": caso.created_at,
        "medico_id": caso.medico_id,
        "patient_id": caso.patient_id,
        "descripcion": getattr(caso, "descripcion", None),
    }

    # Agregar información del paciente si existe
    if caso.patient:
        case_data["patient"] = {
            "id": caso.patient.id,
            "rut": caso.patient.rut,
            "first_name": caso.patient.first_name,
            "last_name": caso.patient.last_name,
        }

    return CaseResponse(**case_data)


@router.get("", response_model=list[CaseResponse])
def list_cases(
    from_date: str | None = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    to_date: str | None = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista casos clínicos con filtros y paginación"""
    query = db.query(Case)

    # Si no es ADMIN, solo ver sus propios casos
    if current_user.role.value != "ADMIN":
        query = query.filter(Case.medico_id == current_user.id)

    # Filtros de fecha (si se implementan en el modelo)
    # Por ahora solo paginación

    cases = query.order_by(Case.created_at.desc()).offset((page - 1) * size).limit(size).all()

    # Convertir cada caso a CaseResponse manualmente
    result = []
    for caso in cases:
        case_data = {
            "id": caso.id,
            "code": caso.code,
            "created_at": caso.created_at,
            "medico_id": caso.medico_id,
            "patient_id": caso.patient_id,
            "descripcion": getattr(caso, "descripcion", None),
        }

        # Agregar información del paciente si existe
        if caso.patient:
            case_data["patient"] = {
                "id": caso.patient.id,
                "rut": caso.patient.rut,
                "first_name": caso.patient.first_name,
                "last_name": caso.patient.last_name,
            }

        result.append(CaseResponse(**case_data))

    return result
