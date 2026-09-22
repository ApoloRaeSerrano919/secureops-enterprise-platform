ROLE_ORDER = {
    "analyst": 1,
    "responder": 2,
    "admin": 3,
}

POLICY = {
    "get_auth_activity": {
        "risk_level": "low",
        "requires_approval": False,
        "roles": {"analyst","responder","admin"},
    },
    "get_service_health": {
        "risk_level": "low",
        "requires_approval": False,
        "roles": {"analyst","responder","admin"},
    },
    "revoke_session": {
        "risk_level": "high",
        "requires_approval": True,
        "roles": {"responder","admin"},
    },
    "isolate_service": {
        "risk_level": "critical",
        "requires_approval": True,
        "roles": {"admin"},
    },
}

def evaluate_tool_policy(role: str, tool_name: str) -> dict:
    policy = POLICY.get(tool_name)
    if not policy:
        return {
            "allowed": False,
            "reason": "unknown_tool",
        }

    if role not in policy["roles"]:
        return {
            "allowed": False,
            "reason": "role_not_allowed",
            "risk_level": policy["risk_level"],
        }

    return {
        "allowed": True,
        "risk_level": policy["risk_level"],
        "requires_approval": policy["requires_approval"],
    }
