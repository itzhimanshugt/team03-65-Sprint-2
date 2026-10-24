"""Index one uploaded document: validate → load → clean → chunk → embed → upsert (US-09–US-11)."""

from dataclasses import dataclass
from pathlib import Path

from embeddings.embedder import embed_texts
from ingestion.chunker import chunk_by_tokens
from ingestion.cleaner import clean_document
from ingestion.loaders import UnsupportedDocumentError, load_document
from ingestion.metadata import build_records, file_checksum
from retrieval.vector_store import to_metadata

MAX_BYTES = 25 * 1024 * 1024
ALLOWED = {".pdf", ".html", ".htm", ".md", ".txt"}
EMBED_BATCH = 50


class UploadError(ValueError):
    def __init__(self, reason: str, status: int = 400):
        super().__init__(reason)
        self.status = status


@dataclass
class UploadResult:
    doc_id: str
    chunks: int
    superseded: int  # chunks of the older version marked is_latest=False


def index_upload(path: Path, entry: dict, collection, embed=embed_texts) -> UploadResult:
    """`entry` has the catalog fields: family, doc_type, issuer, title, published_date, version."""
    if path.suffix.lower() not in ALLOWED:
        raise UploadError(f"Unsupported file type {path.suffix}. Use PDF, HTML, TXT or MD.")
    if path.stat().st_size > MAX_BYTES:
        raise UploadError("File is larger than 25 MB.")
    checksum = file_checksum(path)
    if collection.get(where={"checksum": checksum}, limit=1)["ids"]:
        raise UploadError("This exact file is already indexed (duplicate checksum).", 409)
    try:
        doc, _ = clean_document(load_document(path))
    except UnsupportedDocumentError as error:
        raise UploadError(str(error)) from error
    chunks = chunk_by_tokens(doc)
    if not chunks:
        raise UploadError("This file has no selectable text (scanned or empty).")
    version, family = int(entry["version"]), entry["family"]
    older = collection.get(where={"$and": [{"family": family}, {"is_latest": True}]})
    newest_old = max((m["version"] for m in older["metadatas"]), default=0)
    if older["ids"] and version <= newest_old:
        raise UploadError(
            f"Version {version} is not newer than the indexed version {newest_old}.", 409
        )
    records = [r.model_dump() for r in build_records(entry, path, chunks, {family: version})]
    texts = [r["text"] for r in records]
    vectors = [
        v for i in range(0, len(texts), EMBED_BATCH) for v in embed(texts[i : i + EMBED_BATCH])
    ]
    collection.upsert(
        ids=[r["chunk_id"] for r in records],
        embeddings=vectors,
        documents=texts,
        metadatas=[to_metadata(r) for r in records],
    )
    if older["ids"]:  # FR-9: only now, after the new version is searchable
        collection.update(
            ids=older["ids"], metadatas=[{**m, "is_latest": False} for m in older["metadatas"]]
        )
    return UploadResult(records[0]["doc_id"], len(records), len(older["ids"]))
