"""Embedding sanity report: meaning checks (live) and vector-store checks (offline).

Run: python -m scripts.embedding_sanity  (after scripts.embed_corpus; writes outputs/c20/sanity.md)
Exits with status 1 if any check fails.
"""

import json
import sys
from pathlib import Path

from app.config import get_settings
from embeddings.batch import VectorCache
from embeddings.embedder import embed_texts
from embeddings.sanity import meaning_checks, store_checks

rows = meaning_checks(embed_texts)
records = [json.loads(line) for line in open("data/processed/chunks.jsonl", encoding="utf-8")]
cache = VectorCache("data/processed")
store = store_checks(cache.vectors, cache.ids, records, get_settings().embedding_dimensions)

lines = ["# C20 — Embedding sanity checks", "", "## Meaning checks (live API)", ""]
lines += [
    "| Anchor | Close phrase | sim | Unrelated control | sim | Pass |",
    "|---|---|---|---|---|---|",
]
for r in rows:
    lines.append(
        f"| {r['anchor']} | {r['near']} | {r['near_sim']:.3f} | {r['far']} | {r['far_sim']:.3f} | "
        f"{'PASS' if r['ok'] else 'FAIL'} |"
    )
gap = min(r["near_sim"] - r["far_sim"] for r in rows)
lines += ["", f"Smallest margin between close and unrelated: **{gap:.3f}**", ""]
lines += [
    f"## Vector store checks ({len(cache.ids):,} vectors)",
    "",
    "| Check | Result |",
    "|---|---|",
]
lines += [f"| {k} | {'PASS' if v else 'FAIL'} |" for k, v in store.items()]
out = Path("outputs/c20/sanity.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out.read_text(encoding="utf-8"))
sys.exit(0 if all(r["ok"] for r in rows) and all(store.values()) else 1)
