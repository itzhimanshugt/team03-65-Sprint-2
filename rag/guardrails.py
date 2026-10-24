"""Guardrails that run before the LLM: weak-evidence refusal and advice-seeking detection.

Copy matches the Mock UX states S2c (not enough evidence) and S2d (advice request).
"""

import re

from retrieval.search import Hit

NO_EVIDENCE = (
    "I couldn't find this in the approved documents. "
    "So I won't guess. Try rephrasing or check your filters."
)
ADVICE_NOTICE = (
    "I can share facts, not investment advice. "
    "Here is what the approved documents say about this fund."
)

ADVICE = re.compile(
    r"\b(should|shall|must|would you)\b.{0,40}\b(buy|sell|switch|invest|redeem|exit|move|hold)\b"
    r"|\b(recommend|suggest|advise)\b"
    r"|\b(best|better|good|safe)\b.{0,20}\b(fund|investment|option|time)\b",
    re.IGNORECASE,
)


def is_advice_seeking(question: str) -> bool:
    return bool(ADVICE.search(question))


def has_evidence(hits: list[Hit], threshold: float) -> bool:
    return bool(hits) and max(h.score for h in hits) >= threshold
