import pytest

from retrieval.search import search
from retrieval.vector_store import get_collection

VECS = {"exit load": [1, 0, 0], "expense ratio": [0, 1, 0], "riskometer": [0, 0, 1]}


@pytest.fixture
def col(tmp_path, monkeypatch):
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "3")
    c = get_collection(tmp_path)
    c.upsert(
        ids=["new", "old", "er", "rk"],
        embeddings=[[1, 0, 0], [0.99, 0.14, 0], [0.1, 1, 0], [0, 0, 1]],
        documents=["exit load 1% (Sep)", "exit load 2% (Aug)", "TER 0.6%", "Very High risk"],
        metadatas=[
            {"source_name": "fs-sep.pdf", "page": 2, "is_latest": True},
            {"source_name": "fs-aug.pdf", "page": 2, "is_latest": False},
            {"source_name": "fs-sep.pdf", "page": 3, "is_latest": True},
            {"source_name": "kim.pdf", "page": 1, "is_latest": True},
        ],
    )
    return c


def fake_embed(texts):
    return [VECS[t] for t in texts]


def test_top_k_most_similar_first_with_citation(col):
    hits = search("exit load", k=2, collection=col, embed=fake_embed)
    assert [h.chunk_id for h in hits] == ["new", "er"]
    assert hits[0].score == pytest.approx(1.0, abs=1e-3) and hits[0].score > hits[1].score
    assert hits[0].citation == "fs-sep.pdf · p.2"


def test_superseded_versions_excluded_unless_asked(col):
    assert "old" not in [
        h.chunk_id for h in search("exit load", k=3, collection=col, embed=fake_embed)
    ]
    all_versions = search("exit load", k=2, where=None, collection=col, embed=fake_embed)
    assert [h.chunk_id for h in all_versions] == ["new", "old"]
