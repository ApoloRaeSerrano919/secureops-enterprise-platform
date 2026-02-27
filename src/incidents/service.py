from sqlalchemy import select
from src.db.session import SessionLocal
from src.db.models import Incident, IncidentEvent, SecurityEvent, AuditEvent

def get_incident(incident_id: int) -> dict | None:
    with SessionLocal() as db:
        incident = db.get(Incident, incident_id)
        if not incident:
            return None

        rows = db.execute(
            select(SecurityEvent)
            .join(IncidentEvent, IncidentEvent.event_id == SecurityEvent.id)
            .where(IncidentEvent.incident_id == incident_id)
            .order_by(SecurityEvent.occurred_at)
        ).scalars().all()

        return {
            "incident": {
                "id": incident.id,
                "incident_number": incident.incident_number,
                "title": incident.title,
                "status": incident.status,
                "severity": incident.severity,
                "risk_score": incident.risk_score,
                "principal": incident.principal,
                "primary_ip": incident.primary_ip,
                "assigned_to": incident.assigned_to,
                "ai_summary": incident.ai_summary,
            },
            "timeline": [
                {
                    "event_id": e.id,
                    "source": e.source,
                    "event_type": e.event_type,
                    "severity": e.severity,
                    "principal": e.principal,
                    "source_ip": e.source_ip,
                    "service": e.service,
                    "occurred_at": e.occurred_at.isoformat(),
                }
                for e in rows
            ],
        }

def close_incident(incident_id: int, actor_id: int, resolution: str) -> dict:
    with SessionLocal() as db:
        incident = db.get(Incident, incident_id)
        if not incident:
            raise ValueError("incident_not_found")

        incident.status = "CLOSED"
        db.add(AuditEvent(
            incident_id=incident_id,
            actor_user_id=actor_id,
            action="incident_closed",
            event_metadata={"resolution": resolution},
        ))
        db.commit()
        return {"incident_id": incident_id, "status": "CLOSED"}
