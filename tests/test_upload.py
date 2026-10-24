import uuid

import chromadb
import pytest

from ingestion.upload import UploadError, index_upload

ENTRY = {
    "title": "Notes",
    "doc_type": "internal",
    "issuer": "Firm",
    "family": "notes",
    "published_date": "2026-10-01",
    "version": 1,
}


def fake_embed(texts):
    return [[1.0, 0.0, 0.0] for _ in texts]


@pytest.fixture
def col():
    return chromadb.EphemeralClient().create_collection(
        f"up-{uuid.uuid4().hex[:8]}", metadata={"hnsw:space": "cosine"}
    )


def test_upload_duplicate_and_new_version(tmp_path, col):
    v1 = tmp_path / "notes.md"
    v1.write_text("# Notes\n\nExit load is 1% within one year.", encoding="utf-8")
    r = index_upload(v1, ENTRY, col, fake_embed)
    assert r.chunks >= 1 and r.superseded == 0
    with pytest.raises(UploadError) as dup:
        index_upload(v1, ENTRY, col, fake_embed)
    assert dup.value.status == 409
    v2 = tmp_path / "notes-v2.md"
    v2.write_text("# Notes\n\nExit load is now 0.5% within one year.", encoding="utf-8")
    r2 = index_upload(v2, {**ENTRY, "version": 2}, col, fake_embed)
    assert r2.superseded == r.chunks
    latest = col.get(where={"is_latest": True})["metadatas"]
    assert {m["version"] for m in latest} == {2}


def test_rejects_bad_type_and_old_version(tmp_path, col):
    bad = tmp_path / "x.exe"
    bad.write_bytes(b"MZ")
    with pytest.raises(UploadError, match="Unsupported"):
        index_upload(bad, ENTRY, col, fake_embed)
    f = tmp_path / "a.txt"
    f.write_text("Some approved text here.", encoding="utf-8")
    index_upload(f, {**ENTRY, "version": 3}, col, fake_embed)
    g = tmp_path / "b.txt"
    g.write_text("Different older text.", encoding="utf-8")
    with pytest.raises(UploadError, match="not newer"):
        index_upload(g, {**ENTRY, "version": 2}, col, fake_embed)
