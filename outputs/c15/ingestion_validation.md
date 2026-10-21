# C15 — Corpus ingestion and validation

**20/20 documents · 3,528 chunks · 65 s total**

## Validation checks

| Check | Result |
|---|---|
| Every catalogued document loaded | PASS |
| Every loaded document produced chunks | PASS |
| No empty chunks | PASS |
| No chunk over 400 tokens | PASS |
| Chunk IDs unique | PASS |
| No duplicate documents (same checksum) | PASS |
| Exactly one latest version per family | PASS |

## KPIs

| KPI | Target | Measured |
|---|---|---|
| K9 Ingestion completeness | 100% of corpus docs with all metadata | 100% |
| K10 Ingestion speed (load to chunks, per 50 PDF pages, median) | ≤ 60 s | 1.4 s |

K10 here covers load, clean, chunk and metadata. Embedding and indexing time is added in C22.

## Per document

| Document | Pages/sections | Chunks | Time |
|---|---|---|---|
| hsbc-factsheet-2026-07.pdf | 91 | 532 | 7.1 s |
| hsbc-factsheet-2026-08.pdf | 189 | 730 | 29.3 s |
| ppfas-factsheet-2026-08.pdf | 32 | 102 | 1.2 s |
| ppfas-factsheet-2026-09.pdf | 32 | 103 | 1.0 s |
| ppfas-liquid-kim.pdf | 34 | 118 | 3.5 s |
| ppfas-liquid-sid.pdf | 75 | 175 | 2.2 s |
| sebi-master-circular-mf-2026-03.pdf | 748 | 1395 | 18.7 s |
| sebi-master-circular-ia-2025-06.pdf | 94 | 120 | 1.2 s |
| sebi-master-circular-ia-2026-02.pdf | 99 | 137 | 1.2 s |
| sebi-circular-mf-intraday-borrowing-2026-07.pdf | 3 | 4 | 0.0 s |
| sebi-circular-mf-swp-stp-demat-2026-07.pdf | 2 | 4 | 0.0 s |
| sebi-circular-sif-distribution-2026-07.pdf | 3 | 4 | 0.0 s |
| sebi-investor-education-mutual-funds.html | 2 | 60 | 0.0 s |
| sebi-riskometer.html | 6 | 6 | 0.0 s |
| motilal-exit-load.html | 10 | 11 | 0.0 s |
| tata-riskometer.html | 8 | 12 | 0.0 s |
| zerodha-ratios.html | 1 | 1 | 0.0 s |
| firm-faq.md | 6 | 6 | 0.0 s |
| client-communication-guidelines.md | 7 | 7 | 0.0 s |
| product-shelf-notes.txt | 1 | 1 | 0.0 s |
