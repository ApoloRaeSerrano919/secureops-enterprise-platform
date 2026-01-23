"""Authentication for SecureOps.

Modes (AUTH_MODE):
- demo: static bearer tokens (default)
- jwt: HS256 JWT validated with JWT_SECRET (mint via scripts/mint_dev_jwt.py)
- oidc: JWT validated against OIDC_JWKS_URL
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Header, HTTPException
from jwt import PyJWKClient
from sqlalchemy import select

from src.config.settings import settings
from src.db.models import User
from src.db.session import SessionLocal

DEMO_TOKENS = {
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


def _user_from_email(email: str) -> CurrentUser:
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


def _email_from_demo_token(token: str) -> str | None:
    return DEMO_TOKENS.get(token)


@lru_cache(maxsize=1)
def _jwks_client() -> PyJWKClient:
    if not settings.oidc_jwks_url:
        raise HTTPException(status_code=500, detail="oidc_jwks_url_not_configured")
    return PyJWKClient(settings.oidc_jwks_url)


