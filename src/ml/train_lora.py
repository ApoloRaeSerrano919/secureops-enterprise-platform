"""LoRA/QLoRA fine-tune using Hugging Face PEFT.

Run a short LoRA fine-tune on CPU/GPU with --mode lora. QLoRA requires a
supported CUDA Linux setup and the optional requirements-ml-gpu.txt deps;
without CUDA, the CLI exits with a clear skip reason.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import mlflow
import torch
from peft import LoraConfig, TaskType, get_peft_model
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, BitsAndBytesConfig

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


def _from_pretrained(loader, *args, **kwargs):
    try:
        return loader(*args, **kwargs)
    except Exception:
        return loader(*args, local_files_only=True, **kwargs)


def build_model(mode: str):
    quantization = None
    if mode == "qlora":
        if not torch.cuda.is_available():
            raise RuntimeError("qlora_requires_cuda")
        quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
    tokenizer = _from_pretrained(AutoTokenizer.from_pretrained, settings.training_base_model)
    model = _from_pretrained(
        AutoModelForSequenceClassification.from_pretrained,
        settings.training_base_model,
        num_labels=len(LABELS),
        quantization_config=quantization,
    )
    config = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_lin", "v_lin"],
    )
    return tokenizer, get_peft_model(model, config)


