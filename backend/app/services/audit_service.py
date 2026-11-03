"""Registro de auditoría (RNF05, Ley 19.628). El detalle nunca lleva datos sensibles en claro."""

from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.db.models.audit_log import AuditLog
from app.db.models.user import User

ACTIONS = {
    "LOGIN_OK",
    "LOGIN_FAIL",
    "VIEW",
    "CREATE",
    "UPDATE",
    "DOWNLOAD",
    "OVERRIDE",
    "CONFIG_CHANGE",
    "EXPORT",
}


def client_ip(request: Request | None) -> str | None:
    if request is None:
        return None
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:45]
    return request.client.host[:45] if request.client else None


def audit(
    db: Session,
    user: User | None,
    action: str,
    entity: str,
    entity_id: int | None = None,
    detail: dict[str, Any] | None = None,
    ip: str | None = None,
    commit: bool = True,
) -> AuditLog:
    if action not in ACTIONS:
        raise ValueError(f"Acción de auditoría desconocida: {action}")
    entry = AuditLog(
        user_id=user.id if user is not None else None,
        action=action,
        entity=entity,
        entity_id=entity_id,
        ip_address=ip,
        detail=detail or None,
    )
    db.add(entry)
    if commit:
        db.commit()
    return entry
