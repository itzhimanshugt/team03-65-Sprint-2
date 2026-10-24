import pytest

from retrieval.hybrid import bm25_scores, build_where, hybrid_search
from retrieval.vector_store import get_collection


def test_bm25_prefers_rare_matching_terms():
    docs = ["exit load of value fund", "exit load of small cap fund", "riskometer very high"]
    s = bm25_scores("value fund exit load", docs)
    assert s[0] > s[1] > s[2] == 0


def test_build_where():
    assert build_where() == {"is_latest": True}
    assert build_where(latest_only=False) is None
    assert build_where(issuer="HSBC", doc_type=None) == {
        "$and": [{"issuer": "HSBC"}, {"is_latest": True}]
    }


@pytest.fixture
def col(tmp_path, monkeypatch):
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "2")
    c = get_collection(tmp_path)
    c.upsert(
        ids=["small", "value", "old"],
        # "small" is the closest vector, but only "value" names the fund asked about
        embeddings=[[1, 0], [0.8, 0.6], [0.8, 0.6]],
        documents=[
            "Small Cap redemption charge 1%",
            "HSBC Value Fund exit load 1% within 1 year",
            "HSBC Value Fund exit load 2% (old)",
        ],
        metadatas=[
            {"issuer": "HSBC", "is_latest": True},
            {"issuer": "HSBC", "is_latest": True},
            {"issuer": "HSBC", "is_latest": False},
        ],
    )
    return c


def test_keywords_lift_the_named_fund_and_filters_apply(col):
    hits = hybrid_search("HSBC Value Fund exit load", k=2, collection=col, embed=lambda t: [[1, 0]])
    assert hits[0].chunk_id == "value" and "old" not in [h.chunk_id for h in hits]
    assert hits[0].score > hits[1].score
