"""Re-rank a wide candidate pool (top-20) down to the final top-5 with a lexical-overlap scorer.

Free and instant: no extra API call. Each chunk gets its cosine score plus a bonus for the share of
the question's content words it contains, with a stronger weight on the *leading* words of the
chunk (fund pages start with the fund name, so "HSBC Value Fund" outranks a page that only
mentions it). `Hit.score` stays the cosine score, so the evidence gate is unchanged.
"""

from retrieval.hybrid import tokenize
from retrieval.search import Hit

STOP = set(
    "a an and are as at be by for from has have how in is it its of on or the to was what"
    " when which who why with does do".split()
)
HEAD_TOKENS = 12  # roughly the title line of a chunk


def content_words(question: str) -> set[str]:
    return {t for t in tokenize(question) if t not in STOP}


def rerank_score(question: str, hit: Hit, w_body: float = 0.2, w_head: float = 0.2) -> float:
    words = content_words(question)
    if not words:
        return hit.score
    tokens = tokenize(hit.text)
    body, head = set(tokens), set(tokens[:HEAD_TOKENS])
    return (
        hit.score
        + w_body * len(words & body) / len(words)
        + w_head * len(words & head) / len(words)
    )


def rerank(question: str, hits: list[Hit], k: int = 5) -> list[Hit]:
    return sorted(hits, key=lambda h: rerank_score(question, h), reverse=True)[:k]
