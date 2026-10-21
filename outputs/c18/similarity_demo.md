# C18 — Similarity metrics

Question: _What is the exit load of Parag Parikh Flexi Cap Fund?_

| Chunk | Source | Cosine | Dot | Euclidean |
|---|---|---|---|---|
| `6fde0dc4cd3e-0003` | ppfas-factsheet-2026-09.pdf · p.2 | 0.593 | 0.593 | 0.902 |
| `6402ffa74560-0000` | sebi-master-circular-mf-2026-03.pdf · p.1 | 0.535 | 0.535 | 0.965 |
| `d15820b5bf72-0000` | firm-faq.md · p.1 | 0.423 | 0.423 | 1.075 |
| `a138e0c8b834-0000` | motilal-exit-load.html · p.1 | 0.406 | 0.406 | 1.090 |
| `45d975910d18-0000` | product-shelf-notes.txt · p.1 | 0.544 | 0.544 | 0.955 |

Ranking (most similar first):

- **cosine:** ppfas-factsheet-2026-09.pdf → product-shelf-notes.txt → sebi-master-circular-mf-2026-03.pdf → firm-faq.md → motilal-exit-load.html
- **dot:** ppfas-factsheet-2026-09.pdf → product-shelf-notes.txt → sebi-master-circular-mf-2026-03.pdf → firm-faq.md → motilal-exit-load.html
- **euclidean:** ppfas-factsheet-2026-09.pdf → product-shelf-notes.txt → sebi-master-circular-mf-2026-03.pdf → firm-faq.md → motilal-exit-load.html

Vectors are L2-normalised in `embed_texts` (truncated 768-dim Gemini vectors are not unit-length on their own), so cosine = dot and Euclidean = sqrt(2 − 2·cosine): all three metrics give the same ranking.
