"""Clean every catalogued document and report what was removed.

Run: python -m scripts.cleaning_report  (writes outputs/c11/cleaning_report.md)
"""

import csv
from pathlib import Path

from ingestion.cleaner import clean_document
from ingestion.loaders import load_document

rows = ["| File | Chars before | Chars after | Removed | Boilerplate lines removed (sample) |"]
rows.append("|---|---|---|---|---|")
total_before = total_after = 0
for entry in csv.DictReader(open("data/catalog.csv", encoding="utf-8")):
    doc = load_document(Path("data") / entry["filename"])
    cleaned, repeated = clean_document(doc)
    before, after = len(doc.text), len(cleaned.text)
    total_before, total_after = total_before + before, total_after + after
    sample = "; ".join(sorted(repeated, key=len, reverse=True)[:2])[:120].replace("|", "/")
    rows.append(
        f"| {doc.source} | {before:,} | {after:,} | {1 - after / before:.0%} | {sample or '-'} |"
    )
rows.append(
    f"| **Total** | **{total_before:,}** | **{total_after:,}** | "
    f"**{1 - total_after / total_before:.0%}** | |"
)

out = Path("outputs/c11/cleaning_report.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("# C11 — Cleaning report\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
print(out.read_text(encoding="utf-8"))
