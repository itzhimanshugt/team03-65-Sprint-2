"""Ingest the whole corpus, validate it and save the chunks.

Run: python -m scripts.ingest_corpus
Writes data/processed/chunks.jsonl (git-ignored) and outputs/c15/ingestion_validation.md.
Exits with status 1 if any validation check fails.
"""

import statistics
import sys
from pathlib import Path

from ingestion.pipeline import ingest_catalog, validate

result = ingest_catalog()
checks = validate(result)

Path("data/processed").mkdir(parents=True, exist_ok=True)
with open("data/processed/chunks.jsonl", "w", encoding="utf-8") as f:
    f.writelines(r.model_dump_json() + "\n" for r in result.records)

loaded = [d for d in result.docs if not d.error]
complete = sum(1 for d in loaded if d.chunks) / len(result.docs)
per_50_pages = statistics.median(
    d.seconds / d.pages * 50 for d in loaded if d.source.endswith(".pdf")
)
lines = [
    "# C15 — Corpus ingestion and validation",
    "",
    f"**{len(loaded)}/{len(result.docs)} documents · {len(result.records):,} chunks · "
    f"{sum(d.seconds for d in result.docs):.0f} s total**",
    "",
    "## Validation checks",
    "",
    "| Check | Result |",
    "|---|---|",
    *[
        f"| {name} | {'PASS' if not bad else 'FAIL: ' + ', '.join(bad[:5])} |"
        for name, bad in checks.items()
    ],
    "",
    "## KPIs",
    "",
    "| KPI | Target | Measured |",
    "|---|---|---|",
    f"| K9 Ingestion completeness | 100% of corpus docs with all metadata | {complete:.0%} |",
    "| K10 Ingestion speed (load to chunks, per 50 PDF pages, median) | ≤ 60 s | "
    f"{per_50_pages:.1f} s |",
    "",
    "K10 here covers load, clean, chunk and metadata. Embedding and indexing time is added in C22.",
    "",
    "## Per document",
    "",
    "| Document | Pages/sections | Chunks | Time |",
    "|---|---|---|---|",
    *[f"| {d.source} | {d.pages} | {d.chunks} | {d.seconds:.1f} s |" for d in result.docs],
]
out = Path("outputs/c15/ingestion_validation.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out.read_text(encoding="utf-8"))
sys.exit(0 if not any(checks.values()) else 1)
