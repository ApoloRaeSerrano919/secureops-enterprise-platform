"""MCP server exposing read-only investigation helpers and safe action proposals.

No MCP tool executes privileged infrastructure actions. Mutating actions are
submitted back to SecureOps where RBAC, approval, idempotency and audit apply.
"""
from mcp.server.fastmcp import FastMCP

from src.incidents.service import get_incident
from src.rag.service import retrieve
from src.tools.policy import evaluate_tool_policy

mcp = FastMCP("secureops")


@mcp.tool()
def get_incident_context(incident_id: int) -> dict:
    return get_incident(incident_id) or {"error": "incident_not_found"}


@mcp.tool()
def search_security_knowledge(query: str, limit: int = 4) -> list[dict]:
    return [chunk.__dict__ for chunk in retrieve(query, limit)]


