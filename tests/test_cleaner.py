from ingestion.cleaner import clean_document, normalize
from ingestion.loaders import Document

HEADER = "ACME Mutual Fund - monthly factsheet"


def test_normalize_unicode_hyphens_and_whitespace():
    raw = "The ﬁnal regis-\ntration   fee\t is  1%.\n\n\n\nNext   para "
    assert normalize(raw) == "The final registration fee is 1%.\n\nNext para"


def test_removes_long_lines_repeated_on_most_pages_and_page_numbers():
    pages = [(i, f"{HEADER}\nPage {i} of 5\nFact {i}: exit load {i}%") for i in range(1, 6)]
    cleaned, removed = clean_document(Document("f.pdf", "pdf", pages))
    assert removed == {HEADER}
    assert cleaned.pages[0] == (1, "Fact 1: exit load 1%")
    assert all("Page" not in t for _, t in cleaned.pages)


def test_keeps_lines_repeated_on_half_or_fewer_pages():
    pages = [(1, f"{HEADER}\nA"), (2, f"{HEADER}\nB"), (3, "C"), (4, "D")]
    _, removed = clean_document(Document("f.pdf", "pdf", pages))
    assert not removed


def test_short_repeated_lines_are_kept():
    pages = [(i, f"Moderately High Risk\nScheme {i}") for i in range(1, 6)]
    cleaned, removed = clean_document(Document("f.pdf", "pdf", pages))
    assert not removed and cleaned.pages[0][1].startswith("Moderately High Risk")


def test_short_documents_skip_boilerplate_detection():
    pages = [(1, f"{HEADER}\nA"), (2, f"{HEADER}\nB")]
    _, removed = clean_document(Document("c.pdf", "pdf", pages))
    assert removed == set()


def test_pages_emptied_by_cleaning_are_dropped():
    pages = [(i, f"{HEADER}\nfact {i}") for i in range(1, 5)] + [(5, f"{HEADER}\n5")]
    cleaned, _ = clean_document(Document("f.pdf", "pdf", pages))
    assert [p for p, _ in cleaned.pages] == [1, 2, 3, 4]
