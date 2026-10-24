"""Map the answer's [n] markers to the sources the model was shown; drop ones that point nowhere."""

import re
from dataclasses import dataclass

from retrieval.search import Hit

MARKER = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")  # [1] or [1, 2]


@dataclass
class Citation:
    n: int
    source_name: str
    page: int | None
    title: str
    chunk_id: str


def resolve_citations(text: str, sources: list[Hit]) -> tuple[str, list[Citation]]:
    """Return the text with invalid markers removed, and the cited sources in first-use order."""
    cited: dict[int, Citation] = {}

    def keep(match: re.Match) -> str:
        valid = [n for n in map(int, re.split(r"\s*,\s*", match[1])) if 1 <= n <= len(sources)]
        for n in valid:
            h = sources[n - 1]
            md = h.metadata
            cited.setdefault(
                n,
                Citation(n, md.get("source_name"), md.get("page"), md.get("title", ""), h.chunk_id),
            )
        return f"[{', '.join(map(str, valid))}]" if valid else ""

    cleaned = MARKER.sub(keep, text)
    return re.sub(r" +([.,;])", r"\1", cleaned), list(cited.values())
