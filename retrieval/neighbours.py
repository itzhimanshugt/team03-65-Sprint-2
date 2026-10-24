"""Add the next chunk of the same page after each top hit.

A fact can straddle a chunk boundary: the HSBC Value Fund page (p.39) splits its exit-load
clause, so retrieval found the first half and the model borrowed the "1%" line from another
fund's page. Pulling in the same-page neighbour keeps the whole clause in context.
"""

from retrieval.search import Hit
from retrieval.vector_store import get_collection

EXPAND_TOP = 3  # neighbours for the best 3 hits only, so the 3k-token context budget still fits


def add_neighbours(hits: list[Hit], collection=None, top: int = EXPAND_TOP) -> list[Hit]:
    wanted = {}
    for h in hits[:top]:
        md = h.metadata
        if "doc_id" in md and "chunk_index" in md:
            wanted[h.chunk_id] = f"{md['doc_id']}-{md['chunk_index'] + 1:04d}"
    have = {h.chunk_id for h in hits}
    ids = [n for n in wanted.values() if n not in have]
    if not ids:
        return hits
    got = (collection or get_collection()).get(ids=ids, include=["documents", "metadatas"])
    found = dict(zip(got["ids"], zip(got["documents"], got["metadatas"], strict=True), strict=True))
    out, added = [], set()
    for h in hits:
        out.append(h)
        n = wanted.get(h.chunk_id)
        if n in found and n not in added and n not in have:
            text, md = found[n]
            if md.get("page") == h.metadata.get("page"):  # same page only
                out.append(Hit(n, text, h.score, md))  # inherits the parent's rank and score
                added.add(n)
    return out
