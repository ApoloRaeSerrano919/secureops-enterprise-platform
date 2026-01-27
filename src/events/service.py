from datetime import datetime, timezone
from src.db.session import SessionLocal
from src.db.models import SecurityEvent

VALID_SEVERITIES = {"low","medium","high","critical"}

def ingest_event(payload: dict) -> dict:
    severity = str(payload.get("severity","medium")).lower()
    if severity not in VALID_SEVERITIES:
        severity = "medium"

    occurred_at = payload.get("occurred_at")
    if isinstance(occurred_at, str):
        occurred_at = datetime.fromisoformat(occurred_at.replace("Z","+00:00"))
    if occurred_at is None:
        occurred_at = datetime.now(timezone.utc)

    row = SecurityEvent(
        source=payload["source"],
        event_type=payload["event_type"],
        severity=severity,
        principal=payload.get("principal"),
        source_ip=payload.get("source_ip"),
        service=payload.get("service"),
        indicator=payload.get("indicator"),
        raw_event=payload.get("raw_event", payload),
        occurred_at=occurred_at,
        correlated=False,
    )

    with SessionLocal() as db:
        db.add(row)
        db.commit()
        db.refresh(row)
        return {
            "event_id": row.id,
            "severity": row.severity,
            "occurred_at": row.occurred_at.isoformat(),
        }
