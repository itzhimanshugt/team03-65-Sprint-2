"""Same questions, two ways: the bare LLM (no documents) versus the grounded RAG pipeline.

Run: python -m scripts.grounded_vs_ungrounded  (writes outputs/c30/grounded_vs_ungrounded.md)
"""

from pathlib import Path

from app.llm import complete
from app.prompting import build_messages
from rag.pipeline import answer

QUESTIONS = [
    (
        "What is the riskometer level of HSBC Liquid Fund?",
        "Low to Moderate (Aug 2026 factsheet, p.112)",
    ),
    ("What is the exit load of Parag Parikh Liquid Fund on day 1?", "0.0070% (KIM, p.13)"),
    (
        "How soon does compliance upload a new monthly factsheet?",
        "Within 3 working days (firm FAQ)",
    ),
]
md = [
    "# C30 — Grounded vs ungrounded answers",
    "",
    "Ungrounded = the same model with no documents, asked directly. "
    "Grounded = the full pipeline (retrieve → re-rank → numbered context → answer only from it).",
    "",
]
for q, truth in QUESTIONS:
    bare = complete(build_messages(q)).text.strip()
    rag = answer(q)
    cites = ", ".join(f"[{c.n}] {c.source_name} p.{c.page}" for c in rag.citations) or "—"
    md += [
        f"## {q}",
        "",
        f"**Correct (from the corpus):** {truth}",
        "",
        f"**Ungrounded:** {bare}",
        "",
        f"**Grounded:** {rag.text.strip()}",
        "",
        f"**Grounded citations:** {cites}",
        "",
    ]
out = Path("outputs/c30/grounded_vs_ungrounded.md")
out.write_text("\n".join(md), encoding="utf-8")
print(out.read_text(encoding="utf-8"))
