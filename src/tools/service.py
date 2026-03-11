import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from src.db.session import SessionLocal
from src.db.models import ToolRequest, ToolApproval, AuditEvent
from src.tools.policy import evaluate_tool_policy
from src.tools.registry import TOOL_HANDLERS

def request_tool(*, user, incident_id: int, tool_name: str, arguments: dict, idempotency_key: str | None = None) -> dict:
    key = idempotency_key or str(uuid.uuid4())

    with SessionLocal() as db:
        existing = db.execute(
            select(ToolRequest).where(ToolRequest.idempotency_key == key)
        ).scalar_one_or_none()

        if existing:
            return {
                "tool_request_id": existing.id,
                "status": existing.status,
                "deduplicated": True,
            }

        policy = evaluate_tool_policy(user.role, tool_name)

        if not policy.get("allowed"):
            db.add(AuditEvent(
                incident_id=incident_id,
                actor_user_id=user.id,
                action="tool_request_denied",
                event_metadata={
                    "tool": tool_name,
                    "reason": policy.get("reason"),
                },
            ))
            db.commit()
            return {
                "allowed": False,
                "reason": policy.get("reason"),
            }

        if tool_name not in TOOL_HANDLERS:
            return {
                "allowed": False,
                "reason": "tool_handler_not_found",
            }

        status = "PENDING_APPROVAL" if policy["requires_approval"] else "APPROVED"

        req = ToolRequest(
            incident_id=incident_id,
            requested_by=user.id,
            tool_name=tool_name,
            arguments=arguments,
            risk_level=policy["risk_level"],
            status=status,
            idempotency_key=key,
        )
        db.add(req)
        db.flush()

        db.add(AuditEvent(
            incident_id=incident_id,
            actor_user_id=user.id,
            action="tool_request_created",
            event_metadata={
                "tool_request_id": req.id,
                "tool": tool_name,
                "risk_level": policy["risk_level"],
                "requires_approval": policy["requires_approval"],
            },
        ))

        db.commit()
        db.refresh(req)

    if status == "APPROVED":
        return execute_tool_request(req.id)

    return {
        "allowed": True,
        "tool_request_id": req.id,
        "status": status,
        "approval_required": True,
    }

