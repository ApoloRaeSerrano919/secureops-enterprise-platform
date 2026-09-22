"""MLflow helpers for local study runs without Compose."""
from __future__ import annotations

import urllib.request

import mlflow

from src.config.settings import settings


def configure_mlflow(experiment_name: str) -> str:
    """Point MLflow at Compose tracking URI, or fall back to local SQLite."""
    uri = settings.mlflow_tracking_uri
    if uri.startswith("http"):
        try:
            urllib.request.urlopen(uri, timeout=2)
            mlflow.set_tracking_uri(uri)
        except Exception:
            uri = "sqlite:///mlflow.db"
            mlflow.set_tracking_uri(uri)
    else:
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(experiment_name)
    return uri
