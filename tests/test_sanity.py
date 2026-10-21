import numpy as np

from embeddings.sanity import meaning_checks, store_checks


def test_meaning_checks_flag_a_broken_embedder():
    # A broken embedder that returns the same vector for everything cannot tell near from far.
    rows = meaning_checks(lambda texts: [[1.0, 0.0]] * len(texts))
    assert not any(r["ok"] for r in rows)


def test_meaning_checks_pass_for_a_good_embedder():
    def embed(texts):  # anchor and its synonym share a direction; controls are orthogonal
        out = []
        for i in range(0, len(texts), 3):
            k = i // 3
            base = np.eye(len(texts) // 3 + 1)[k]
            out += [base, base * 0.9 + 0.1, np.eye(len(texts) // 3 + 1)[-1]]
        return out

    assert all(r["ok"] for r in meaning_checks(embed))


def test_store_checks_catch_problems():
    recs = [{"chunk_id": "a", "text": "x"}, {"chunk_id": "b", "text": "x"}]
    good = np.array([[1.0, 0.0], [1.0, 0.0]])
    assert all(store_checks(good, ["a", "b"], recs, 2).values())
    bad = np.array([[np.nan, 0.0], [0.5, 0.5]])
    result = store_checks(bad, ["a", "b"], recs, 2)
    assert not result["no NaN or infinite values"] and not result["all vectors unit-length"]
    assert not store_checks(good, ["a"], recs, 2)["one vector per chunk"]
