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


def get_service_health(arguments: dict) -> dict:
    """Read-only health probe.

    When SERVICE_HEALTH_BASE_URL is set, performs a real outbound HTTP GET to
    ``{base}/{service}/health`` (still subject to policy/RBAC before execution).
    When unset/empty, returns a simulated payload.
    """
    args = ServiceArgs(**arguments)
    base = (settings.service_health_base_url or "").rstrip("/")
    if not base:
        return {
            "service": args.service,
            "status": "healthy",
            "error_rate": 0.7,
            "mode": "simulated",
        }

    url = f"{base}/{args.service}/health"
    try:
        with httpx.Client(timeout=settings.service_health_timeout_seconds) as client:
            response = client.get(url)
            response.raise_for_status()
            body = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"raw": response.text}
    except httpx.HTTPError as exc:
        return {
            "service": args.service,
            "status": "unreachable",
            "mode": "http",
            "url": url,
            "error": exc.__class__.__name__,
        }

    return {
        "service": args.service,
        "status": body.get("status", "unknown") if isinstance(body, dict) else "unknown",
        "mode": "http",
        "url": url,
        "upstream": body,
    }


def revoke_session(arguments: dict) -> dict:
    args = SessionArgs(**arguments)
    return {
        "session_id": args.session_id,
        "action": "revoke_session",
        "result": "simulated_success",
    }


