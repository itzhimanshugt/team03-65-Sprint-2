"""Token-aware chunking over the whole corpus: size distribution, limit check and overlap.

Run: python -m scripts.token_chunking_report  (writes outputs/c14/token_chunking_report.md)
"""

import csv
from pathlib import Path

from app.tokens import count_tokens
from ingestion.chunker import chunk_by_tokens, chunk_document
from ingestion.cleaner import clean_document
from ingestion.loaders import load_document

char_sizes, token_sizes, pairs, overlapping = [], [], 0, 0
for entry in csv.DictReader(open("data/catalog.csv", encoding="utf-8")):
    doc, _ = clean_document(load_document(Path("data") / entry["filename"]))
    char_sizes += [count_tokens(t) for _, t in chunk_document(doc, 1_600)]
    chunks = chunk_by_tokens(doc)
    token_sizes += [count_tokens(t) for _, t in chunks]
    for (p1, a), (p2, b) in zip(chunks, chunks[1:], strict=False):
        if p1 == p2:
            pairs += 1
            overlapping += b.splitlines()[0] in a


def histogram(sizes: list[int]) -> list[str]:
    bins = [(0, 100), (100, 200), (200, 300), (300, 400), (400, 10_000)]
    return [f"{sum(lo <= s < hi for s in sizes) / len(sizes):.0%}" for lo, hi in bins]


lines = [
    "# C14 — Token-aware chunk sizing and overlap",
    "",
    "Target: 400 tokens per chunk (8-token safety margin), 60-token overlap. Sizes measured "
    "exactly with tiktoken after chunking.",
    "",
    "| Chunking | Chunks | Mean tokens | Max tokens | <100 | 100–199 | 200–299 | 300–399 | ≥400 |",
    "|---|---|---|---|---|---|---|---|---|",
]
for name, sizes in (
    ("1,600 characters (C12)", char_sizes),
    ("400 tokens + overlap (C14)", token_sizes),
):
    lines.append(
        f"| {name} | {len(sizes):,} | {sum(sizes) // len(sizes)} | {max(sizes)} | "
        + " | ".join(histogram(sizes))
        + " |"
    )
lines += [
    "",
    f"Neighbouring chunks on the same page that share overlap text: "
    f"**{overlapping:,} of {pairs:,} ({overlapping / pairs:.0%})**. The rest meet at a boundary "
    "where the last piece is longer than 60 tokens, so it can't be repeated.",
]

out = Path("outputs/c14/token_chunking_report.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out.read_text(encoding="utf-8"))
