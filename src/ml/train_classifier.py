"""Small Hugging Face/PyTorch fine-tuning workflow for event severity classification.

Compact training/evaluation path with optional MLflow tracking.
"""
from __future__ import annotations

import json
from pathlib import Path

import mlflow
import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.config.settings import settings
from src.ml.tracking import configure_mlflow

LABELS = {"low": 0, "medium": 1, "high": 2, "critical": 3}


