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


