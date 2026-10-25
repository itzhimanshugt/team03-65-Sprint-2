# C34 — Answer evaluation (40 questions)

| Metric | Value | Target |
|---|---|---|
| K5 correct refusal rate | 90% | ≥ 90% |
| K6 false refusal rate | 0% | ≤ 10% |
| answers with ≥1 resolved citation | 97% | — |
| K8 p95 latency | 11.1 s | ≤ 8 s |

## Per question

| id | slice | expected | got | citations | s |
|---|---|---|---|---|---|
| q01 | factual | answer | answer | 2 | 4.7 |
| q02 | factual | answer | answer | 2 | 2.1 |
| q03 | factual | answer | answer | 1 | 1.7 |
| q04 | factual | answer | answer | 1 | 1.2 |
| q05 | factual | answer | answer | 2 | 1.6 |
| q06 | factual | answer | answer | 2 | 2.2 |
| q07 | factual | answer | answer | 2 | 1.6 |
| q08 | factual | answer | answer | 2 | 1.2 |
| q09 | factual | answer | answer | 2 | 2.4 |
| q10 | factual | answer | answer | 2 | 9.5 |
| q11 | factual | answer | answer | 1 | 1.8 |
| q12 | factual | answer | answer | 1 | 3.2 |
| q13 | factual | answer | answer | 1 | 1.9 |
| q14 | factual | answer | answer | 2 | 1.7 |
| q15 | factual | answer | answer | 2 | 168.6 |
| q16 | factual | answer | answer | 1 | 16.6 |
| q17 | factual | answer | answer | 1 | 4.6 |
| q18 | factual | answer | answer | 1 | 7.4 |
| q19 | factual | answer | answer | 1 | 6.0 |
| q20 | factual | answer | answer | 2 | 3.4 |
| q21 | factual | answer | answer | 2 | 7.5 |
| q22 | factual | answer | answer | 2 | 5.6 |
| q23 | factual | answer | answer | 1 | 11.1 |
| q24 | factual | answer | answer | 1 | 2.2 |
| q25 | factual | answer | answer | 1 | 1.6 |
| q26 | multi_doc | answer | answer | 0 | 2.1 |
| q27 | multi_doc | answer | answer | 2 | 3.6 |
| q28 | multi_doc | answer | answer | 2 | 7.8 |
| q29 | multi_doc | answer | answer | 2 | 4.3 |
| q30 | multi_doc | answer | answer | 2 | 8.1 |
| q31 | unanswerable | no_evidence | no_evidence | 0 | 0.0 |
| q32 | unanswerable | no_evidence | answer | 0 | 4.0 |
| q33 | unanswerable | no_evidence | no_evidence | 0 | 0.0 |
| q34 | unanswerable | no_evidence | no_evidence | 0 | 0.0 |
| q35 | unanswerable | no_evidence | no_evidence | 0 | 0.0 |
| q36 | unanswerable | no_evidence | no_evidence | 0 | 0.0 |
| q37 | advice | advice | advice | 7 | 1.8 |
| q38 | advice | advice | advice | 0 | 0.0 |
| q39 | advice | advice | advice | 0 | 0.0 |
| q40 | advice | advice | advice | 0 | 0.0 |

## Spot check of the 30 answerable answers (full index, 3,528 chunks, 25 Oct 2026)
- **29 / 30 correct and complete.** q13, q20 and q29 are correct but worded differently from the reference.
- Still missing: q26, a two-fund comparison. The Value Fund benchmark chunk is not in the top 5, and the model says it couldn't find it (a soft refusal, not an invented answer).
- K5 miss unchanged: q32 ("NAV of HSBC Value Fund in 2015") was answered instead of refused.
- K3 / K4 were reviewed in `k3_k4_review.md` on the 24 Oct run (2,824 chunks). This re-run was not re-reviewed citation by citation.
