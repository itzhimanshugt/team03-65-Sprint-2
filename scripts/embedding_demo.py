"""Embed three real corpus chunks and show what an embedding looks like.

Run: python -m scripts.embedding_demo
Needs data/processed/chunks.jsonl (python -m scripts.ingest_corpus).
"""

import json
import time
from pathlib import Path

from app.config import get_settings
from embeddings.embedder import embed_texts

chunks = [json.loads(line) for line in open("data/processed/chunks.jsonl", encoding="utf-8")]
picked = [c for c in chunks if c["family"] == "ppfas-factsheet" and c["is_latest"]][3:4]
picked += [c for c in chunks if c["family"] == "firm-faq"][:1]
picked += [c for c in chunks if c["doc_type"] == "circular"][:1]
start = time.perf_counter()
vectors = embed_texts([c["text"] for c in picked])
took = time.perf_counter() - start
s = get_settings()
lines = [
    "# C17 — Embeddings via API",
    "",
    f"Model `{s.embedding_model}` · {s.embedding_dimensions} dimensions · "
    f"{len(picked)} chunks in one request · {took:.1f} s",
    "",
    "| Chunk | Source · page | Tokens | Dims | First 5 values |",
    "|---|---|---|---|---|",
]
for c, v in zip(picked, vectors, strict=True):
    head = ", ".join(f"{x:+.4f}" for x in v[:5])
    src = f"{c['source_name']} · p.{c['page']}"
    lines.append(f"| `{c['chunk_id']}` | {src} | {c['token_count']} | {len(v)} | {head} … |")
out = Path("outputs/c17/embedding_demo.md")
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out.read_text(encoding="utf-8"))
