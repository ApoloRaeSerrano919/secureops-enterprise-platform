"""Simple RAG layer backed by PostgreSQL + pgvector.

The retriever embeds approved security knowledge with a Hugging Face model and
returns the closest chunks. Retrieved text is treated as untrusted context by
the LLM prompt and never bypasses policy checks.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable

from sqlalchemy import text
from sentence_transformers import SentenceTransformer

from src.config.settings import settings
from src.db.session import SessionLocal


@dataclass
class RetrievedChunk:
    document_id: int
    title: str
    chunk_text: str
    score: float


@lru_cache(maxsize=1)
def embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


