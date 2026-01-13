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

@dataclass
class CurrentUser:
    id: int
    email: str
    name: str
    role: str

async def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing_token")

    token = authorization.removeprefix("Bearer ").strip()
    email = TOKENS.get(token)
    if not email:
        raise HTTPException(status_code=401, detail="invalid_token")

    with SessionLocal() as db:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="user_not_found")

        return CurrentUser(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
        )
