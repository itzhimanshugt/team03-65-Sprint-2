"""Answer the demo questions and show each [n] resolved to its document and page.

Run: python -m scripts.citation_demo  (writes outputs/c31/citations.md; 4 embedding + 4 LLM calls)
"""

from pathlib import Path

from rag.pipeline import answer

QUESTIONS = [
    "What is the exit load of HSBC Value Fund?",
    "Who are the fund managers of HSBC Small Cap Fund?",
    "What is the riskometer level of HSBC Liquid Fund?",
    "What is the benchmark of HSBC Value Fund?",
]

md = ["# C31 — Source citations, resolved", ""]
for q in QUESTIONS:
    a = answer(q)
    md += [
        f"## {q}",
        "",
        a.text.strip(),
        "",
        "| Marker | Document | Page | Chunk |",
        "|---|---|---|---|",
    ]
    md += [f"| [{c.n}] | {c.title} | {c.page} | `{c.chunk_id}` |" for c in a.citations]
    resolved = "all resolve" if a.citations else "NONE resolved"
    md += ["", f"_{len(a.citations)} cited of {len(a.sources)} shown, {resolved}._", ""]
out = Path("outputs/c31/citations.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(md), encoding="utf-8")
print(out.read_text(encoding="utf-8"))
