# C34 — Answer evaluation (40 questions)

| Metric | Value | Target |
|---|---|---|
| K5 correct refusal rate | 90% | ≥ 90% |
| K6 false refusal rate | 0% | ≤ 10% |
| answers with ≥1 resolved citation | 97% | — |
| K8 p95 latency | 15.7 s | ≤ 8 s |

## Per question

| id | slice | expected | got | citations | s |
|---|---|---|---|---|---|
| q01 | factual | answer | answer | 2 | 4.5 |
| q02 | factual | answer | answer | 1 | 2.5 |
| q03 | factual | answer | answer | 1 | 2.5 |
| q04 | factual | answer | answer | 1 | 1.9 |
| q05 | factual | answer | answer | 3 | 2.5 |
| q06 | factual | answer | answer | 2 | 3.3 |
| q07 | factual | answer | answer | 2 | 5.7 |
| q08 | factual | answer | answer | 2 | 2.3 |
| q09 | factual | answer | answer | 2 | 4.3 |
| q10 | factual | answer | answer | 2 | 3.9 |
| q11 | factual | answer | answer | 1 | 2.1 |
| q12 | factual | answer | answer | 1 | 2.5 |
| q13 | factual | answer | answer | 1 | 10.0 |
| q14 | factual | answer | answer | 1 | 2.9 |
| q15 | factual | answer | answer | 2 | 2.4 |
| q16 | factual | answer | answer | 1 | 2.8 |
| q17 | factual | answer | answer | 1 | 32.9 |
| q18 | factual | answer | answer | 0 | 1.8 |
| q19 | factual | answer | answer | 1 | 7.3 |
| q20 | factual | answer | answer | 2 | 2.6 |
| q21 | factual | answer | answer | 2 | 3.9 |
| q22 | factual | answer | answer | 2 | 1.8 |
| q23 | factual | answer | answer | 1 | 3.2 |
| q24 | factual | answer | answer | 1 | 3.0 |
| q25 | factual | answer | answer | 1 | 116.7 |
| q26 | multi_doc | answer | answer | 3 | 3.4 |
| q27 | multi_doc | answer | answer | 2 | 15.6 |
| q28 | multi_doc | answer | answer | 2 | 3.5 |
| q29 | multi_doc | answer | answer | 2 | 15.7 |
| q30 | multi_doc | answer | answer | 2 | 2.8 |
| q31 | unanswerable | no_evidence | no_evidence | 0 | 0.0 |
| q32 | unanswerable | no_evidence | answer | 0 | 4.3 |
| q33 | unanswerable | no_evidence | no_evidence | 0 | 0.0 |
| q34 | unanswerable | no_evidence | no_evidence | 0 | 0.0 |
| q35 | unanswerable | no_evidence | no_evidence | 0 | 0.0 |
| q36 | unanswerable | no_evidence | no_evidence | 0 | 0.0 |
| q37 | advice | advice | advice | 2 | 3.3 |
| q38 | advice | advice | advice | 0 | 0.0 |
| q39 | advice | advice | advice | 0 | 0.0 |
| q40 | advice | advice | advice | 0 | 0.0 |

## Spot check of the 30 answerable answers (reference answer vs. answer text)
- **28 / 30 correct and complete.**
- q18: soft refusal. The CIO's name was in the retrieved context, but the model said "couldn't find it".
- q26: half answered. The Value Fund benchmark chunk was not in the top 5.
- K5 miss: q32 ("NAV of HSBC Value Fund in 2015") was answered instead of refused. Its top cosine score passed the 0.72 threshold.
- K3 / K4: the manual citation review uses `review_sheet.md`. In the spot check no invented facts were found. One weak citation is known: the Value Fund's "1%" exit-load line is cited from p.52, which is a different fund's page.
