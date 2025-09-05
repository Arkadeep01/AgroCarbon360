from pydantic import BaseModel, Field
from datetime import datetime


class AuditLogBase(BaseModel):
    auditor_id: int
    entity_type: str = Field(..., max_length=50)
    entity_id: int
    action: str = Field(..., max_length=255)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: str | None = None
    status: str = Field(default="pending", max_length=50)


class AuditLogCreate(AuditLogBase):
    pass


class AuditLog(AuditLogBase):
    id: int

    class Config:
        orm_mode = True