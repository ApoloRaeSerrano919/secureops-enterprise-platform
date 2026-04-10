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


def train(data_path: str = "data/training/events.jsonl", epochs: int = 1):
    rows = [json.loads(line) for line in Path(data_path).read_text().splitlines() if line.strip()]
    tokenizer = AutoTokenizer.from_pretrained(settings.training_base_model)
    model = AutoModelForSequenceClassification.from_pretrained(settings.training_base_model, num_labels=len(LABELS))
    loader = DataLoader(EventDataset(rows, tokenizer), batch_size=4, shuffle=True)
    optimizer = AdamW(model.parameters(), lr=2e-5)

    configure_mlflow("secureops-event-severity")
    with mlflow.start_run():
        mlflow.log_params({"base_model": settings.training_base_model, "epochs": epochs, "samples": len(rows)})
        model.train()
        final_loss = 0.0
        for _ in range(epochs):
            for batch in loader:
                optimizer.zero_grad()
                output = model(**batch)
                output.loss.backward()
                optimizer.step()
                final_loss = float(output.loss.detach().cpu())
        mlflow.log_metric("final_train_loss", final_loss)
        Path("artifacts/severity-model").mkdir(parents=True, exist_ok=True)
        model.save_pretrained("artifacts/severity-model")
        tokenizer.save_pretrained("artifacts/severity-model")
        mlflow.log_artifacts("artifacts/severity-model", artifact_path="model")
    return {"samples": len(rows), "final_train_loss": final_loss}


if __name__ == "__main__":
    print(train())
