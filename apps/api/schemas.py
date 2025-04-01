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

class AIInvestigationRequest(BaseModel):
    prompt: str | None = Field(default=None, max_length=4000)

class ToolRequestCreate(BaseModel):
    tool_name: str
    arguments: dict
    idempotency_key: str | None = None

