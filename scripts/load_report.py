"""Load every catalogued document and report what was extracted.

Run: python -m scripts.load_report  (writes outputs/c10/load_report.md)
"""

import csv
import time
from pathlib import Path

from ingestion.loaders import UnsupportedDocumentError, load_document

rows = [
    "| File | Format | Pages/sections | Characters | Time | Status |",
    "|---|---|---|---|---|---|",
]
for entry in csv.DictReader(open("data/catalog.csv", encoding="utf-8")):
    path = Path("data") / entry["filename"]
    start = time.perf_counter()
    try:
        doc = load_document(path)
        status, fmt, n, chars = "ok", doc.format, len(doc.pages), f"{len(doc.text):,}"
    except (UnsupportedDocumentError, FileNotFoundError) as error:
        status, fmt, n, chars = f"rejected: {error}", path.suffix[1:], "-", "-"
    rows.append(
        f"| {path.name} | {fmt} | {n} | {chars} | {time.perf_counter() - start:.1f}s | {status} |"
    )

out = Path("outputs/c10/load_report.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("# C10 — Corpus load report\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
print(out.read_text(encoding="utf-8"))
