from pydantic import BaseModel, Field
import httpx

from src.config.settings import settings


class PrincipalArgs(BaseModel):
    principal: str = Field(min_length=3, max_length=255)


class ServiceArgs(BaseModel):
    service: str = Field(min_length=2, max_length=120)


class SessionArgs(BaseModel):
    session_id: str = Field(min_length=3, max_length=255)


def get_auth_activity(arguments: dict) -> dict:
    args = PrincipalArgs(**arguments)
    return {
        "principal": args.principal,
        "failed_logins": 8,
        "new_regions": ["PL"],
        "last_seen_ip": "185.199.110.42",
    }


