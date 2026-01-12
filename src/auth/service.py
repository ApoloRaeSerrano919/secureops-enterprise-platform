from dataclasses import dataclass
from fastapi import Header, HTTPException
from sqlalchemy import select
from src.db.session import SessionLocal
from src.db.models import User

TOKENS = {
    "analyst-token": "analyst@secureops.local",
    "responder-token": "responder@secureops.local",
    "admin-token": "admin@secureops.local",
}

