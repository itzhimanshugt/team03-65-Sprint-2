import pytest
from pydantic import ValidationError

from ingestion.metadata import ChunkRecord, build_records, latest_versions

CATALOG = [
    {"family": "acme-fs", "version": "1"},
    {"family": "acme-fs", "version": "2"},
    {"family": "faq", "version": "1"},
]


def entry(version="2"):
    return {
        "title": "ACME Factsheet",
        "doc_type": "factsheet",
        "issuer": "ACME MF",
        "family": "acme-fs",
        "published_date": "2026-08-31",
        "version": version,
    }


def test_latest_version_per_family():
    assert latest_versions(CATALOG) == {"acme-fs": 2, "faq": 1}


def test_records_carry_source_position_and_ids(tmp_path):
    f = tmp_path / "acme.pdf"
    f.write_bytes(b"%PDF fake bytes")
    records = build_records(
        entry(), f, [(3, "Exit load 1%"), (4, "Expense ratio 0.68%")], {"acme-fs": 2}
    )
    first = records[0]
    assert first.chunk_id == f"{first.doc_id}-0000" and records[1].chunk_index == 1
    assert (first.page, first.source_name, first.is_latest) == (3, "acme.pdf", True)
    assert first.token_count > 0 and len(first.checksum) == 64


def test_older_version_is_not_latest(tmp_path):
    f = tmp_path / "old.pdf"
    f.write_bytes(b"%PDF old")
    (record,) = build_records(entry("1"), f, [(1, "text")], {"acme-fs": 2})
    assert record.is_latest is False


def test_same_file_gets_same_doc_id(tmp_path):
    a, b = tmp_path / "a.pdf", tmp_path / "b.pdf"
    a.write_bytes(b"same")
    b.write_bytes(b"same")
    ids = {build_records(entry(), p, [(1, "t")], {"acme-fs": 2})[0].doc_id for p in (a, b)}
    assert len(ids) == 1  # duplicate upload detectable by doc_id


def test_schema_rejects_bad_values(tmp_path):
    f = tmp_path / "x.pdf"
    f.write_bytes(b"x")
    good = build_records(entry(), f, [(1, "t")], {"acme-fs": 2})[0].model_dump()
    for field, bad in [("doc_type", "blog"), ("page", 0), ("text", "")]:
        with pytest.raises(ValidationError):
            ChunkRecord(**{**good, field: bad})
