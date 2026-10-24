"""Five grounded Q&As through the full pipeline, saved with the context each answer used.

Run: python -m scripts.answer_demo  (writes outputs/c30/answers.md; 5 embedding + ≤5 LLM calls)
"""

from pathlib import Path

from rag.pipeline import answer

QUESTIONS = [
    "What is the exit load of HSBC Value Fund?",
    "Who are the fund managers of HSBC Small Cap Fund?",
    "What is the riskometer level of HSBC Liquid Fund?",
    "What is the benchmark of HSBC Value Fund?",
    "Should my client switch from HSBC Value Fund to HSBC Small Cap Fund?",
]
md = ["# C30 — Grounded answers (5 sample questions)", ""]
for q in QUESTIONS:
    a = answer(q)
    md += [f"## {q}", "", f"**Answer:** {a.text.strip()}", ""]
    if a.refused:
        md += ["_Refused before the LLM: no chunk passed the evidence threshold._", ""]
    md += ["<details><summary>Context used</summary>", ""]
    md += [f"- [{n}] {h.citation} (score {h.score:.3f})" for n, h in enumerate(a.sources, 1)]
    md += ["", "</details>", ""]
out = Path("outputs/c30/answers.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(md), encoding="utf-8")
print(out.read_text(encoding="utf-8"))
