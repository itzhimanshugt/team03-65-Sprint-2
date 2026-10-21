"""Load embedded chunks into the vector store and verify the result."""

import random

import numpy as np

from retrieval.vector_store import to_metadata

UPSERT_BATCH = 500
KEYS = ("page", "source_name", "version", "is_latest")


def build_index(collection, records: list[dict], ids: list[str], vectors: np.ndarray) -> int:
    """Upsert every chunk that has a vector; re-running replaces rows, never duplicates them."""
    by_id = {r["chunk_id"]: r for r in records}
    for start in range(0, len(ids), UPSERT_BATCH):
        batch = ids[start : start + UPSERT_BATCH]
        collection.upsert(
            ids=batch,
            embeddings=vectors[start : start + UPSERT_BATCH].tolist(),
            documents=[by_id[i]["text"] for i in batch],
            metadatas=[to_metadata(by_id[i]) for i in batch],
        )
    return len(ids)


def verify_index(collection, records, ids, vectors, samples: int = 25, seed: int = 0) -> dict:
    """Counts, metadata round-trip and self-retrieval on a random sample."""
    by_id = {r["chunk_id"]: r for r in records}
    rng = random.Random(seed)
    picks = rng.sample(range(len(ids)), min(samples, len(ids)))
    got = collection.get(ids=[ids[i] for i in picks], include=["metadatas", "documents"])
    meta = {i: m for i, m in zip(got["ids"], got["metadatas"], strict=True)}
    docs = dict(zip(got["ids"], got["documents"], strict=True))
    self_hits = 0
    for i in picks:
        hit = collection.query(query_embeddings=[vectors[i].tolist()], n_results=1)
        self_hits += hit["ids"][0][0] == ids[i]
    return {
        "indexed rows = cached vectors": collection.count() == len(ids),
        "every chunk with a vector is indexed": len(collection.get(ids=ids, include=[])["ids"])
        == len(ids),
        "metadata round-trips (page, source, version, latest)": all(
            tuple(meta[ids[i]][k] for k in KEYS) == tuple(by_id[ids[i]][k] for k in KEYS)
            for i in picks
        ),
        "stored text matches the chunk": all(docs[ids[i]] == by_id[ids[i]]["text"] for i in picks),
        f"self-retrieval (sample of {len(picks)})": self_hits == len(picks),
    }
