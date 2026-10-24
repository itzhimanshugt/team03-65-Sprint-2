# C34 — Answer evaluation (40 questions)

| Metric | Value | Target |
|---|---|---|
| K5 correct refusal rate | 90% | ≥ 90% |
| K6 false refusal rate | 0% | ≤ 10% |
| answers with ≥1 resolved citation | 97% | — |
| K8 p95 latency | 12.2 s | ≤ 8 s |

## Per question

| id | slice | expected | got | citations | s |
|---|---|---|---|---|---|
| q01 | factual | answer | answer | 2 | 5.6 |
| q02 | factual | answer | answer | 2 | 3.2 |
| q03 | factual | answer | answer | 1 | 3.5 |
| q04 | factual | answer | answer | 1 | 5.5 |
| q05 | factual | answer | answer | 2 | 3.2 |
| q06 | factual | answer | answer | 2 | 2.9 |
| q07 | factual | answer | answer | 2 | 2.9 |
| q08 | factual | answer | answer | 2 | 3.1 |
| q09 | factual | answer | answer | 2 | 18.3 |
| q10 | factual | answer | answer | 2 | 5.4 |
| q11 | factual | answer | answer | 1 | 11.0 |
| q12 | factual | answer | answer | 1 | 4.2 |
| q13 | factual | answer | answer | 1 | 20.4 |
| q14 | factual | answer | answer | 2 | 3.2 |
| q15 | factual | answer | answer | 2 | 8.5 |
| q16 | factual | answer | answer | 1 | 3.9 |
| q17 | factual | answer | answer | 1 | 3.0 |
| q18 | factual | answer | answer | 1 | 3.0 |
| q19 | factual | answer | answer | 1 | 5.3 |
| q20 | factual | answer | answer | 2 | 12.2 |
| q21 | factual | answer | answer | 2 | 5.8 |
| q22 | factual | answer | answer | 2 | 2.5 |
| q23 | factual | answer | answer | 1 | 2.9 |
| q24 | factual | answer | answer | 1 | 5.2 |
| q25 | factual | answer | answer | 1 | 4.1 |
| q26 | multi_doc | answer | answer | 0 | 3.3 |
| q27 | multi_doc | answer | answer | 2 | 3.8 |
| q28 | multi_doc | answer | answer | 2 | 5.3 |
| q29 | multi_doc | answer | answer | 2 | 4.1 |
| q30 | multi_doc | answer | answer | 2 | 3.2 |
| q31 | unanswerable | no_evidence | no_evidence | 0 | 0.1 |
| q32 | unanswerable | no_evidence | answer | 0 | 5.5 |
| q33 | unanswerable | no_evidence | no_evidence | 0 | 0.1 |
| q34 | unanswerable | no_evidence | no_evidence | 0 | 0.1 |
| q35 | unanswerable | no_evidence | no_evidence | 0 | 0.1 |
| q36 | unanswerable | no_evidence | no_evidence | 0 | 0.1 |
| q37 | advice | advice | advice | 4 | 3.6 |
| q38 | advice | advice | advice | 0 | 0.1 |
| q39 | advice | advice | advice | 0 | 0.1 |
| q40 | advice | advice | advice | 0 | 0.1 |

## Spot check of the 30 answerable answers (re-run with same-page neighbour chunks)
- **29 / 30 correct and complete** (was 28 / 30).
- q18 is fixed: the PPFAS CIO answer now names Mr. Rajeev Thakkar.
- q26 is still a miss. The Value Fund benchmark chunk is not in the top 5 of a two-fund comparison, and the model says it couldn't find it. That is a soft refusal; there was no invented answer.
- Weak citation fixed: the HSBC Value Fund exit load now cites only **p.39** (both halves of the page). Before, the "1%" line came from p.52, another fund's page.
- K5 miss unchanged: q32 ("NAV of HSBC Value Fund in 2015") was answered instead of refused.
