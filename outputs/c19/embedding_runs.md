# C19 — Batch embedding runs

Batches of ≤ 100 chunks / ≤ 8,000 tokens · model `gemini-embedding-001` · cost at paid-tier list price.

| Date | Chunks | Cached | Embedded | Requests | Retries | Tokens | Cost | Time | Result |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-21 | 3,528 | 0 | 928 | — | 10 | 304,148 | $0.0456 | ~11 min | stopped by daily quota (resets in 20 h) — free tier counts each chunk as one request, limit 1,000/day |
| 2026-10-24 | 3,528 | 928 | 996 | 52 | 13 | 298,297 | $0.0447 | 783 s | stopped by daily quota (resets in 0 h) |
| 2026-10-24 | 2,824 | 1,924 | 900 | 38 | 10 | 217,840 | $0.0327 | 724 s | complete |
| 2026-10-25 | 3,528 | 2,824 | 704 | 30 | 7 | 177,380 | $0.0266 | 419 s | complete |
