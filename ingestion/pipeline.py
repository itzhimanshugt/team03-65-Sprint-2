"""Run load → clean → chunk → metadata over the catalog, then validate the result."""

import csv
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from ingestion.chunker import chunk_by_tokens
from ingestion.cleaner import clean_document
from ingestion.loaders import UnsupportedDocumentError, load_document
from ingestion.metadata import ChunkRecord, build_records, latest_versions


@dataclass
class DocResult:
    source: str
    pages: int = 0
    chunks: int = 0
    seconds: float = 0.0
    error: str = ""


@dataclass
class IngestResult:
    records: list[ChunkRecord] = field(default_factory=list)
    docs: list[DocResult] = field(default_factory=list)


def ingest_catalog(catalog_path: str | Path = "data/catalog.csv") -> IngestResult:
    catalog = list(csv.DictReader(open(catalog_path, encoding="utf-8")))
    latest = latest_versions(catalog)
    result = IngestResult()
    for entry in catalog:
        path = Path(catalog_path).parent / entry["filename"]
        start = time.perf_counter()
        doc_result = DocResult(source=path.name)
        try:
            doc, _ = clean_document(load_document(path))
            records = build_records(entry, path, chunk_by_tokens(doc), latest)
            result.records += records
            doc_result.pages, doc_result.chunks = len(doc.pages), len(records)
        except (UnsupportedDocumentError, FileNotFoundError) as error:
            doc_result.error = str(error)
        doc_result.seconds = time.perf_counter() - start
        result.docs.append(doc_result)
    return result


def validate(result: IngestResult, max_tokens: int = 400) -> dict[str, list[str]]:
    """Each check maps to the list of problems found; an empty list means the check passed."""
    records = result.records
    families = Counter(r.family for r in records if r.is_latest and r.chunk_index == 0)
    family_names = {r.family for r in records}
    checksums = Counter(r.checksum for r in records if r.chunk_index == 0)
    return {
        "Every catalogued document loaded": [
            f"{d.source}: {d.error}" for d in result.docs if d.error
        ],
        "Every loaded document produced chunks": [
            d.source for d in result.docs if not d.error and d.chunks == 0
        ],
        "No empty chunks": [r.chunk_id for r in records if not r.text.strip()],
        f"No chunk over {max_tokens} tokens": [
            f"{r.chunk_id} ({r.token_count})" for r in records if r.token_count > max_tokens
        ],
        "Chunk IDs unique": [
            cid for cid, n in Counter(r.chunk_id for r in records).items() if n > 1
        ],
        "No duplicate documents (same checksum)": [c[:12] for c, n in checksums.items() if n > 1],
        "Exactly one latest version per family": [
            f for f in family_names if families.get(f, 0) != 1
        ],
    }
