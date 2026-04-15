from src.db.session import SessionLocal
from src.db.models import AuditEvent

def write_audit(*, incident_id=None, actor_user_id=None, action: str, metadata: dict):
    with SessionLocal() as db:
        row = AuditEvent(
            incident_id=incident_id,
            actor_user_id=actor_user_id,
            action=action,
            event_metadata=metadata,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id
