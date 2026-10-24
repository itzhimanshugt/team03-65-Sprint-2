"""Turn text into embedding vectors with an OpenAI-compatible embeddings API."""

import json
import math
from pathlib import Path

from openai import OpenAI

from app.config import get_settings
from app.llm import get_client


class EmbeddingError(RuntimeError):
    pass


def embed_texts(texts: list[str], client: OpenAI | None = None) -> list[list[float]]:
    """Return one vector per text, in input order, each with the configured dimension."""
    if not texts:
        return []
    settings = get_settings()
    client = client or get_client(settings)
    response = client.embeddings.create(
        model=settings.embedding_model, input=texts, dimensions=settings.embedding_dimensions
    )
    data = response.data
    # OpenAI sets `index`; Gemini's compatible endpoint leaves it None and keeps input order.
    if all(d.index is not None for d in data):
        data = sorted(data, key=lambda d: d.index)
    vectors = [d.embedding for d in data]
    if len(vectors) != len(texts):
        raise EmbeddingError(f"Expected {len(texts)} vectors, got {len(vectors)}")
    bad = {len(v) for v in vectors} - {settings.embedding_dimensions}
    if bad:
        raise EmbeddingError(f"Expected {settings.embedding_dimensions} dimensions, got {bad}")
    # Truncated Gemini embeddings (< 3072 dims) are not unit-length; normalise so cosine,
    # dot product and Euclidean distance all rank the same way.
    return [[x / n for x in v] if (n := math.sqrt(sum(x * x for x in v))) else v for v in vectors]


QUERY_CACHE = Path("data/processed/query_cache.json")


def embed_cached(
    texts: list[str], path: Path = QUERY_CACHE, embed=embed_texts
) -> list[list[float]]:
    """embed_texts with a disk cache keyed by model, dimension and text.

    Questions repeat across demos and eval runs; on the free tier every embedding is a request.
    """
    settings = get_settings()
    cache = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    key = [f"{settings.embedding_model}|{settings.embedding_dimensions}|{t}" for t in texts]
    missing = [t for t, k in zip(texts, key, strict=True) if k not in cache]
    if missing:
        for t, v in zip(missing, embed(missing), strict=True):
            cache[f"{settings.embedding_model}|{settings.embedding_dimensions}|{t}"] = v
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cache), encoding="utf-8")
    return [cache[k] for k in key]
