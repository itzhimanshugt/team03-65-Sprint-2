from rag.context import assemble_context, source_header
from retrieval.search import Hit

MD = {"title": "HSBC Factsheet Aug 2026", "page": 39, "published_date": "2026-08-31"}


def hit(cid, text="Exit load 1% within 1 year."):
    return Hit(cid, text, 0.8, MD)


def test_header_names_title_page_and_date():
    assert source_header(2, hit("a")) == "[2] HSBC Factsheet Aug 2026 · p.39 · published 2026-08-31"


def test_sources_numbered_in_rank_order():
    context, used = assemble_context([hit("a", "first"), hit("b", "second")])
    assert [h.chunk_id for h in used] == ["a", "b"]
    assert (
        context.index("[1]")
        < context.index("first")
        < context.index("[2]")
        < context.index("second")
    )


def test_over_budget_drops_lowest_ranked():
    hits = [hit(str(i), "word " * 100) for i in range(10)]
    context, used = assemble_context(hits, budget=250)
    assert [h.chunk_id for h in used] == ["0", "1"] and "[3]" not in context
