"""Embed the whole corpus into data/processed/embeddings.npy (+ embedding_ids.json).

Run: python -m scripts.embed_corpus  (needs data/processed/chunks.jsonl)
Re-running only embeds chunks that are not in the cache yet, smallest documents first.
Every run, complete or stopped by a daily quota, is logged to outputs/c19/embedding_runs.md;
a stopped run exits with status 1.
"""

import json
from collections import Counter
from datetime import date
from pathlib import Path

from openai import RateLimitError

from app.config import get_settings
from app.llm import retry_delay_seconds
from embeddings.batch import BatchReport, VectorCache, embed_records

records = [json.loads(line) for line in open("data/processed/chunks.jsonl", encoding="utf-8")]
# Smallest documents first: a run cut short by the daily quota still covers the most documents.
size = Counter(r["doc_id"] for r in records)
records.sort(key=lambda r: size[r["doc_id"]])  # stable: chunk order within a document is kept
rep, result = BatchReport(), "complete"
try:
    embed_records(records, VectorCache("data/processed"), report=rep)
except RateLimitError as error:  # daily quota: everything up to the last batch is already saved
    wait = retry_delay_seconds(str(error))
    result = (
        f"stopped by daily quota (resets in {wait / 3600:.0f} h)" if wait else "stopped by quota"
    )
model = get_settings().embedding_model
row = (
    f"| {date.today()} | {rep.total:,} | {rep.skipped:,} | {rep.embedded:,} | {rep.requests} | "
    f"{rep.retries} | {rep.tokens:,} | ${rep.cost(model):.4f} | {rep.seconds:.0f} s | {result} |"
)
HEADER = [
    "# C19 — Batch embedding runs",
    "",
    f"Batches of ≤ 100 chunks / ≤ 8,000 tokens · model `{model}` · cost at paid-tier list price.",
    "",
    "| Date | Chunks | Cached | Embedded | Requests | Retries | Tokens | Cost | Time | Result |",
    "|---|---|---|---|---|---|---|---|---|---|",
]
out = Path("outputs/c19/embedding_runs.md")
out.parent.mkdir(parents=True, exist_ok=True)
if not out.exists():
    out.write_text("\n".join(HEADER) + "\n", encoding="utf-8")
with out.open("a", encoding="utf-8") as f:
    f.write(row + "\n")
print(out.read_text(encoding="utf-8"))
raise SystemExit(0 if result == "complete" else 1)
