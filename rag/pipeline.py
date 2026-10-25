"""End-to-end RAG flow: retrieve → re-rank → evidence gate → assemble context → generate.

Each stage is a plain function passed in, so later concepts swap one stage without touching the
rest (hybrid retrieval C24, re-ranking C26, refusals C32, follow-up condensing C33).
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from app.config import get_settings
from app.llm import complete
from app.prompting import build_messages, load_system_prompt, render_prompt
from app.tokens import count_tokens
from rag.citations import Citation, resolve_citations
from rag.context import assemble_context
from rag.guardrails import ADVICE_NOTICE, NO_EVIDENCE, has_evidence, is_advice_seeking
from retrieval.neighbours import add_neighbours
from retrieval.reranker import rerank as lexical_rerank
from retrieval.search import Hit, search

Retrieve = Callable[[str], list[Hit]]
Rerank = Callable[[str, list[Hit]], list[Hit]]
Generate = Callable[[list[dict]], str]
Expand = Callable[[list[Hit]], list[Hit]]


@dataclass
class Answer:
    text: str
    sources: list[Hit] = field(default_factory=list)  # numbered [1], [2], … in the prompt
    refusal: str | None = None  # "no_evidence" (S2c) or "advice" (S2d)
    citations: list[Citation] = field(default_factory=list)  # only markers that resolve
    trace: dict = field(default_factory=dict)  # what each stage did, for the UI's audit panel

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
    expand: Expand = add_neighbours,
) -> Answer:
    threshold = get_settings().refusal_threshold if threshold is None else threshold
    advice = is_advice_seeking(question)
    pool = retrieve(question)
    hits = rerank(question, pool)
    trace = {
        "candidates": len(pool),
        "reranked": len(hits),
        "top_score": round(max((h.score for h in hits), default=0.0), 3),
        "threshold": threshold,
        "advice": advice,
    }
    if not has_evidence(hits, threshold):  # weak evidence: refuse, never call the LLM
        if advice:
            return Answer(ADVICE_NOTICE, refusal="advice", trace=trace)
        return Answer(NO_EVIDENCE, refusal="no_evidence", trace=trace)
    expanded = expand(hits)
    context, used = assemble_context(expanded)
    trace |= {
        "neighbours": len(expanded) - len(hits),
        "context_chunks": len(used),
        "context_tokens": count_tokens(context),
        "model": get_settings().llm_model,
    }
    messages = build_messages(
        render_prompt("answer", context=context, question=question), load_system_prompt()
    )
    text, citations = resolve_citations(generate(messages), used)
    if advice:  # US-05: decline the advice, still offer the related facts
        return Answer(f"{ADVICE_NOTICE}\n\n{text}", used, "advice", citations, trace)
    return Answer(text, sources=used, citations=citations, trace=trace)
