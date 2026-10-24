# C27 — Retrieval evaluation (k=5, 30 answerable questions, 2,824 chunks indexed)

| Retriever | Slice | Recall@5 | Precision@5 | MRR@5 |
|---|---|---|---|---|
| vector | factual | 0.84 | 0.18 | 0.73 |
| vector | multi_doc | 0.80 | 0.32 | 0.53 |
| vector | all | 0.83 | 0.20 | 0.70 |
| hybrid (BM25 + vector, RRF) | factual | 0.64 | 0.13 | 0.44 |
| hybrid (BM25 + vector, RRF) | multi_doc | 0.20 | 0.08 | 0.10 |
| hybrid (BM25 + vector, RRF) | all | 0.57 | 0.12 | 0.38 |
