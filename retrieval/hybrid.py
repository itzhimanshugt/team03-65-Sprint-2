"""Hybrid search: BM25 keyword scores + vector similarity, fused by reciprocal rank (RRF).

Vector search knows "this is about exit loads"; BM25 knows "this chunk says HSBC Value Fund".
Metadata filters (issuer, doc_type, latest version...) narrow both sides before ranking.
"""

import math
import re
from collections import Counter

from app.config import get_settings
from embeddings.embedder import embed_cached
from retrieval.search import LATEST_ONLY, Hit, search
from retrieval.vector_store import get_collection

RRF_K = 60  # standard RRF constant: damps the gap between rank 1 and rank 2


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def bm25_scores(query: str, docs: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    """Okapi BM25 score of every doc for `query`."""
    toks = [tokenize(d) for d in docs]
    n, avg = len(docs), sum(map(len, toks)) / max(len(docs), 1)
    df = Counter(t for ts in toks for t in set(ts))
    scores = []
    for ts in toks:
        tf, s = Counter(ts), 0.0
        for q in set(tokenize(query)):
            if q in tf:
                idf = math.log(1 + (n - df[q] + 0.5) / (df[q] + 0.5))
                s += idf * tf[q] * (k1 + 1) / (tf[q] + k1 * (1 - b + b * len(ts) / avg))
        scores.append(s)
    return scores


def build_where(latest_only: bool = True, **filters) -> dict | None:
    """{"issuer": "HSBC", "doc_type": "factsheet"} -> a Chroma where clause (None if empty)."""
    conds = [{k: v} for k, v in filters.items() if v is not None]
    if latest_only:
        conds.append(LATEST_ONLY)
    return None if not conds else conds[0] if len(conds) == 1 else {"$and": conds}


def hybrid_search(
    question: str,
    k: int | None = None,
    where: dict | None = LATEST_ONLY,
    collection=None,
    embed=embed_cached,
    pool: int = 30,
) -> list[Hit]:
    """Top-`k` chunks by RRF of the vector top-`pool` and the BM25 top-`pool`."""
    collection = collection or get_collection()
    k = k or get_settings().top_k
    vec = search(question, k=pool, where=where, collection=collection, embed=embed)
    got = collection.get(where=where or None, include=["documents", "metadatas"])
    bm = bm25_scores(question, got["documents"])
    kw = sorted(range(len(bm)), key=lambda i: -bm[i])[:pool]
    kw = [i for i in kw if bm[i] > 0]

    fused, hits = Counter(), {h.chunk_id: h for h in vec}
    for rank, h in enumerate(vec):
        fused[h.chunk_id] += 1 / (RRF_K + rank + 1)
    for rank, i in enumerate(kw):
        cid = got["ids"][i]
        fused[cid] += 1 / (RRF_K + rank + 1)
        hits.setdefault(cid, Hit(cid, got["documents"][i], 0.0, got["metadatas"][i]))
    return [
        Hit(cid, hits[cid].text, score, hits[cid].metadata) for cid, score in fused.most_common(k)
    ]
