"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
    )
    op.create_table(
        "security_events",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=30), nullable=False),
        sa.Column("principal", sa.String(length=255), nullable=True),
        sa.Column("source_ip", sa.String(length=64), nullable=True),
        sa.Column("service", sa.String(length=120), nullable=True),
        sa.Column("indicator", sa.String(length=255), nullable=True),
        sa.Column("raw_event", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correlated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_security_events_source", "security_events", ["source"])
    op.create_index("ix_security_events_event_type", "security_events", ["event_type"])
    op.create_index("ix_security_events_severity", "security_events", ["severity"])
    op.create_index("ix_security_events_principal", "security_events", ["principal"])
    op.create_index("ix_security_events_source_ip", "security_events", ["source_ip"])
    op.create_index("ix_security_events_service", "security_events", ["service"])
    op.create_index("ix_security_events_occurred_at", "security_events", ["occurred_at"])

    op.create_table(
        "incidents",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("incident_number", sa.String(length=50), nullable=False, unique=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="OPEN"),
        sa.Column("severity", sa.String(length=30), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("principal", sa.String(length=255), nullable=True),
        sa.Column("primary_ip", sa.String(length=64), nullable=True),
        sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_incidents_status", "incidents", ["status"])
    op.create_index("ix_incidents_severity", "incidents", ["severity"])

    op.create_table(
        "incident_events",
        sa.Column("incident_id", sa.BigInteger(), sa.ForeignKey("incidents.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("event_id", sa.BigInteger(), sa.ForeignKey("security_events.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "tool_definitions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("risk_level", sa.String(length=30), nullable=False),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("allowed_roles", sa.JSON(), nullable=False),
    )

    op.create_table(
        "tool_requests",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("incident_id", sa.BigInteger(), sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("requested_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tool_name", sa.String(length=120), nullable=False),
        sa.Column("arguments", sa.JSON(), nullable=False),
        sa.Column("risk_level", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("idempotency_key", sa.String(length=120), nullable=False, unique=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tool_requests_incident_id", "tool_requests", ["incident_id"])
    op.create_index("ix_tool_requests_status", "tool_requests", ["status"])

    op.create_table(
        "tool_approvals",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("tool_request_id", sa.BigInteger(), sa.ForeignKey("tool_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("approver_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("decision", sa.String(length=20), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_tool_approvals_tool_request_id", "tool_approvals", ["tool_request_id"])

    op.create_table(
        "audit_events",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("incident_id", sa.BigInteger(), sa.ForeignKey("incidents.id"), nullable=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_events_incident_id", "audit_events", ["incident_id"])
    op.create_index("ix_audit_events_action", "audit_events", ["action"])

    op.create_table(
        "evaluation_runs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("prompt_injection_block_rate", sa.Float(), nullable=False),
        sa.Column("unsafe_tool_call_rate", sa.Float(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


