from evaluation.retrieval_eval import EVAL_SET, evaluate, load_eval_set, score
from retrieval.search import Hit


def hits(*ids):
    return [Hit(i, "", 0.5, {}) for i in ids]


def test_scores_count_facts_ranks_and_precision():
    s = score(hits("x", "a1", "b1"), [{"a1", "a2"}, {"b1"}], k=3)
    assert (s.recall, round(s.precision, 3), s.mrr) == (1.0, 0.667, 0.5)
    s = score(hits("x", "a1", "b1"), [{"a1"}, {"b1"}], k=2)
    assert (s.recall, s.mrr) == (0.5, 0.5)
    assert score(hits("x"), [{"a"}], k=1).mrr == 0


def test_evaluate_averages_per_slice():
    rows = [
        {
            "slice": "factual",
            "question": "q1",
            "relevant": [{"contains": "fee"}],
            "relevant_chunk_ids": ["a"],
        },
        {
            "slice": "factual",
            "question": "q2",
            "relevant": [{"contains": "fee"}],
            "relevant_chunk_ids": ["b"],
        },
    ]
    out = evaluate(lambda q: hits("a"), rows, {"a": "fee 1%", "b": "fee 2%"}, k=1)
    assert out["factual"].recall == 0.5 and out["all"].mrr == 0.5


def test_committed_eval_set_matches_prd_slices():
    rows = load_eval_set(EVAL_SET, answerable_only=False)
    count = {s: sum(r["slice"] == s for r in rows) for s in {r["slice"] for r in rows}}
    assert count == {"factual": 25, "multi_doc": 5, "unanswerable": 6, "advice": 4}
    assert all(r["relevant_chunk_ids"] for r in rows if r["expected"] == "answer")
