"""Compare fixed-size vs recursive chunking on three corpus documents.

Run: python -m scripts.chunking_report  (writes outputs/c12/chunking_report.md)
"""

import re
from pathlib import Path

from ingestion.chunker import chunk_document
from ingestion.cleaner import clean_document
from ingestion.loaders import load_document

SIZE = 1_600  # characters, about 400 tokens
FILES = [
    "raw/ppfas-factsheet-2026-09.pdf",
    "raw/sebi-master-circular-ia-2026-02.pdf",
    "internal/firm-faq.md",
]


def stats(doc, chunks: list[tuple[int, str]]) -> tuple[int, int, str, str]:
    texts = [t for _, t in chunks]
    pages = dict(doc.pages)
    clean_end = sum(bool(re.search(r"[.!?:;)%]$", t)) for t in texts) / len(texts)
    # A word is cut in half when two neighbouring chunks join with no separator inside a word.
    cut = sum(
        a[1][-1].isalnum() and b[1][0].isalnum() and (a[1][-15:] + b[1][:15]) in pages[a[0]]
        for a, b in zip(chunks, chunks[1:], strict=False)
        if a[0] == b[0]
    ) / max(1, len(texts) - 1)
    return len(texts), sum(map(len, texts)) // len(texts), f"{clean_end:.0%}", f"{cut:.0%}"


lines = [
    "# C12 — Chunking strategies (size 1,600 characters ≈ 400 tokens)",
    "",
    "| Document | Strategy | Chunks | Mean chars | Ends at sentence end | Cuts a word |",
    "|---|---|---|---|---|---|",
]
examples = []
for name in FILES:
    doc, _ = clean_document(load_document(Path("data") / name))
    for strategy in ("fixed", "recursive"):
        chunks = chunk_document(doc, SIZE, strategy=strategy)
        n, mean, end, cut = stats(doc, chunks)
        lines.append(f"| {doc.source} | {strategy} | {n} | {mean} | {end} | {cut} |")
        if "master-circular" in name:
            boundary = chunks[4][1][-160:] + "\n<<< CHUNK BOUNDARY >>>\n" + chunks[5][1][:160]
            examples.append((strategy, boundary))

lines += ["", "## Same SEBI circular, boundary between chunk 5 and chunk 6", ""]
for strategy, text in examples:
    lines += [f"**{strategy}:**", "", "```", text, "```", ""]

out = Path("outputs/c12/chunking_report.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines), encoding="utf-8")
print(out.read_text(encoding="utf-8"))
