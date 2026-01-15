from src.incidents.service import get_incident
from src.security.prompt_guard import inspect_prompt
from src.db.session import SessionLocal
from src.db.models import Incident, AuditEvent
from src.ai.llm_client import investigate_with_llm


def _rag_context(data: dict, analyst_prompt: str | None) -> list[dict]:
    query_parts = [data["incident"].get("title", ""), analyst_prompt or ""]
    for event in data["timeline"][-8:]:
        query_parts.append(str(event.get("event_type", "")))
        query_parts.append(str(event.get("indicator", "")))
    query = " ".join(part for part in query_parts if part).strip()
    if not query:
        return []
    try:
        from src.rag.service import retrieve

        return [chunk.__dict__ for chunk in retrieve(query)]
    except Exception:
        # RAG is enrichment, not an availability dependency for core incident response.
        return []


