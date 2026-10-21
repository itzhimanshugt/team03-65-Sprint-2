"""Embed many chunks in batches, surviving rate limits and skipping work already done."""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from openai import RateLimitError

from app.llm import retry_delay_seconds
from app.tokens import estimate_cost
from embeddings.embedder import embed_texts

MAX_RETRIES = 5
TOKEN_BUDGET = 8_000  # per request; the free tier also limits tokens per minute
UNKNOWN_WAIT = 60  # a 429 without a stated delay is treated as the per-minute limit


@dataclass
class BatchReport:
    total: int = 0
    skipped: int = 0
    embedded: int = 0
    requests: int = 0
    retries: int = 0
    tokens: int = 0
    seconds: float = 0.0
    waits: list[float] = field(default_factory=list)

    def cost(self, model: str) -> float:
        return estimate_cost(model, self.tokens)


class VectorCache:
    """chunk_id -> vector, stored as embedding_ids.json + embeddings.npy."""

    def __init__(self, folder: str | Path):
        self.ids_path, self.vec_path = (
            Path(folder) / "embedding_ids.json",
            Path(folder) / "embeddings.npy",
        )
        self.ids: list[str] = (
            json.loads(self.ids_path.read_text()) if self.ids_path.exists() else []
        )
        self.vectors = np.load(self.vec_path) if self.vec_path.exists() else None

    def add(self, ids: list[str], vectors: list[list[float]]) -> None:
        new = np.asarray(vectors, dtype=np.float32)
        self.vectors = new if self.vectors is None else np.vstack([self.vectors, new])
        self.ids += ids
        self.ids_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(self.vec_path, self.vectors)
        self.ids_path.write_text(json.dumps(self.ids))


def embed_records(
    records: list[dict],
    cache: VectorCache,
    batch_size: int = 100,
    token_budget: int = TOKEN_BUDGET,
    embed=embed_texts,
    sleep=time.sleep,
    log=print,
    report: BatchReport | None = None,
) -> BatchReport:
    """Embed records ({chunk_id, text, token_count}) missing from the cache, batch by batch."""
    start = time.perf_counter()
    done = set(cache.ids)
    todo = [r for r in records if r["chunk_id"] not in done]
    # A caller-supplied report keeps the numbers even if a daily-quota error stops the run.
    rep = report or BatchReport()
    rep.total, rep.skipped = len(records), len(records) - len(todo)
    batches, current, tokens = [], [], 0
    for r in todo:  # at most `batch_size` chunks and `token_budget` tokens per request
        if current and (len(current) == batch_size or tokens + r["token_count"] > token_budget):
            batches.append(current)
            current, tokens = [], 0
        current.append(r)
        tokens += r["token_count"]
    if current:
        batches.append(current)
    for batch in batches:
        for attempt in range(MAX_RETRIES + 1):
            try:
                rep.requests += 1
                vectors = embed([r["text"] for r in batch])
                break
            except RateLimitError as error:
                wait = retry_delay_seconds(str(error)) or UNKNOWN_WAIT
                if attempt == MAX_RETRIES or wait > 90:
                    raise  # daily quota or persistent limit: stop; progress is already saved
                rep.retries += 1
                rep.waits.append(wait)
                log(f"rate limited, waiting {wait:.0f}s")
                sleep(wait + 1)
        cache.add([r["chunk_id"] for r in batch], vectors)  # saved after every batch
        rep.embedded += len(batch)
        rep.seconds = time.perf_counter() - start
        rep.tokens += sum(r["token_count"] for r in batch)
        log(f"{rep.skipped + rep.embedded}/{rep.total} chunks")
    rep.seconds = time.perf_counter() - start
    return rep
