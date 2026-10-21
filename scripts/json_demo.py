"""Structured JSON answers over a small hand-written context.

Run: python -m scripts.json_demo  (writes outputs/c8/json_demo.md)
"""

from pathlib import Path

from app.prompting import load_system_prompt
from app.structured import Answer, complete_json

CONTEXT = """[1] chunk_id=abc-fs-0003 source="ABC Flexi Cap Fund Factsheet – Sep 2026.pdf" page=4
Exit load: 1% if redeemed within 365 days from allotment; nil after 365 days.

[2] chunk_id=abc-fs-0004 source="ABC Flexi Cap Fund Factsheet – Sep 2026.pdf" page=4
Total expense ratio (regular plan): 1.72%. Total expense ratio (direct plan): 0.68%."""

QUESTIONS = [
    "What is the exit load and the direct-plan expense ratio of ABC Flexi Cap Fund?",
    "Who is the fund manager of ABC Flexi Cap Fund?",
]

lines = [
    "# C8 — Structured JSON output",
    "",
    "Context given to the model:",
    "",
    "```",
    CONTEXT,
    "```",
]
for q in QUESTIONS:
    messages = [
        {"role": "system", "content": load_system_prompt()},
        {"role": "user", "content": f"Context:\n{CONTEXT}\n\nQuestion: {q}\nCite sources as [n]."},
    ]
    result = complete_json(messages, Answer)
    lines += ["", f"## Q: {q}", "", "```json", result.model_dump_json(indent=2), "```"]

out = Path("outputs/c8/json_demo.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines), encoding="utf-8")
print(out.read_text(encoding="utf-8"))
