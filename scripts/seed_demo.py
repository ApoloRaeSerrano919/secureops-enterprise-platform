from datetime import datetime, timezone, timedelta
from src.db.session import SessionLocal
from src.db.models import User, ToolDefinition
from src.events.service import ingest_event

def main():
    with SessionLocal() as db:
        users = [
            User(email="analyst@secureops.local", name="Alex Analyst", role="analyst"),
            User(email="responder@secureops.local", name="Riley Responder", role="responder"),
            User(email="admin@secureops.local", name="Morgan Admin", role="admin"),
        ]
        db.add_all(users)

        db.add_all([
            ToolDefinition(
                name="get_auth_activity",
                risk_level="low",
                requires_approval=False,
                allowed_roles=["analyst","responder","admin"],
            ),
            ToolDefinition(
                name="get_service_health",
                risk_level="low",
                requires_approval=False,
                allowed_roles=["analyst","responder","admin"],
            ),
            ToolDefinition(
                name="revoke_session",
                risk_level="high",
                requires_approval=True,
                allowed_roles=["responder","admin"],
            ),
            ToolDefinition(
                name="isolate_service",
                risk_level="critical",
                requires_approval=True,
                allowed_roles=["admin"],
            ),
        ])

        db.commit()

    now = datetime.now(timezone.utc)

    events = [
        {
            "source":"identity",
            "event_type":"failed_login",
            "severity":"medium",
            "principal":"user@example.com",
            "source_ip":"185.199.110.42",
            "raw_event":{"attempts":8},
            "occurred_at":now-timedelta(minutes=8),
        },
        {
            "source":"identity",
            "event_type":"successful_login_new_region",
            "severity":"high",
            "principal":"user@example.com",
            "source_ip":"185.199.110.42",
            "raw_event":{"country":"PL"},
            "occurred_at":now-timedelta(minutes=6),
        },
        {
            "source":"model-registry",
            "event_type":"model_registry_access",
            "severity":"high",
            "principal":"user@example.com",
            "source_ip":"185.199.110.42",
            "service":"model-registry",
            "raw_event":{"model":"payments-risk-v3"},
            "occurred_at":now-timedelta(minutes=4),
        },
        {
            "source":"agent-gateway",
            "event_type":"dangerous_tool_request",
            "severity":"critical",
            "principal":"user@example.com",
            "source_ip":"185.199.110.42",
            "service":"ops-agent",
            "raw_event":{"tool":"export_model_data"},
            "occurred_at":now-timedelta(minutes=2),
        },
        {
            "source":"policy-engine",
            "event_type":"policy_block",
            "severity":"high",
            "principal":"user@example.com",
            "source_ip":"185.199.110.42",
            "service":"ops-agent",
            "raw_event":{"reason":"tool_not_allowed"},
            "occurred_at":now-timedelta(minutes=1),
        },
    ]

    for event in events:
        ingest_event(event)

    print("Seeded users, tools, and correlated-event demo data.")

if __name__ == "__main__":
    main()
