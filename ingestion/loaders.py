"""Load PDF, HTML, Markdown and TXT files into one common representation."""

import re
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader

MAX_BYTES = 25 * 1024 * 1024  # PRD FR-1


class UnsupportedDocumentError(ValueError):
    """The file can't be ingested; the message says why (shown to the uploader, US-10)."""


@dataclass
class Document:
    source: str  # file name
    format: str  # pdf | html | md | txt
    pages: list[tuple[int, str]]  # (position, text): PDF page number, or section number

    @property
    def text(self) -> str:
        return "\n\n".join(t for _, t in self.pages)


def load_document(path: str | Path) -> Document:
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise UnsupportedDocumentError("File is larger than 25 MB.")
    loader = LOADERS.get(path.suffix.lower())
    if loader is None:
        raise UnsupportedDocumentError(
            f"Unsupported file type '{path.suffix}'. Use PDF, HTML, MD or TXT."
        )
    fmt, pages = loader(path)
    pages = [(pos, text) for pos, text in pages if text.strip()]
    if not pages:
        raise UnsupportedDocumentError("No selectable text found (scanned or empty document).")
    return Document(source=path.name, format=fmt, pages=pages)


def _pdf(path: Path):
    reader = PdfReader(path)
    # shortcut: PDFs locked with an empty user password are rejected too; try
    # reader.decrypt("") (needs the cryptography package) if real uploads hit this.
    if reader.is_encrypted:
        raise UnsupportedDocumentError("File is password protected.")
    return "pdf", [(i, page.extract_text() or "") for i, page in enumerate(reader.pages, start=1)]


def _html(path: Path):
    soup = BeautifulSoup(path.read_bytes(), "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "form", "svg"]):
        tag.decompose()
    root = soup.find("article") or soup.find("main") or soup.body or soup
    # One section per heading, so citations can point at a position inside the page.
    sections, current = [], []
    for el in root.find_all(["h1", "h2", "h3", "p", "li", "td", "th"]):
        if el.name in ("h1", "h2", "h3") and current:
            sections.append("\n".join(current))
            current = []
        text = el.get_text(" ", strip=True)
        if text:
            current.append(text)
    sections.append("\n".join(current))
    return "html", list(enumerate(sections, start=1))


def _markdown(path: Path):
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"\n(?=#{1,3} )", text)
    return "md", list(enumerate(sections, start=1))


def _txt(path: Path):
    return "txt", [(1, path.read_text(encoding="utf-8"))]


LOADERS = {".pdf": _pdf, ".html": _html, ".htm": _html, ".md": _markdown, ".txt": _txt}
