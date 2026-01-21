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


