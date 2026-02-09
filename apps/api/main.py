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

@app.post("/incidents/{incident_id}/ai-investigation")
def ai_investigation(
    incident_id: int,
    payload: AIInvestigationRequest,
    user: CurrentUser = Depends(get_current_user),
):
    try:
        return summarize_incident(
            incident_id,
            analyst_prompt=payload.prompt,
            actor_user_id=user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

@app.post("/incidents/{incident_id}/ai-investigation/async")
def ai_investigation_async(
    incident_id: int,
    payload: AIInvestigationRequest,
    user: CurrentUser = Depends(get_current_user),
):
    job_id = enqueue_investigation(incident_id, payload.prompt or "", user.id)
    return {"job_id": job_id, "status": "queued"}

@app.get("/jobs/{job_id}")
def job_status(job_id: str, user: CurrentUser = Depends(get_current_user)):
    try:
        job = Job.fetch(job_id, connection=Redis.from_url(settings.redis_url))
    except Exception:
        raise HTTPException(status_code=404, detail="job_not_found")
    result = {"job_id": job.id, "status": job.get_status()}
    if job.is_finished:
        result["result"] = job.result
    if job.is_failed:
        result["error"] = "job_failed"
    return result

@app.post("/incidents/{incident_id}/tools")
def create_tool_request(
    incident_id: int,
    payload: ToolRequestCreate,
    user: CurrentUser = Depends(get_current_user),
):
    try:
        return request_tool(
            user=user,
            incident_id=incident_id,
            tool_name=payload.tool_name,
            arguments=payload.arguments,
            idempotency_key=payload.idempotency_key,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

