"""Conversational RAG: rewrite a follow-up into a standalone query before retrieval.

"and its expense ratio?" means nothing to a vector index; "What is the expense ratio of HSBC
Value Fund?" does. Only the last 4 turns are used (PRD §6.2).
"""

from app.prompting import build_messages, render_prompt
from rag.pipeline import Answer, Generate, answer, default_generate

MAX_TURNS = 4
ANSWER_CHARS = 300  # earlier answers are trimmed: the condenser needs the topic, not every fact


def condense(
    question: str, turns: list[tuple[str, str]], generate: Generate = default_generate
) -> str:
    if not turns:
        return question  # first question: nothing to resolve, no LLM call
    history = "\n".join(f"User: {q}\nAssistant: {a[:ANSWER_CHARS]}" for q, a in turns[-MAX_TURNS:])
    standalone = generate(
        build_messages(render_prompt("condense", history=history, question=question))
    )
    return standalone.strip() or question


class Conversation:
    """Keeps (question, answer) turns and answers each follow-up as a standalone question."""

    def __init__(self, generate: Generate = default_generate, **answer_kwargs):
        self.turns: list[tuple[str, str]] = []
        self.generate = generate
        self.answer_kwargs = answer_kwargs

    def ask(self, question: str) -> tuple[str, Answer]:
        standalone = condense(question, self.turns, self.generate)
        result = answer(standalone, generate=self.generate, **self.answer_kwargs)
        self.turns.append((question, result.text))
        return standalone, result
