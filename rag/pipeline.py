"""End-to-end RAG flow: retrieve → re-rank → evidence gate → assemble context → generate.

Each stage is a plain function passed in, so later concepts swap one stage without touching the
rest (hybrid retrieval C24, re-ranking C26, refusals C32, follow-up condensing C33).
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from app.config import get_settings
from app.llm import complete
from app.prompting import build_messages, load_system_prompt, render_prompt
from rag.context import assemble_context
from retrieval.search import Hit, search

Retrieve = Callable[[str], list[Hit]]
Rerank = Callable[[str, list[Hit]], list[Hit]]
Generate = Callable[[list[dict]], str]

NO_EVIDENCE = "I couldn't find this in the approved documents."


@dataclass
class Answer:
    text: str
    sources: list[Hit] = field(default_factory=list)  # numbered [1], [2], … in the prompt
    refused: bool = False


def default_generate(messages: list[dict]) -> str:
    return complete(messages).text


def answer(
    question: str,
    retrieve: Retrieve = search,
    rerank: Rerank = lambda _q, hits: hits,
    generate: Generate = default_generate,
    threshold: float | None = None,
) -> Answer:
    threshold = get_settings().refusal_threshold if threshold is None else threshold
    hits = rerank(question, retrieve(question))
    if not hits or max(h.score for h in hits) < threshold:
        return Answer(NO_EVIDENCE, refused=True)  # weak evidence: refuse, never call the LLM
    context, used = assemble_context(hits)
    messages = build_messages(
        render_prompt("answer", context=context, question=question), load_system_prompt()
    )
    return Answer(generate(messages), sources=used)
