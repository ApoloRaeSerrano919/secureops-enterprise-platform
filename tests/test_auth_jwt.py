from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from src.auth import service as auth_service
from src.config.settings import settings


def test_demo_token_maps_to_email():
    assert auth_service._email_from_demo_token("analyst-token") == "analyst@secureops.local"
    assert auth_service._email_from_demo_token("nope") is None


