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


def embed(text_value: str) -> list[float]:
    vector = embedding_model().encode(text_value, normalize_embeddings=True)
    return vector.tolist()


def index_documents(documents: Iterable[tuple[str, str]]) -> int:
    count = 0
    with SessionLocal() as db:
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS knowledge_chunks (
                id BIGSERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                chunk_text TEXT NOT NULL,
                embedding vector(384) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT now()
            )
        """))
        for title, chunk in documents:
            vector = embed(chunk)
            db.execute(
                text("INSERT INTO knowledge_chunks(title, chunk_text, embedding) VALUES (:t, :c, CAST(:e AS vector))"),
                {"t": title, "c": chunk, "e": str(vector)},
            )
            count += 1
        db.commit()
    return count


def retrieve(query: str, limit: int | None = None) -> list[RetrievedChunk]:
    k = limit or settings.rag_top_k
    vector = embed(query)
    with SessionLocal() as db:
        rows = db.execute(
            text("""
                SELECT id, title, chunk_text, 1 - (embedding <=> CAST(:embedding AS vector)) AS score
                FROM knowledge_chunks
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :limit
            """),
            {"embedding": str(vector), "limit": k},
        ).mappings().all()
    return [RetrievedChunk(r["id"], r["title"], r["chunk_text"], float(r["score"])) for r in rows]
