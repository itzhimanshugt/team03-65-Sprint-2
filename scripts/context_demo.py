"""Show the augmented prompt the LLM receives: system rules + numbered, cited context + question.

Run: python -m scripts.context_demo  (writes outputs/c29/prompt_demo.md; one embedding call, no LLM)
"""

from pathlib import Path

from app.prompting import load_system_prompt, render_prompt
from app.tokens import count_tokens
from rag.context import assemble_context
from retrieval.search import search

QUESTION = "What is the exit load of HSBC Value Fund?"
context, used = assemble_context(search(QUESTION))
user = render_prompt("answer", context=context, question=QUESTION)
system = load_system_prompt()
md = [
    "# C29 — Context injection: the augmented prompt",
    "",
    f"Question: **{QUESTION}** · {len(used)} sources · context {count_tokens(context)} tokens "
    f"(budget 3,000) · full prompt {count_tokens(system) + count_tokens(user)} tokens",
    "",
    "## System message",
    "",
    "```text",
    system,
    "```",
    "",
    "## User message (retrieved context injected)",
    "",
    "```text",
    user,
    "```",
]
out = Path("outputs/c29/prompt_demo.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
