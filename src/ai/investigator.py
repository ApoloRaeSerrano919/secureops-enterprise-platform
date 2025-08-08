from src.incidents.service import get_incident
from src.security.prompt_guard import inspect_prompt
from src.db.session import SessionLocal
from src.db.models import Incident, AuditEvent
from src.ai.llm_client import investigate_with_llm


def summarize_incident(incident_id: int, analyst_prompt: str | None = None, actor_user_id: int | None = None) -> dict:
    if analyst_prompt:
        guard = inspect_prompt(analyst_prompt)
        if not guard.allowed:
            return {
                "allowed": False,
                "reason": guard.reason,
                "summary": "Prompt blocked by AI security policy.",
                "recommended_actions": [],
            }

    data = get_incident(incident_id)
    if not data:
        raise ValueError("incident_not_found")

    context = {
        "incident": data["incident"],
        "timeline": data["timeline"],
        "analyst_question": analyst_prompt,
        "instruction": "Use only this incident evidence. Do not execute actions; recommendations are advisory only.",
    }

    investigation, llm_meta = investigate_with_llm(context)

    with SessionLocal() as db:
        row = db.get(Incident, incident_id)
        row.ai_summary = investigation.summary
        db.add(AuditEvent(
            incident_id=incident_id,
            actor_user_id=actor_user_id,
            action="llm_investigation_completed",
            event_metadata={
                "timeline_events": len(data["timeline"]),
                "recommendation_count": len(investigation.recommended_actions),
                "confidence": investigation.confidence,
                "severity_assessment": investigation.severity_assessment,
                "provider": llm_meta["provider"],
                "model": llm_meta["model"],
                "response_id": llm_meta.get("response_id"),
            },
        ))
        db.commit()

    return {
        "allowed": True,
        **investigation.model_dump(),
        "evidence_count": len(data["timeline"]),
        "llm": {
            "provider": llm_meta["provider"],
            "model": llm_meta["model"],
            "response_id": llm_meta.get("response_id"),
        },
    }
