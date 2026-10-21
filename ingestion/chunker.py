"""Split documents into chunks that fit retrieval and context limits.

Two strategies:
- fixed_size_split: cut every `size` characters, ignoring text structure (baseline).
- recursive_split: cut at the largest natural boundary that fits
  (paragraph, then line, then sentence, then word), so chunks keep whole units of meaning.
Chunks never cross a page/section, so every chunk keeps one citation position.
"""

from collections.abc import Callable

from app.config import get_settings
from app.tokens import count_tokens
from ingestion.loaders import Document

SEPARATORS = ("\n\n", "\n", ". ", " ")


def fixed_size_split(text: str, size: int) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)]


def recursive_split(
    text: str,
    size: int,
    length: Callable[[str], int] = len,
    overlap: int = 0,
    separators: tuple[str, ...] = SEPARATORS,
) -> list[str]:
    if length(text) <= size:
        return [text] if text.strip() else []
    sep = next((s for s in separators if s in text), None)
    if sep is None:  # one unbroken run longer than size: hard cut
        cut = max(1, len(text) * size // length(text))
        return [text[:cut], *recursive_split(text[cut:], size, length, overlap, ())]
    rest = separators[separators.index(sep) + 1 :]
    pieces = []
    for part in text.split(sep):
        if length(part) > size:
            pieces.extend(recursive_split(part, size, length, overlap, rest))
        else:
            pieces.append(part)
    return _merge(pieces, sep, size, length, overlap)


def _merge(
    pieces: list[str], sep: str, size: int, length: Callable[[str], int], overlap: int = 0
) -> list[str]:
    """Greedily pack pieces into chunks of at most `size`, re-joined with `sep`.

    With `overlap`, each new chunk starts with the previous chunk's last pieces (up to
    `overlap` long), so a fact split across a boundary is whole in at least one chunk.
    """
    chunks, current, current_len, sep_len = [], [], 0, length(sep)
    for piece in pieces:
        piece_len = length(piece)
        # shortcut: lengths are summed, not re-measured; exact for characters, within a
        # token or two for tokens (chunk_by_tokens keeps a margin).
        if current and current_len + sep_len + piece_len > size:
            chunks.append(sep.join(current))
            tail, tail_len = [], 0
            for prev in reversed(current):
                prev_len = length(prev) + (sep_len if tail else 0)
                if tail_len + prev_len > overlap:
                    break
                tail.insert(0, prev)
                tail_len += prev_len
            if tail and tail_len + sep_len + piece_len > size:  # no room: drop the overlap
                tail, tail_len = [], 0
            current, current_len = tail, tail_len
        current_len += piece_len + (sep_len if current else 0)
        current.append(piece)
    if current:
        chunks.append(sep.join(current))
    return [c.strip() for c in chunks if c.strip()]


def chunk_document(
    doc: Document,
    size: int,
    length: Callable[[str], int] = len,
    strategy: str = "recursive",
    overlap: int = 0,
) -> list[tuple[int, str]]:
    """Return (position, chunk_text) for every chunk in the document."""
    split = (
        (lambda t: fixed_size_split(t, size))
        if strategy == "fixed"
        else (lambda t: recursive_split(t, size, length, overlap))
    )
    return [(pos, chunk) for pos, text in doc.pages for chunk in split(text)]


TOKEN_MARGIN = 8  # summed token lengths can undercount by a few; stay safely under the limit


def chunk_by_tokens(doc: Document) -> list[tuple[int, str]]:
    """Production chunking: recursive, sized in tokens with overlap (PRD §6.2: 400 / 60)."""
    s = get_settings()
    return chunk_document(doc, s.chunk_size - TOKEN_MARGIN, count_tokens, overlap=s.chunk_overlap)
