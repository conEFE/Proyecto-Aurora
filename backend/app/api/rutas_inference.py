from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.rbac import require_roles
from app.db.models.user import User, UserRole
from app.inference.providers import provider_status

router = APIRouter()
all_roles = require_roles(UserRole.ADMIN, UserRole.MEDICO, UserRole.ADMINISTRATIVO)


class InferenceStatus(BaseModel):
    model_config = {"protected_namespaces": ()}

    provider: str  # simulated | http
    reachable: bool | None = None
    fallback: bool = False
    model_version: str | None = None
    device: str | None = None
    clinically_validated: bool = False
    error: str | None = None


@router.get("/status", response_model=InferenceStatus)
def inference_status(_: User = Depends(all_roles)):
    """Qué proveedor de IA usa la plataforma y si el modelo real responde (sin datos de pacientes)."""
    return provider_status()
