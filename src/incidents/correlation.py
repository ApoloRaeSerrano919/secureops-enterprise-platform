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

