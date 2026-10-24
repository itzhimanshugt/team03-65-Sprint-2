"""Refusal handling live: unanswerable, advice-seeking and answerable questions side by side.

Run: python -m scripts.guardrail_demo  (writes outputs/c32/guardrails.md)
"""

from pathlib import Path

from rag.pipeline import answer

QUESTIONS = [
    "What is the exit load of SBI Bluechip Fund?",
    "Has SEBI approved a Bitcoin ETF?",
    "Should my client switch from HSBC Value Fund to HSBC Small Cap Fund?",
    "What is the benchmark of HSBC Midcap Fund?",
]
md = [
    "# C32 — Guardrails & refusals",
    "",
    "| Question | Outcome | Response (start) |",
    "|---|---|---|",
]
for q in QUESTIONS:
    a = answer(q)
    md.append(f"| {q} | {a.refusal or 'answered'} | {a.text.strip()[:160].replace(chr(10), ' ')} |")
out = Path("outputs/c32/guardrails.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
