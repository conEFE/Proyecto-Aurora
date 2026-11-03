from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    action: str
    entity: str
    entity_id: int | None
    ip_address: str | None
    detail: dict[str, Any] | None
    created_at: datetime


class AuditPage(BaseModel):
    items: list[AuditOut]
    total: int
    page: int
    size: int
