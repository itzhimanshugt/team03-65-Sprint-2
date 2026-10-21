from ingestion.chunker import chunk_document, fixed_size_split, recursive_split
from ingestion.loaders import Document

PARAS = "Exit load is 1% within a year.\n\nExpense ratio is 0.68% for direct.\n\nNAV is daily."


def test_fixed_size_cuts_blindly():
    chunks = fixed_size_split("abcdefghij", 4)
    assert chunks == ["abcd", "efgh", "ij"]


def test_short_text_is_one_chunk():
    assert recursive_split("Short text.", 100) == ["Short text."]
    assert recursive_split("   ", 100) == []


def test_recursive_prefers_paragraph_boundaries():
    chunks = recursive_split(PARAS, 70)
    assert chunks == [
        "Exit load is 1% within a year.\n\nExpense ratio is 0.68% for direct.",
        "NAV is daily.",
    ]


def test_falls_back_to_sentences_then_words():
    text = "First sentence here. Second sentence here. Third sentence here."
    chunks = recursive_split(text, 25)
    assert all(len(c) <= 25 for c in chunks)
    assert chunks[0] == "First sentence here"
    long_word = "x" * 30
    assert all(len(c) <= 10 for c in recursive_split(long_word, 10))


def test_no_chunk_exceeds_size_and_no_text_lost():
    text = ("Lorem ipsum dolor sit amet. " * 40 + "\n") * 5
    chunks = recursive_split(text, 200)
    assert max(len(c) for c in chunks) <= 200
    assert "".join(chunks).replace(" ", "").replace(".", "").replace("\n", "") == text.replace(
        " ", ""
    ).replace(".", "").replace("\n", "")


def test_chunks_keep_their_page():
    doc = Document("f.pdf", "pdf", [(3, "Page three text."), (4, PARAS)])
    chunks = chunk_document(doc, 70)
    assert [p for p, _ in chunks] == [3, 4, 4]
    assert [p for p, _ in chunk_document(doc, 70, strategy="fixed")][0] == 3


def test_overlap_repeats_tail_of_previous_chunk():
    lines = "\n".join(f"line {i} says something" for i in range(12))
    chunks = recursive_split(lines, 80, overlap=30)
    assert len(chunks) > 1
    for prev, nxt in zip(chunks, chunks[1:], strict=False):
        assert nxt.splitlines()[0] == prev.splitlines()[-1]
        assert len(nxt) <= 80


def test_overlap_zero_means_no_repeats():
    lines = "\n".join(f"line {i} says something" for i in range(12))
    chunks = recursive_split(lines, 80)
    assert sum(len(c.splitlines()) for c in chunks) == 12


def test_token_chunks_stay_under_limit_with_overlap():
    from app.tokens import count_tokens
    from ingestion.chunker import chunk_by_tokens

    text = "\n".join(f"Scheme {i}: exit load {i % 3}% within {i * 30} days." for i in range(300))
    chunks = chunk_by_tokens(Document("f.pdf", "pdf", [(1, text)]))
    assert max(count_tokens(c) for _, c in chunks) <= 400
    first_line_of_second = chunks[1][1].splitlines()[0]
    assert first_line_of_second in chunks[0][1]  # overlap carried over
