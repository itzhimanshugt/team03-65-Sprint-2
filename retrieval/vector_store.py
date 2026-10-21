"""Persistent ChromaDB collection holding chunk vectors, text and metadata (PRD §6.2-6.3)."""

import logging
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings

COLLECTION = "verifai_chunks"
# chromadb 1.0 + posthog 6 log a harmless error on every call; telemetry is off anyway.
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)

# Metadata stored with each vector: everything needed to cite and filter, nothing else.
METADATA_FIELDS = (
    "doc_id",
    "chunk_index",
    "source_name",
    "title",
    "doc_type",
    "issuer",
    "family",
    "published_date",
    "version",
    "is_latest",
    "page",
    "token_count",
    "checksum",
)


def get_collection(path: str | Path | None = None, name: str = COLLECTION):
    """Open (or create) the collection; refuse to mix vectors of a different dimension."""
    s = get_settings()
    client = chromadb.PersistentClient(
        path=str(path or s.chroma_path), settings=ChromaSettings(anonymized_telemetry=False)
    )
    col = client.get_or_create_collection(
        name,
        metadata={"hnsw:space": "cosine", "dimensions": s.embedding_dimensions},
        embedding_function=None,  # we always pass our own vectors (C17)
    )
    if col.metadata.get("dimensions") != s.embedding_dimensions:
        raise ValueError(
            f"Collection holds {col.metadata.get('dimensions')}-dim vectors, "
            f"settings say {s.embedding_dimensions}. Rebuild the index."
        )
    return col


def to_metadata(record: dict) -> dict:
    """Flatten a ChunkRecord dict to the scalar types Chroma accepts (dates become ISO strings)."""
    return {
        k: (v if isinstance(v, (str, int, float, bool)) else str(v))
        for k in METADATA_FIELDS
        if (v := record.get(k)) is not None
    }
