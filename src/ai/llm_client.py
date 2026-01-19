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

    chunks: list[str] = []
    for item in payload.get("output", []) or []:
        for content in item.get("content", []) or []:
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    if not chunks:
        raise LLMProviderError("llm_response_missing_text")
    return "".join(chunks)


