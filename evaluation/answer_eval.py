"""End-to-end answer evaluation: K5/K6 automatic, K3/K4 from a manual review sheet (PRD §5)."""

import time
from collections.abc import Callable
from dataclasses import dataclass

from rag.pipeline import Answer


@dataclass
class Run:
    row: dict
    answer: Answer
    seconds: float


def run_eval(rows: list[dict], ask: Callable[[str], Answer]) -> list[Run]:
    runs = []
    for row in rows:
        start = time.perf_counter()
        a = ask(row["question"])
        runs.append(Run(row, a, time.perf_counter() - start))
    return runs


def refusal_metrics(runs: list[Run]) -> dict[str, float]:
    should = [r for r in runs if r.row["expected"] != "answer"]
    answerable = [r for r in runs if r.row["expected"] == "answer"]
    cited = [r for r in answerable if not r.answer.refused]
    return {
        "K5 correct refusal rate": sum(r.answer.refused for r in should) / len(should),
        "K6 false refusal rate": sum(r.answer.refused for r in answerable) / len(answerable),
        "answers with ≥1 resolved citation": sum(bool(r.answer.citations) for r in cited)
        / max(len(cited), 1),
    }


def latency_p95(runs: list[Run]) -> float:
    s = sorted(r.seconds for r in runs)
    return s[min(len(s) - 1, round(0.95 * (len(s) - 1)))]
