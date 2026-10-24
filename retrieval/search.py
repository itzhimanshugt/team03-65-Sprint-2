"""Semantic top-K search: embed the question, return the nearest chunks with their citations."""

from dataclasses import dataclass

from app.config import get_settings
from embeddings.embedder import embed_cached
from retrieval.vector_store import get_collection

LATEST_ONLY = {"is_latest": True}  # PRD FR-9: superseded versions are excluded by default


@dataclass
class Hit:
    chunk_id: str
    text: str
    score: float  # cosine similarity (1 - Chroma's cosine distance)
    metadata: dict

    @property
    def citation(self) -> str:
        return f"{self.metadata.get('source_name')} · p.{self.metadata.get('page')}"


def search(
    question: str,
    k: int | None = None,
    where: dict | None = LATEST_ONLY,
    collection=None,
    embed=embed_cached,
) -> list[Hit]:
    """Top-`k` chunks for `question`, most similar first; where=None searches every version."""
    collection = collection or get_collection()
    k = k or get_settings().top_k
    (qv,) = embed([question])
    res = collection.query(
        query_embeddings=[qv],
        n_results=k,
        where=where or None,
        include=["documents", "metadatas", "distances"],
    )
    return [
        Hit(cid, doc, 1 - dist, md)
        for cid, doc, md, dist in zip(
            res["ids"][0],
            res["documents"][0],
            res["metadatas"][0],
            res["distances"][0],
            strict=True,
        )
    ]
