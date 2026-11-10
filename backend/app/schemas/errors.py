from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ErrorLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    occurred_at: datetime
    method: str
    path: str
    status_code: int
    error_type: str
    message: str | None
    location: str | None
    user_id: int | None
    request_id: str


class ErrorLogPage(BaseModel):
    items: list[ErrorLogOut]
    total: int
    page: int
    size: int


class ErrorTypeCount(BaseModel):
    error_type: str
    count: int
