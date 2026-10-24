"""Vector-only vs hybrid (BM25 + vector) top-5 on the demo questions.

Run: python -m scripts.hybrid_demo  (writes outputs/c24/hybrid_demo.md)
"""

from pathlib import Path

from retrieval.hybrid import build_where, hybrid_search
from retrieval.search import search

DEMO = [
    "What is the exit load of HSBC Value Fund?",
    "Who is the fund manager of HSBC Small Cap Fund?",
    "What is the riskometer level of HSBC Liquid Fund?",
]
# Metadata filter: one AMC's factsheets, latest versions only.
where = build_where(issuer="HSBC Mutual Fund", doc_type="factsheet")


def cell(hit) -> str:
    return f"{hit.citation} — {hit.text[:60].replace(chr(10), ' ').replace('|', '/')}…"


lines = [f"# C24 — Vector-only vs hybrid search (filter: `{where}`)", ""]
for q in DEMO:
    lines += [f"## {q}", "", "| # | Vector-only | Hybrid (BM25 + vector, RRF) |", "|---|---|---|"]
    pairs = zip(search(q, where=where), hybrid_search(q, where=where), strict=True)
    lines += [f"| {n} | {cell(v)} | {cell(h)} |" for n, (v, h) in enumerate(pairs, start=1)]
    lines.append("")
out = Path("outputs/c24/hybrid_demo.md")
out.write_text("\n".join(lines), encoding="utf-8")
print(out.read_text(encoding="utf-8"))
