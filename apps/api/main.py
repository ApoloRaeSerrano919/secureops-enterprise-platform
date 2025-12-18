from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from apps.api.schemas import (
    SecurityEventCreate, IncidentAssignRequest, IncidentCloseRequest,
    AIInvestigationRequest, ToolRequestCreate, ToolApprovalRequest
)
from src.auth.service import CurrentUser, get_current_user
from src.events.service import ingest_event
from src.incidents.correlation import correlate_open_events
from src.incidents.service import get_incident, assign_incident, close_incident
from src.ai.investigator import summarize_incident
from src.ai.llm_client import LLMConfigurationError, LLMProviderError
from src.tools.service import request_tool, approve_tool_request
from src.db.session import SessionLocal
from src.db.models import Incident, AuditEvent, ToolRequest

app = FastAPI(
    title="SecureOps",
    version="2.0.0",
    description="Security event correlation with policy-gated response tools.",
)

@app.get("/health")
def health():
    return {"status": "ok"}

