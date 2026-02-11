"""MCP server exposing read-only investigation helpers and safe action proposals.

No MCP tool executes privileged infrastructure actions. Mutating actions are
submitted back to SecureOps where RBAC, approval, idempotency and audit apply.
"""
from mcp.server.fastmcp import FastMCP

from src.incidents.service import get_incident
from src.rag.service import retrieve
from src.tools.policy import evaluate_tool_policy

mcp = FastMCP("secureops")


