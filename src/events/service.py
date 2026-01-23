from datetime import datetime, timezone
from src.db.session import SessionLocal
from src.db.models import SecurityEvent

VALID_SEVERITIES = {"low","medium","high","critical"}

