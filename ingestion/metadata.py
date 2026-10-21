"""Attach source and position metadata to every chunk (PRD §6.3) so answers can cite it."""

import hashlib
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from app.tokens import count_tokens

APPROVED_BY = "compliance-desk (simulated)"


class ChunkRecord(BaseModel):
    chunk_id: str  # f"{doc_id}-{chunk_index:04d}"
    doc_id: str  # first 12 hex chars of the file's SHA-256: same file, same id
    chunk_index: int = Field(ge=0)
    text: str = Field(min_length=1)
    source_name: str
    title: str
    doc_type: Literal["factsheet", "sid_kim", "circular", "research", "internal"]
    issuer: str
    family: str  # versions of the same document share a family
    published_date: date
    version: int = Field(ge=1)
    is_latest: bool
    approved_by: str
    approved_at: datetime
    page: int = Field(ge=1)  # PDF page, or section number for HTML/MD/TXT
    token_count: int = Field(ge=1)
    checksum: str = Field(min_length=64, max_length=64)


def file_checksum(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def latest_versions(catalog: list[dict]) -> dict[str, int]:
    """Highest version per family; anything older is not the latest."""
    latest: dict[str, int] = {}
    for entry in catalog:
        latest[entry["family"]] = max(latest.get(entry["family"], 0), int(entry["version"]))
    return latest


def build_records(
    entry: dict, path: str | Path, chunks: list[tuple[int, str]], latest: dict[str, int]
) -> list[ChunkRecord]:
    """Turn one document's (position, text) chunks into validated ChunkRecords."""
    checksum = file_checksum(path)
    doc_id = checksum[:12]
    approved_at = datetime.now(UTC)
    return [
        ChunkRecord(
            chunk_id=f"{doc_id}-{i:04d}",
            doc_id=doc_id,
            chunk_index=i,
            text=text,
            source_name=Path(path).name,
            title=entry["title"],
            doc_type=entry["doc_type"],
            issuer=entry["issuer"],
            family=entry["family"],
            published_date=entry["published_date"],
            version=int(entry["version"]),
            is_latest=int(entry["version"]) == latest[entry["family"]],
            approved_by=APPROVED_BY,
            approved_at=approved_at,
            page=page,
            token_count=count_tokens(text),
            checksum=checksum,
        )
        for i, (page, text) in enumerate(chunks)
    ]
