# C20 — Embedding sanity checks

## Meaning checks (live API)

| Anchor | Close phrase | sim | Unrelated control | sim | Pass |
|---|---|---|---|---|---|
| exit load | redemption charge for selling units early | 0.676 | the cricket match was stopped by rain | 0.479 | PASS |
| NAV of a mutual fund | net asset value per unit | 0.735 | add two cups of flour to the batter | 0.431 | PASS |
| riskometer | risk level label shown on a scheme | 0.694 | the train leaves platform four at noon | 0.481 | PASS |
| expense ratio | annual fee charged by the fund for management costs | 0.698 | the weather is sunny today | 0.454 | PASS |
| SID | scheme information document of a mutual fund | 0.519 | my phone battery is almost empty | 0.484 | PASS |
| SEBI | Securities and Exchange Board of India, the market regulator | 0.766 | a recipe for chocolate cake | 0.400 | PASS |

Smallest margin between close and unrelated: **0.035**

## Vector store checks (2,824 vectors)

| Check | Result |
|---|---|
| one vector per chunk | FAIL |
| every vector has 768 dimensions | PASS |
| no NaN or infinite values | PASS |
| all vectors unit-length | PASS |
| identical texts get identical vectors | PASS |

**Status:** "one vector per chunk" fails *on purpose*: it compares vectors with all 3,528 chunks, and 704 chunks are still waiting.
- All 704 belong to the 1,395-chunk SEBI Master Circular for MFs, the largest document (smallest documents are embedded first).
- They are left for the next free-tier quota window (1,000 embeddings a day).
- All 20 documents have vectors; 19 of them are complete.
