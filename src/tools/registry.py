from pydantic import BaseModel, Field

class PrincipalArgs(BaseModel):
    principal: str = Field(min_length=3, max_length=255)

class ServiceArgs(BaseModel):
    service: str = Field(min_length=2, max_length=120)

class SessionArgs(BaseModel):
    session_id: str = Field(min_length=3, max_length=255)

def get_service_health(arguments: dict) -> dict:
    args = ServiceArgs(**arguments)
    return {
        "service": args.service,
        "status": "healthy",
        "error_rate": 0.7,
    }

def revoke_session(arguments: dict) -> dict:
    args = SessionArgs(**arguments)
    return {
        "session_id": args.session_id,
        "action": "revoke_session",
        "result": "simulated_success",
    }

def isolate_service(arguments: dict) -> dict:
    args = ServiceArgs(**arguments)
    return {
        "service": args.service,
        "action": "isolate_service",
        "result": "simulated_success",
    }

TOOL_HANDLERS = {
    "get_auth_activity": get_auth_activity,
    "get_service_health": get_service_health,
    "revoke_session": revoke_session,
    "isolate_service": isolate_service,
}
