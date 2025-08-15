from datetime import datetime, timedelta, timezone
from sqlalchemy import select, or_
from src.db.session import SessionLocal
from src.db.models import SecurityEvent, Incident, IncidentEvent, AuditEvent
from src.config.settings import settings

SEVERITY_WEIGHT = {
    "low": 10,
    "medium": 25,
    "high": 45,
    "critical": 70,
}

EVENT_BONUS = {
    "failed_login": 8,
    "successful_login_new_region": 20,
    "model_registry_access": 18,
    "large_export_request": 25,
    "dangerous_tool_request": 30,
    "policy_block": 12,
}

def _risk(events: list[SecurityEvent]) -> float:
    base = max((SEVERITY_WEIGHT.get(e.severity, 20) for e in events), default=0)
    bonus = sum(EVENT_BONUS.get(e.event_type, 0) for e in events)
    diversity = len({e.event_type for e in events}) * 3
    return min(100.0, float(base + bonus + diversity))

def correlate_open_events() -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=settings.correlation_window_minutes)

    with SessionLocal() as db:
        events = db.execute(
            select(SecurityEvent)
            .where(
                SecurityEvent.correlated.is_(False),
                SecurityEvent.occurred_at >= cutoff,
            )
            .order_by(SecurityEvent.occurred_at)
        ).scalars().all()

        grouped: dict[str, list[SecurityEvent]] = {}

        for event in events:
            key = event.principal or event.source_ip or event.service or f"event:{event.id}"
            grouped.setdefault(key, []).append(event)

        created = []

        for key, group in grouped.items():
            # Require either multiple related events or a critical event.
            if len(group) < 2 and not any(e.severity == "critical" for e in group):
                continue

            score = _risk(group)
            severity = (
                "critical" if score >= 85
                else "high" if score >= 65
                else "medium" if score >= 35
                else "low"
            )

            seq = db.execute(select(Incident.id).order_by(Incident.id.desc()).limit(1)).scalar()
            next_id = (seq or 0) + 1

            principal = next((e.principal for e in group if e.principal), None)
            primary_ip = next((e.source_ip for e in group if e.source_ip), None)

            incident = Incident(
                incident_number=f"INC-{datetime.now().year}-{next_id:06d}",
                title=f"Correlated security activity for {principal or primary_ip or key}",
                status="OPEN",
                severity=severity,
                risk_score=score,
                principal=principal,
                primary_ip=primary_ip,
            )
            db.add(incident)
            db.flush()

            for event in group:
                db.add(IncidentEvent(incident_id=incident.id, event_id=event.id))
                event.correlated = True

            db.add(AuditEvent(
                incident_id=incident.id,
                actor_user_id=None,
                action="incident_correlated",
                event_metadata={
                    "event_count": len(group),
                    "risk_score": score,
                    "correlation_key": key,
                },
            ))

            created.append({
                "incident_id": incident.id,
                "incident_number": incident.incident_number,
                "risk_score": score,
                "severity": severity,
                "event_count": len(group),
            })

        db.commit()
        return created
