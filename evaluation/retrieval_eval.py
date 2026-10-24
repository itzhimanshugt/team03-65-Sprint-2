"""Retrieval metrics on the labelled eval set: Recall@k, Precision@k, MRR@k (PRD K1, K2).

A question can need several facts (multi-doc slice). Recall@k is the share of those facts with at
least one relevant chunk in the top k; MRR@k uses the rank of the first relevant chunk.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from retrieval.search import Hit

EVAL_SET = Path(__file__).with_name("eval_set.jsonl")


def load_eval_set(path: Path = EVAL_SET, answerable_only: bool = True) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return [r for r in rows if r["expected"] == "answer"] if answerable_only else rows


def fact_ids(row: dict, chunk_text: dict[str, str]) -> list[set[str]]:
    """Relevant chunk ids grouped per fact, so recall counts facts, not chunks."""
    norm = lambda s: "".join(s.split()).lower()  # noqa: E731
    groups = []
    for rule in row["relevant"]:
        ids = {
            cid
            for cid in row["relevant_chunk_ids"]
            if norm(rule["contains"]) in norm(chunk_text.get(cid, ""))
        }
        groups.append(ids)
    return groups


@dataclass
class Scores:
    recall: float
    precision: float
    mrr: float


def score(hits: list[Hit], groups: list[set[str]], k: int) -> Scores:
    top = [h.chunk_id for h in hits[:k]]
    relevant = set().union(*groups)
    found = sum(any(cid in g for cid in top) for g in groups)
    first = next((i for i, cid in enumerate(top, 1) if cid in relevant), None)
    return Scores(
        found / len(groups), sum(c in relevant for c in top) / k, 1 / first if first else 0
    )


def evaluate(
    retrieve: Callable[[str], list[Hit]], rows: list[dict], chunk_text: dict[str, str], k: int
) -> dict[str, Scores]:
    """Mean scores per slice plus 'all'; `retrieve` must return at least k hits per question."""
    per_slice: dict[str, list[Scores]] = {}
    for row in rows:
        s = score(retrieve(row["question"]), fact_ids(row, chunk_text), k)
        per_slice.setdefault(row["slice"], []).append(s)
    per_slice["all"] = [s for slice_ in list(per_slice.values()) for s in slice_]
    return {
        name: Scores(
            *(sum(getattr(s, f) for s in ss) / len(ss) for f in ("recall", "precision", "mrr"))
        )
        for name, ss in per_slice.items()
    }
