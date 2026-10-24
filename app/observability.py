"""Query cache, JSONL request log and usage stats (C39). The log never holds keys or secrets."""

import hashlib
import json
import time
from pathlib import Path

LOG = Path("data/logs/requests.jsonl")


def cache_key(question: str, history: list, filters: dict) -> str:
    raw = json.dumps([question.strip().lower(), history, filters], sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


class QueryCache:
    def __init__(self, max_items: int = 500):
        self.items: dict[str, dict] = {}
        self.max_items = max_items

    def get(self, key: str) -> dict | None:
        return self.items.get(key)

    def put(self, key: str, value: dict) -> None:
        if len(self.items) >= self.max_items:
            self.items.pop(next(iter(self.items)))  # drop the oldest
        self.items[key] = value


def log_request(entry: dict, path: Path = LOG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), **entry}) + "\n")


def stats(path: Path = LOG) -> dict:
    rows = (
        [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        if path.exists()
        else []
    )
    lat = sorted(r["latency_s"] for r in rows if not r.get("cached"))
    p95 = lat[min(len(lat) - 1, round(0.95 * (len(lat) - 1)))] if lat else 0.0
    return {
        "requests": len(rows),
        "cache_hits": sum(bool(r.get("cached")) for r in rows),
        "refusals": sum(bool(r.get("refusal")) for r in rows),
        "p95_latency_s": round(p95, 2),
    }
