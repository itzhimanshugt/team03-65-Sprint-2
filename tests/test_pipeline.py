from rag.pipeline import NO_EVIDENCE, answer, assemble_context
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
    assert system["role"] == "system" and "[1] (f.pdf · p.3)" in user["content"]


def test_weak_evidence_refuses_without_calling_llm():
    def generate(messages):
        raise AssertionError("LLM must not be called")

    out = answer("x", retrieve=lambda q: [hit("a", 0.2)], generate=generate, threshold=0.5)
    assert out.refused and out.text == NO_EVIDENCE and out.sources == []


def test_context_stops_at_token_budget():
    hits = [hit(str(i), 0.9, "word " * 100) for i in range(10)]
    context, used = assemble_context(hits, budget=250)
    assert len(used) == 2 and context.startswith("[1]") and "[3]" not in context
