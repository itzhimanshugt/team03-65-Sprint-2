# C22 — Indexing report

**2,824 of 3,528 chunks indexed** from 20 documents in 10.5 s (the rest are waiting for embeddings; re-running adds them without duplicates).

| Check | Result |
|---|---|
| indexed rows = cached vectors | PASS |
| every chunk with a vector is indexed | PASS |
| metadata round-trips (page, source, version, latest) | PASS |
| stored text matches the chunk | PASS |
| self-retrieval (sample of 25) | FAIL |
