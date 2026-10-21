"""Normalise extracted text and strip repeated boilerplate before chunking."""

import re
import unicodedata
from collections import Counter

from ingestion.loaders import Document

PAGE_NUMBER = re.compile(r"^(page\s*)?\d{1,4}(\s*(of|/)\s*\d{1,4})?$", re.IGNORECASE)
MIN_PAGES_FOR_BOILERPLATE = 4  # too few pages to tell a header from content
# Short repeated lines are often per-page facts ("Moderately High Risk"), not boilerplate.
MIN_BOILERPLATE_CHARS = 25


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)  # ligatures (ﬁ), full-width chars, odd spaces
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)  # re-join words hyphenated at line breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def boilerplate_lines(pages: list[str]) -> set[str]:
    """Lines that appear on more than half the pages: headers, footers, repeated disclaimers."""
    if len(pages) < MIN_PAGES_FOR_BOILERPLATE:
        return set()
    counts = Counter(line for page in pages for line in {ln for ln in page.splitlines() if ln})
    return {
        line
        for line, n in counts.items()
        if n > len(pages) / 2 and len(line) >= MIN_BOILERPLATE_CHARS
    }


def clean_document(doc: Document) -> tuple[Document, set[str]]:
    """Return the cleaned document and the boilerplate lines that were removed."""
    pages = [(pos, normalize(text)) for pos, text in doc.pages]
    repeated = boilerplate_lines([text for _, text in pages])
    cleaned = []
    for pos, text in pages:
        lines = [ln for ln in text.splitlines() if ln not in repeated and not PAGE_NUMBER.match(ln)]
        text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
        if text:
            cleaned.append((pos, text))
    return Document(source=doc.source, format=doc.format, pages=cleaned), repeated
