"""Compare answers with and without the VerifAI system prompt.

Run: python -m scripts.compare_system_prompt  (writes outputs/c4/system_prompt_comparison.md)
"""

from pathlib import Path

from app.llm import complete
from app.prompting import build_messages, load_system_prompt

QUESTIONS = [
    "Should my client move all their savings into a small-cap fund?",
    "What is the expense ratio of the ABC Flexi Cap Fund?",
    "Explain what a mutual fund exit load is.",
]

system = load_system_prompt()
lines = ["# C4 — With vs without system prompt", "", "System prompt: `prompts/system.md`", ""]
for q in QUESTIONS:
    lines += [f"## Q: {q}", ""]
    for label, sys_prompt in (("Without system prompt", None), ("With system prompt", system)):
        reply = complete(build_messages(q, sys_prompt), temperature=0.1)
        lines += [f"**{label}:**", "", reply.text.strip(), ""]

out = Path("outputs/c4/system_prompt_comparison.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines), encoding="utf-8")
print(f"Saved {out}")
