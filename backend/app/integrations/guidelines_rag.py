"""Guideline RAG interface — evidence-grounded answers over clinical guidelines.

Future: embed USPSTF / Ministry of Health / European guideline texts into a vector
store (pgvector / Pinecone) and retrieve relevant passages to ground narration and
screening rationale with citations.

Status: NOT ACTIVE — requires an embedding model + vector store.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class GuidelinePassage:
    source: str
    text: str
    url: str | None = None


class GuidelineRetriever(Protocol):
    def search(self, query: str, k: int = 4) -> list[GuidelinePassage]:
        ...


class PgVectorRetriever:
    """Skeleton: store guideline chunks + embeddings in Postgres (pgvector).

    To implement: enable the `vector` extension, embed chunks with an embedding
    model, and run a cosine-similarity query in search().
    """

    def search(self, query: str, k: int = 4) -> list[GuidelinePassage]:  # noqa: ARG002
        raise NotImplementedError(
            "Guideline RAG requires an embedding model and a pgvector store. Not configured."
        )
