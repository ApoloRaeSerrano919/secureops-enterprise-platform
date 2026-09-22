"""Mint HS256 study JWTs for AUTH_MODE=jwt (or demo dual-accept)."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

import jwt

from src.config.settings import settings

ROLE_EMAILS = {
    "analyst": "analyst@secureops.local",
    "responder": "responder@secureops.local",
    "admin": "admin@secureops.local",
}


def mint(role: str, hours: int = 8) -> str:
    email = ROLE_EMAILS[role]
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "email": email,
        "role": role,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + timedelta(hours=hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mint a SecureOps study JWT")
    parser.add_argument("--role", choices=sorted(ROLE_EMAILS), default="analyst")
    parser.add_argument("--hours", type=int, default=8)
    args = parser.parse_args()
    print(mint(args.role, hours=args.hours))
