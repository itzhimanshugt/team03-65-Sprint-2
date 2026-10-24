from rag.citations import resolve_citations
from retrieval.search import Hit


def src(cid, page):
    return Hit(cid, "t", 0.8, {"source_name": "f.pdf", "page": page, "title": "F"})


SOURCES = [src("a", 3), src("b", 7)]


def test_markers_map_to_sources_in_first_use_order():
    text, cites = resolve_citations("Load is 1% [2]. NAV is 10 [1, 2].", SOURCES)
    assert text == "Load is 1% [2]. NAV is 10 [1, 2]."
    assert [(c.n, c.page, c.chunk_id) for c in cites] == [(2, 7, "b"), (1, 3, "a")]


def test_markers_outside_the_sources_are_dropped():
    text, cites = resolve_citations("Fact [3]. Other [1, 9].", SOURCES)
    assert text == "Fact. Other [1]." and [c.n for c in cites] == [1]


def test_no_markers_means_no_citations():
    assert resolve_citations("Plain text.", SOURCES) == ("Plain text.", [])
