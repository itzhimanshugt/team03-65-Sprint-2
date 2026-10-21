"""Ask the index a question and see the top-K chunks with scores and citations.

Run: python -m scripts.search "What is the exit load of HSBC Value Fund?"
With no question, runs the demo questions and writes outputs/c23/search_demo.md.
"""

import sys
from pathlib import Path

from retrieval.search import search

DEMO = [
    "What is the exit load of HSBC Value Fund?",
    "Who is the fund manager of HSBC Small Cap Fund?",
    "What is the riskometer level of HSBC Liquid Fund?",
]


def table(question: str) -> list[str]:
    rows = [f"## {question}", "", "| # | Score | Source | Chunk (start) |", "|---|---|---|---|"]
    for n, h in enumerate(search(question), start=1):
        snippet = h.text[:110].replace("\n", " ").replace("|", "/")
        rows.append(f"| {n} | {h.score:.3f} | {h.citation} | {snippet}… |")
    return rows + [""]


if len(sys.argv) > 1:
    print("\n".join(table(" ".join(sys.argv[1:]))))
else:
    lines = ["# C23 — Similarity search, top-5 (latest versions only)", ""]
    for q in DEMO:
        lines += table(q)
    out = Path("outputs/c23/search_demo.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out.read_text(encoding="utf-8"))
