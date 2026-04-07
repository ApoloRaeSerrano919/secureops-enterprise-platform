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


class EventDataset(Dataset):
    def __init__(self, rows, tokenizer):
        self.rows = rows
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        encoded = self.tokenizer(
            row["text"], truncation=True, padding="max_length", max_length=128, return_tensors="pt"
        )
        item = {k: v.squeeze(0) for k, v in encoded.items()}
        item["labels"] = torch.tensor(LABELS[row["label"]], dtype=torch.long)
        return item


