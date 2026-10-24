"""A follow-up question resolved through the conversation (C33).

Run: python -m scripts.followup_demo  (writes outputs/c33/followup.md)
"""

from pathlib import Path

from rag.conversation import Conversation

chat = Conversation()
md = ["# C33 — Follow-up questions", ""]
for q in ("What is the exit load of HSBC Value Fund?", "and its benchmark?"):
    standalone, a = chat.ask(q)
    cites = ", ".join(f"[{c.n}] {c.source_name} p.{c.page}" for c in a.citations)
    md += [
        f"**User:** {q}",
        "",
        f"**Standalone query:** {standalone}",
        "",
        f"**Answer:** {a.text.strip()}",
        "",
        f"**Cited:** {cites}",
        "",
    ]
out = Path("outputs/c33/followup.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(md), encoding="utf-8")
print("\n".join(md))
