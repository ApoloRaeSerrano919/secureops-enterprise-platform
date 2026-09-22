from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

HTTP_REQUESTS = Counter("secureops_http_requests_total", "HTTP requests", ["method", "path", "status"])
LLM_INVESTIGATIONS = Counter("secureops_llm_investigations_total", "LLM investigations", ["status"])
LLM_LATENCY = Histogram("secureops_llm_investigation_seconds", "LLM investigation latency")
TOOL_REQUESTS = Counter("secureops_tool_requests_total", "Tool requests", ["tool", "outcome"])


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
