import numpy as np

from retrieval.indexer import build_index, verify_index
from retrieval.vector_store import get_collection


def make(n):
    recs = [
        {
            "chunk_id": f"d1-{i:04d}",
            "doc_id": "d1",
            "chunk_index": i,
            "source_name": "f.pdf",
            "title": "F",
            "doc_type": "factsheet",
            "issuer": "I",
            "family": "f",
            "published_date": "2026-09-30",
            "version": 1,
            "is_latest": True,
            "page": i + 1,
            "token_count": 5,
            "checksum": "c" * 64,
            "text": f"chunk {i}",
        }
        for i in range(n)
    ]
    vecs = np.eye(n, dtype=np.float32)  # orthogonal unit vectors: each is its own nearest neighbour
    return recs, [r["chunk_id"] for r in recs], vecs


def test_build_and_verify(tmp_path, monkeypatch):
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "6")
    recs, ids, vecs = make(6)
    col = get_collection(tmp_path)
    assert build_index(col, recs, ids, vecs) == 6
    assert all(verify_index(col, recs, ids, vecs, samples=6).values())


def test_rebuild_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "4")
    recs, ids, vecs = make(4)
    col = get_collection(tmp_path)
    build_index(col, recs, ids, vecs)
    build_index(col, recs, ids, vecs)
    assert col.count() == 4
