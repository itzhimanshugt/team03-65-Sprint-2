from retrieval.reranker import rerank
from retrieval.search import Hit


def test_named_fund_page_moves_to_top():
    other = Hit("other", "Load Structure Exit Load: 1% within 1 year.", 0.80, {})
    named = Hit("named", "HSBC Value Fund Type of Scheme ... Exit Load: 1%.", 0.75, {})
    noise = Hit("noise", "Unrelated portfolio holdings table.", 0.79, {})
    out = rerank("What is the exit load of HSBC Value Fund?", [other, noise, named], k=2)
    assert [h.chunk_id for h in out] == ["named", "other"]
    assert out[0].score == 0.75  # cosine kept for the evidence gate
