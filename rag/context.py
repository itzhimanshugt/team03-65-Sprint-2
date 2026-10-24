"""Context injection: turn ranked chunks into the numbered, cited excerpts the prompt carries."""

from app.tokens import count_tokens
from retrieval.search import Hit

CONTEXT_TOKEN_BUDGET = 3000  # PRD §8: assembled context stays under ~3k tokens


def source_header(n: int, hit: Hit) -> str:
    md = hit.metadata
    title = md.get("title") or md.get("source_name")
    return f"[{n}] {title} · p.{md.get('page')} · published {md.get('published_date', 'n/a')}"


def assemble_context(hits: list[Hit], budget: int = CONTEXT_TOKEN_BUDGET) -> tuple[str, list[Hit]]:
    """Number chunks [1]..[k] in rank order; when over budget, the lowest-ranked are dropped."""
    blocks, used, total = [], [], 0
    for hit in hits:
        block = f"{source_header(len(used) + 1, hit)}\n{hit.text.strip()}"
        cost = count_tokens(block)
        if total + cost > budget:
            break
        blocks.append(block)
        used.append(hit)
        total += cost
    return "\n\n".join(blocks), used
