from pydantic import BaseModel, Field
from datetime import datetime

class SecurityEventCreate(BaseModel):
    source: str
    event_type: str
    severity: str = "medium"
    principal: str | None = None
    source_ip: str | None = None
    service: str | None = None
    indicator: str | None = None
    raw_event: dict = {}
    occurred_at: datetime | None = None

class IncidentAssignRequest(BaseModel):
    user_id: int

class IncidentCloseRequest(BaseModel):
    resolution: str = Field(min_length=3, max_length=2000)

