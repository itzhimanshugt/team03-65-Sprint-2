"""Multi-turn chat that trims history to a token budget.

Run: python -m scripts.history_demo  (writes outputs/c6/history_demo.md)
"""

from pathlib import Path

from app.history import ChatHistory
from app.llm import complete
from app.tokens import count_message_tokens

QUESTIONS = [
    "What does NAV mean for a mutual fund?",
    "How is it calculated?",
    "What is an exit load?",
    "And how is that different from an expense ratio?",
    "Which of the two is charged every year?",
    "Summarise our conversation in one line.",
]

# A tutor prompt (no documents yet) so follow-ups like "How is it calculated?" get real answers.
SYSTEM = "You are a concise finance tutor. Answer in at most 2 sentences."
history = ChatHistory(system_prompt=SYSTEM, max_turns=4, token_budget=300)
rows = []
for q in QUESTIONS:
    messages = history.messages(q)
    reply = complete(messages, temperature=0.1, max_tokens=300)
    rows.append(
        (
            q,
            len(history.turns),
            history.dropped_turns(q),
            count_message_tokens(messages),
            reply.prompt_tokens,
            reply.text.strip().replace("\n", " ")[:140],
        )
    )
    history.add_turn(q, reply.text)

lines = [
    "# C6 — History management (max 4 turns, 300-token budget)",
    "",
    "| Question | Turns stored | Turns dropped | Est. tokens | Actual input | Answer |",
    "|---|---|---|---|---|---|",
    *[f"| {q} | {t} | {d} | {e} | {a} | {ans} |" for q, t, d, e, a, ans in rows],
]
out = Path("outputs/c6/history_demo.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines), encoding="utf-8")
print(out.read_text(encoding="utf-8"))
