from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from src.auth import service as auth_service
from src.config.settings import settings


def test_demo_token_maps_to_email():
    assert auth_service._email_from_demo_token("analyst-token") == "analyst@secureops.local"
    assert auth_service._email_from_demo_token("nope") is None


def test_jwt_roundtrip_email_claim(monkeypatch):
    monkeypatch.setattr(settings, "auth_mode", "jwt")
    monkeypatch.setattr(settings, "jwt_secret", "test-secret")
    monkeypatch.setattr(settings, "jwt_issuer", "secureops-local")
    monkeypatch.setattr(settings, "jwt_audience", "secureops-api")
    monkeypatch.setattr(settings, "jwt_algorithm", "HS256")

    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": "analyst@secureops.local",
            "email": "analyst@secureops.local",
            "iss": "secureops-local",
            "aud": "secureops-api",
            "iat": now,
            "exp": now + timedelta(hours=1),
        },
        "test-secret",
        algorithm="HS256",
    )
    assert auth_service._email_from_jwt(token) == "analyst@secureops.local"


def test_jwt_rejects_bad_signature(monkeypatch):
    monkeypatch.setattr(settings, "auth_mode", "jwt")
    monkeypatch.setattr(settings, "jwt_secret", "test-secret")
    monkeypatch.setattr(settings, "jwt_issuer", "secureops-local")
    monkeypatch.setattr(settings, "jwt_audience", "secureops-api")
    monkeypatch.setattr(settings, "jwt_algorithm", "HS256")

    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "email": "analyst@secureops.local",
            "iss": "secureops-local",
            "aud": "secureops-api",
            "iat": now,
            "exp": now + timedelta(hours=1),
        },
        "wrong-secret",
        algorithm="HS256",
    )
    with pytest.raises(HTTPException) as exc:
        auth_service._email_from_jwt(token)
    assert exc.value.status_code == 401
