"""End-to-end RAG flow: retrieve → re-rank → evidence gate → assemble context → generate.

Each stage is a plain function passed in, so later concepts swap one stage without touching the
rest (hybrid retrieval C24, re-ranking C26, refusals C32, follow-up condensing C33).
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from app.config import get_settings
from app.llm import complete
from app.prompting import build_messages, load_system_prompt, render_prompt
from rag.citations import Citation, resolve_citations
from rag.context import assemble_context
from rag.guardrails import ADVICE_NOTICE, NO_EVIDENCE, has_evidence, is_advice_seeking
from retrieval.reranker import rerank as lexical_rerank
from retrieval.search import Hit, search

Retrieve = Callable[[str], list[Hit]]
Rerank = Callable[[str, list[Hit]], list[Hit]]
Generate = Callable[[list[dict]], str]


@dataclass
class Answer:
    text: str
    sources: list[Hit] = field(default_factory=list)  # numbered [1], [2], … in the prompt
    refusal: str | None = None  # "no_evidence" (S2c) or "advice" (S2d)
    citations: list[Citation] = field(default_factory=list)  # only markers that resolve

    @property
    def refused(self) -> bool:
        return self.refusal is not None


def default_generate(messages: list[dict]) -> str:
    return complete(messages).text


def answer(
    question: str,
    retrieve: Retrieve = lambda q: search(q, k=20),  # wide pool, cut to 5 by the re-ranker
    rerank: Rerank = lexical_rerank,
    generate: Generate = default_generate,
    threshold: float | None = None,
) -> Answer:
    threshold = get_settings().refusal_threshold if threshold is None else threshold
    advice = is_advice_seeking(question)
    hits = rerank(question, retrieve(question))
    if not has_evidence(hits, threshold):  # weak evidence: refuse, never call the LLM
        if advice:
            return Answer(ADVICE_NOTICE, refusal="advice")
        return Answer(NO_EVIDENCE, refusal="no_evidence")
    context, used = assemble_context(hits)
    messages = build_messages(
        render_prompt("answer", context=context, question=question), load_system_prompt()
    )
    text, citations = resolve_citations(generate(messages), used)
    if advice:  # US-05: decline the advice, still offer the related facts
        return Answer(f"{ADVICE_NOTICE}\n\n{text}", used, "advice", citations)
    return Answer(text, sources=used, citations=citations)
