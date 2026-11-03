"""Datos de referencia mínimos que deben existir en toda BD."""

from sqlalchemy.orm import Session


def ensure_reference_data(db: Session) -> None:
    """La configuración de triage v1 la crea la migración; esto la repone si la tabla quedó vacía."""
    from app.services.triage_service import ensure_default_config

    ensure_default_config(db)
