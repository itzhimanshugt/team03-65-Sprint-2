"""Index every embedded chunk into ChromaDB and verify it.

Run: python -m scripts.build_index  (after scripts.embed_corpus; writes outputs/c22/index_report.md)
Exits with status 1 if a check fails.
"""

import json
import sys
import time
from pathlib import Path

from embeddings.batch import VectorCache
from retrieval.indexer import build_index, verify_index
from retrieval.vector_store import get_collection

records = [json.loads(line) for line in open("data/processed/chunks.jsonl", encoding="utf-8")]
cache = VectorCache("data/processed")
col = get_collection()
start = time.perf_counter()
n = build_index(col, records, cache.ids, cache.vectors)
took = time.perf_counter() - start
checks = verify_index(col, records, cache.ids, cache.vectors)
docs = {r["source_name"] for r in records if r["chunk_id"] in set(cache.ids)}
lines = [
    "# C22 — Indexing report",
    "",
    f"**{n:,} of {len(records):,} chunks indexed** from {len(docs)} documents in {took:.1f} s "
    f"(the rest are waiting for embeddings; re-running adds them without duplicates).",
    "",
    "| Check | Result |",
    "|---|---|",
    *[f"| {k} | {'PASS' if v else 'FAIL'} |" for k, v in checks.items()],
]
out = Path("outputs/c22/index_report.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out.read_text(encoding="utf-8"))
sys.exit(0 if all(checks.values()) else 1)
