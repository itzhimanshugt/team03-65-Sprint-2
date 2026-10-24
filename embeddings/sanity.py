"""Sanity checks that catch embedding bugs early: meaning checks and vector-store checks."""

import numpy as np

from embeddings.similarity import cosine

# (anchor, should be close, should be far)
TRIPLETS = [
    (
        "exit load",
        "redemption charge for selling units early",
        "the cricket match was stopped by rain",
    ),
    ("NAV of a mutual fund", "net asset value per unit", "add two cups of flour to the batter"),
    ("riskometer", "risk level label shown on a scheme", "the train leaves platform four at noon"),
    (
        "expense ratio",
        "annual fee charged by the fund for management costs",
        "the weather is sunny today",
    ),
    ("SID", "scheme information document of a mutual fund", "my phone battery is almost empty"),
    (
        "SEBI",
        "Securities and Exchange Board of India, the market regulator",
        "a recipe for chocolate cake",
    ),
]


def meaning_checks(embed, triplets=TRIPLETS) -> list[dict]:
    """Embed all phrases in one call; each anchor must be closer to its synonym than its control."""
    flat = [p for t in triplets for p in t]
    vecs = embed(flat)
    rows = []
    for i, (a, near, far) in enumerate(triplets):
        va, vn, vf = vecs[3 * i : 3 * i + 3]
        sn, sf = cosine(va, vn), cosine(va, vf)
        rows.append(
            {"anchor": a, "near": near, "far": far, "near_sim": sn, "far_sim": sf, "ok": sn > sf}
        )
    return rows


def store_checks(
    vectors: np.ndarray, ids: list[str], records: list[dict], dims: int
) -> dict[str, bool]:
    """Structural checks on the saved vectors; no API calls."""
    norms = np.linalg.norm(vectors, axis=1)
    by_id = {r["chunk_id"]: r["text"] for r in records}
    first_for_text, dup_ok = {}, True
    for row, cid in enumerate(ids):
        text = by_id.get(cid)
        if text in first_for_text:
            dup_ok &= bool(cosine(vectors[first_for_text[text]], vectors[row]) > 0.999)
        else:
            first_for_text[text] = row
    return {
        "one vector per chunk": len(ids) == len(set(ids)) == len(records) == len(vectors),
        f"every vector has {dims} dimensions": vectors.shape[1] == dims,
        "no NaN or infinite values": bool(np.isfinite(vectors).all()),
        "all vectors unit-length": bool(np.allclose(norms, 1.0, atol=1e-3)),
        "identical texts get identical vectors": dup_ok,
    }
