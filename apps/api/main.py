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
from src.queueing.jobs import enqueue_investigation
from src.observability.metrics import HTTP_REQUESTS, metrics_response
from redis import Redis
from rq.job import Job
from src.config.settings import settings

app = FastAPI(
    title="SecureOps",
    version="2.0.0",
    description="Security event correlation with policy-gated response tools.",
 )

@app.middleware("http")
async def observe_requests(request, call_next):
    response = await call_next(request)
    HTTP_REQUESTS.labels(request.method, request.url.path, response.status_code).inc()
    return response

@app.get("/metrics")
def metrics():
    return metrics_response()

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/internal/probes/{service}/health")
def service_health_probe(service: str):
    """Local probe target for the real HTTP get_service_health adapter."""
    return {"service": service, "status": "healthy", "source": "secureops-probe"}


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

