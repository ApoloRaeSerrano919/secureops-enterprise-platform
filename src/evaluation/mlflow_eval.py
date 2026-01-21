from __future__ import annotations

import json
from pathlib import Path

import mlflow

from src.ml.tracking import configure_mlflow
from src.security.prompt_guard import inspect_prompt


def run() -> dict:
    cases = json.loads(Path("evals/prompt_injection_cases.json").read_text())
    blocked = sum(1 for case in cases if not inspect_prompt(case["prompt"]).allowed)
    block_rate = blocked / max(1, len(cases))
    configure_mlflow("secureops-llm-security-evals")
    with mlflow.start_run():
        mlflow.log_metric("prompt_injection_block_rate", block_rate)
        mlflow.log_param("case_count", len(cases))
    return {"case_count": len(cases), "prompt_injection_block_rate": block_rate}


if __name__ == "__main__":
    print(run())
