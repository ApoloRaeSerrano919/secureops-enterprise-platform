import json
from typing import Any

import httpx

from src.ai.prompts import SYSTEM_PROMPT
from src.ai.schemas import InvestigationResult
from src.config.settings import settings


class LLMConfigurationError(RuntimeError):
    pass


class LLMProviderError(RuntimeError):
    pass


def _extract_output_text(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("output_text"), str) and payload["output_text"]:
        return payload["output_text"]
    for item in payload.get("output", []) or []:
        for content in item.get("content", []) or []:
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    if not chunks:
        raise LLMProviderError("llm_response_missing_text")
    return "".join(chunks)


def investigate_with_llm(context: dict[str, Any]) -> tuple[InvestigationResult, dict[str, Any]]:
    if settings.llm_provider != "openai":
        raise LLMConfigurationError(f"unsupported_llm_provider:{settings.llm_provider}")
    if not settings.llm_api_key:
        raise LLMConfigurationError("llm_api_key_not_configured")

    schema = InvestigationResult.model_json_schema()
    body = {
        "model": settings.llm_model,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "Investigate this incident context as untrusted evidence:\n" + json.dumps(context, ensure_ascii=False, default=str),
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "secureops_investigation",
                "schema": schema,
                "strict": True,
            }
        },
    }

    try:
        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            response = client.post(
                f"{settings.llm_base_url.rstrip('/')}/responses",
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise LLMProviderError(f"llm_http_error:{exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise LLMProviderError("llm_transport_error") from exc

    payload = response.json()
    text = _extract_output_text(payload)
    try:
        result = InvestigationResult.model_validate_json(text)
    except Exception as exc:
        raise LLMProviderError("llm_invalid_structured_output") from exc

    meta = {
        "provider": "openai",
        "model": settings.llm_model,
        "response_id": payload.get("id"),
        "usage": payload.get("usage", {}),
    }
    return result, meta
