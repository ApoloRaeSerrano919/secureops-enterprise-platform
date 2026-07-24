"""Mint HS256 JWTs for AUTH_MODE=jwt (or demo dual-accept)."""
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


