from rag.guardrails import NO_EVIDENCE
from rag.pipeline import answer
from retrieval.search import Hit


def hit(cid, score, text="HSBC Value Fund exit load 1% within 1 year."):
    return Hit(cid, text, score, {"source_name": "f.pdf", "page": 3})


def test_stages_run_in_order_and_sources_are_numbered():
    seen = {}

    def generate(messages):
        seen["messages"] = messages
        return "Exit load is 1% [1]."

    out = answer(
        "exit load?",
        retrieve=lambda q: [hit("a", 0.6), hit("b", 0.8)],
        rerank=lambda q, hits: sorted(hits, key=lambda h: -h.score),
        generate=generate,
        threshold=0.5,
    )
    assert out.text == "Exit load is 1% [1]." and not out.refused
    assert [h.chunk_id for h in out.sources] == ["b", "a"]
    system, user = seen["messages"]
    assert system["role"] == "system" and "[1] f.pdf · p.3" in user["content"]


def test_weak_evidence_refuses_without_calling_llm():
    def generate(messages):
        raise AssertionError("LLM must not be called")

    out = answer("x", retrieve=lambda q: [hit("a", 0.2)], generate=generate, threshold=0.5)
    assert out.refused and out.text == NO_EVIDENCE and out.sources == []


def test_grounding_rules_reach_the_llm():
    seen = {}
    answer(
        "exit load?",
        retrieve=lambda q: [hit("a", 0.9)],
        generate=lambda m: seen.setdefault("m", m) and "ok",
        threshold=0.5,
    )
    system, user = seen["m"]
    assert "Do not use outside knowledge" in system["content"]
    assert "Answer only from the context above" in user["content"]


def test_trace_reports_each_stage():
    out = answer(
        "exit load?",
        retrieve=lambda q: [hit("a", 0.9), hit("b", 0.6)],
        rerank=lambda q, hits: hits[:1],
        generate=lambda m: "1% [1].",
        threshold=0.5,
        expand=lambda hits: hits,
    )
    t = out.trace
    assert (t["candidates"], t["reranked"], t["top_score"], t["neighbours"]) == (2, 1, 0.9, 0)
    assert t["context_chunks"] == 1 and t["context_tokens"] > 0
