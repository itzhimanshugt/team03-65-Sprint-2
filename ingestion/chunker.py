"""Split documents into chunks that fit retrieval and context limits.

Two strategies:
- fixed_size_split: cut every `size` characters, ignoring text structure (baseline).
- recursive_split: cut at the largest natural boundary that fits
  (paragraph, then line, then sentence, then word), so chunks keep whole units of meaning.
Chunks never cross a page/section, so every chunk keeps one citation position.
"""

from collections.abc import Callable

from ingestion.loaders import Document

SEPARATORS = ("\n\n", "\n", ". ", " ")


def fixed_size_split(text: str, size: int) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)]


def recursive_split(
    text: str,
    size: int,
    length: Callable[[str], int] = len,
    separators: tuple[str, ...] = SEPARATORS,
) -> list[str]:
    if length(text) <= size:
        return [text] if text.strip() else []
    sep = next((s for s in separators if s in text), None)
    if sep is None:  # one unbroken run longer than size: hard cut
        cut = max(1, len(text) * size // length(text))
        return [text[:cut], *recursive_split(text[cut:], size, length, ())]
    rest = separators[separators.index(sep) + 1 :]
    pieces = []
    for part in text.split(sep):
        pieces.extend(recursive_split(part, size, length, rest) if length(part) > size else [part])
    return _merge(pieces, sep, size, length)


def _merge(pieces: list[str], sep: str, size: int, length: Callable[[str], int]) -> list[str]:
    """Greedily pack pieces into chunks of at most `size`, re-joined with `sep`."""
    chunks, current, current_len, sep_len = [], [], 0, length(sep)
    for piece in pieces:
        piece_len = length(piece)
        # shortcut: lengths are summed, not re-measured; exact for characters, within a
        # token or two for tokens (C14 keeps a margin).
        if current and current_len + sep_len + piece_len > size:
            chunks.append(sep.join(current))
            current, current_len = [], 0
        current_len += piece_len + (sep_len if current else 0)
        current.append(piece)
    if current:
        chunks.append(sep.join(current))
    return [c.strip() for c in chunks if c.strip()]


def chunk_document(
    doc: Document, size: int, length: Callable[[str], int] = len, strategy: str = "recursive"
) -> list[tuple[int, str]]:
    """Return (position, chunk_text) for every chunk in the document."""
    split = (
        (lambda t: fixed_size_split(t, size))
        if strategy == "fixed"
        else (lambda t: recursive_split(t, size, length))
    )
    return [(pos, chunk) for pos, text in doc.pages for chunk in split(text)]
