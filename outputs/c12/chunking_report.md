# C12 — Chunking strategies (size 1,600 characters ≈ 400 tokens)

| Document | Strategy | Chunks | Mean chars | Ends at sentence end | Cuts a word |
|---|---|---|---|---|---|
| ppfas-factsheet-2026-09.pdf | fixed | 79 | 1253 | 13% | 35% |
| ppfas-factsheet-2026-09.pdf | recursive | 80 | 1237 | 29% | 0% |
| sebi-master-circular-ia-2026-02.pdf | fixed | 160 | 981 | 24% | 25% |
| sebi-master-circular-ia-2026-02.pdf | recursive | 163 | 962 | 41% | 0% |
| firm-faq.md | fixed | 6 | 223 | 100% | 0% |
| firm-faq.md | recursive | 6 | 223 | 100% | 0% |

## Same SEBI circular, boundary between chunk 5 and chunk 6

**fixed:**

```
ilience Framework (CSCRF) 53
28. Adoption of Standardised, Validated and Exclusive UPI IDs for Payment
Collection by SEBI Registered Intermediaries from Investo
<<< CHUNK BOUNDARY >>>
rs
29. Rights of Persons with Disabilities Act, 2016 and rules made thereunder -
mandatory compliance by all Regulated Entities.
VII. REPORTING REQUIREMENTS
```

**recursive:**

```
g and Retrieval Assistant)
27. Cybersecurity and Cyber Resilience Framework (CSCRF) 53
28. Adoption of Standardised, Validated and Exclusive UPI IDs for Payment
<<< CHUNK BOUNDARY >>>
Collection by SEBI Registered Intermediaries from Investors
29. Rights of Persons with Disabilities Act, 2016 and rules made thereunder -
mandatory compliance b
```
