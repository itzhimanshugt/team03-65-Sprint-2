import csv

from ingestion.pipeline import ingest_catalog, validate

FIELDS = ["filename", "family", "doc_type", "issuer", "title", "published_date", "version", "url"]


def write_catalog(tmp_path, rows):
    with open(tmp_path / "catalog.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    return tmp_path / "catalog.csv"


def row(filename, family="faq", version="1"):
    return {
        "filename": filename,
        "family": family,
        "doc_type": "internal",
        "issuer": "Demo",
        "title": filename,
        "published_date": "2026-10-01",
        "version": version,
        "url": "",
    }


def test_ingests_and_validates_clean_corpus(tmp_path):
    (tmp_path / "a.md").write_text("# A\nExit load is 1%.\n## B\nNAV is daily.", encoding="utf-8")
    (tmp_path / "b.txt").write_text("Shelf notes v2.", encoding="utf-8")
    (tmp_path / "c.txt").write_text("Shelf notes v1.", encoding="utf-8")
    catalog = write_catalog(
        tmp_path, [row("a.md"), row("b.txt", "shelf", "2"), row("c.txt", "shelf", "1")]
    )
    result = ingest_catalog(catalog)
    assert len(result.records) == 4
    assert not any(validate(result).values())


def test_validation_flags_missing_files_and_duplicates(tmp_path):
    (tmp_path / "a.txt").write_text("Same text.", encoding="utf-8")
    (tmp_path / "b.txt").write_text("Same text.", encoding="utf-8")
    catalog = write_catalog(
        tmp_path, [row("a.txt", "x"), row("b.txt", "y"), row("missing.pdf", "z")]
    )
    checks = validate(ingest_catalog(catalog))
    assert checks["Every catalogued document loaded"]
    assert checks["No duplicate documents (same checksum)"]
    assert checks["Chunk IDs unique"]  # same file content gives the same doc_id
