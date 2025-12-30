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

@app.post("/events")
def create_event(
    payload: SecurityEventCreate,
    user: CurrentUser = Depends(get_current_user),
):
    result = ingest_event(payload.model_dump())
    return result

@app.post("/correlate")
def correlate(
    user: CurrentUser = Depends(get_current_user),
):
    if user.role not in {"responder","admin"}:
        raise HTTPException(status_code=403, detail="forbidden")
    return {"incidents": correlate_open_events()}

@app.get("/incidents")
def list_incidents(
    user: CurrentUser = Depends(get_current_user),
):
    with SessionLocal() as db:
        rows = db.execute(
            select(Incident).order_by(Incident.created_at.desc()).limit(100)
        ).scalars().all()

        return {
            "incidents": [
                {
                    "id": x.id,
                    "incident_number": x.incident_number,
                    "title": x.title,
                    "status": x.status,
                    "severity": x.severity,
                    "risk_score": x.risk_score,
                    "principal": x.principal,
                    "created_at": x.created_at,
                }
                for x in rows
            ]
        }

@app.get("/incidents/{incident_id}")
def incident_detail(
    incident_id: int,
    user: CurrentUser = Depends(get_current_user),
):
    result = get_incident(incident_id)
    if not result:
        raise HTTPException(status_code=404, detail="incident_not_found")
    return result

@app.post("/incidents/{incident_id}/assign")
def assign(
    incident_id: int,
    payload: IncidentAssignRequest,
    user: CurrentUser = Depends(get_current_user),
):
    if user.role not in {"responder","admin"}:
        raise HTTPException(status_code=403, detail="forbidden")
    try:
        return assign_incident(incident_id, payload.user_id, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

