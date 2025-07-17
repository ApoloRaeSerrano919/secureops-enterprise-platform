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


def downgrade() -> None:
    op.drop_table("evaluation_runs")
    op.drop_table("audit_events")
    op.drop_table("tool_approvals")
    op.drop_table("tool_requests")
    op.drop_table("tool_definitions")
    op.drop_table("incident_events")
    op.drop_table("incidents")
    op.drop_table("security_events")
    op.drop_table("users")
