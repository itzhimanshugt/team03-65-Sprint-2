import pytest

from retrieval.vector_store import get_collection, to_metadata

REC = {
    "chunk_id": "d1-0000",
    "doc_id": "d1",
    "chunk_index": 0,
    "source_name": "f.pdf",
    "title": "F",
    "doc_type": "factsheet",
    "issuer": "PPFAS",
    "family": "ppfas-factsheet",
    "published_date": "2026-09-30",
    "version": 2,
    "is_latest": True,
    "page": 2,
    "token_count": 12,
    "checksum": "x" * 64,
    "text": "not stored as metadata",
}


def test_metadata_is_flat_and_complete():
    md = to_metadata(REC)
    assert md["page"] == 2 and md["is_latest"] is True and md["published_date"] == "2026-09-30"
    assert "text" not in md and all(isinstance(v, (str, int, float, bool)) for v in md.values())


def test_collection_stores_and_queries_with_cosine(tmp_path, monkeypatch):
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "3")
    col = get_collection(tmp_path)
    col.upsert(
        ids=["a", "b"],
        embeddings=[[1, 0, 0], [0, 1, 0]],
        documents=["exit load", "NAV"],
        metadatas=[to_metadata(REC), {**to_metadata(REC), "is_latest": False}],
    )
    hit = col.query(query_embeddings=[[0.9, 0.1, 0]], n_results=1)
    assert hit["ids"] == [["a"]] and hit["distances"][0][0] < 0.01  # distance = 1 - cosine
    latest = col.query(query_embeddings=[[0, 1, 0]], n_results=2, where={"is_latest": True})
    assert latest["ids"] == [["a"]]
    assert get_collection(tmp_path).count() == 2  # reopening is idempotent and persistent


def test_dimension_mismatch_is_refused(tmp_path, monkeypatch):
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "3")
    get_collection(tmp_path)
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "768")
    with pytest.raises(ValueError, match="Rebuild"):
        get_collection(tmp_path)
