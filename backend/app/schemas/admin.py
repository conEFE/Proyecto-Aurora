from datetime import datetime

from pydantic import BaseModel


class DayLogins(BaseModel):
    day: str
    ok: int
    failed: int


class AdminOverview(BaseModel):
    version: str
    users_total: int
    users_active: int
    users_by_role: dict[str, int]
    users_locked: int
    users_pending_password: int
    # Activos que no ingresan hace 30 días o más (o nunca)
    users_idle_30d: int
    admins_active: int
    # Ingresos fallidos, cambios de contraseña fallidos y firmas fallidas en las últimas 24 h
    security_events_24h: int
    logins_per_day: list[DayLogins]
    actions_7d: dict[str, int]
    server_errors_7d: int
    last_server_error_at: datetime | None
    audit_total: int
