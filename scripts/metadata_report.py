"""Build chunk records for the whole corpus and show their metadata.

Run: python -m scripts.metadata_report  (writes outputs/c13/metadata_report.md)
"""

import csv
from pathlib import Path

from ingestion.chunker import chunk_document
from ingestion.cleaner import clean_document
from ingestion.loaders import load_document
from ingestion.metadata import build_records, latest_versions

catalog = list(csv.DictReader(open("data/catalog.csv", encoding="utf-8")))
latest = latest_versions(catalog)
rows = [
    "| File | Family | Version | is_latest | Chunks | Pages cited |",
    "|---|---|---|---|---|---|",
]
sample = None
for entry in catalog:
    path = Path("data") / entry["filename"]
    doc, _ = clean_document(load_document(path))
    records = build_records(entry, path, chunk_document(doc, 1_600), latest)
    pages = sorted({r.page for r in records})
    rows.append(
        f"| {path.name} | {entry['family']} | {entry['version']} | "
        f"{records[0].is_latest} | {len(records)} | {pages[0]}–{pages[-1]} |"
    )
    if entry["family"] == "ppfas-factsheet" and records[0].is_latest:
        sample = records[3]

out = Path("outputs/c13/metadata_report.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(
    "# C13 — Chunk metadata\n\n"
    + "\n".join(rows)
    + "\n\n## Example chunk record\n\n```json\n"
    + sample.model_dump_json(indent=2)
    + "\n```\n",
    encoding="utf-8",
)
print(out.read_text(encoding="utf-8"))
