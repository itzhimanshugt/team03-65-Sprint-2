# C14 — Token-aware chunk sizing and overlap

Target: 400 tokens per chunk (8-token safety margin), 60-token overlap. Sizes measured exactly with tiktoken after chunking.

| Chunking | Chunks | Mean tokens | Max tokens | <100 | 100–199 | 200–299 | 300–399 | ≥400 |
|---|---|---|---|---|---|---|---|---|
| 1,600 characters (C12) | 3,278 | 279 | 869 | 20% | 14% | 16% | 29% | 21% |
| 400 tokens + overlap (C14) | 3,528 | 282 | 392 | 12% | 13% | 12% | 62% | 0% |

Neighbouring chunks on the same page that share overlap text: **1,594 of 2,085 (76%)**. The rest meet at a boundary where the last piece is longer than 60 tokens, so it can't be repeated.
