# C25 — Retrieval tuning

## Top-k

| k | Recall@k | Precision@k | MRR@k |
|---|---|---|---|
| 3 | 0.82 | 0.31 | 0.70 |
| 5 | 0.83 | 0.20 | 0.70 |
| 8 | 0.85 | 0.13 | 0.70 |

## Evidence threshold (refuse if top cosine < t)

| t | Unanswerable refused (K5 part) | Answerable wrongly refused (K6) |
|---|---|---|
| 0.45 | 0% | 0% |
| 0.55 | 0% | 0% |
| 0.60 | 0% | 0% |
| 0.65 | 50% | 0% |
| 0.70 | 67% | 0% |
| 0.72 | 83% | 0% |
| 0.75 | 83% | 3% |

Top cosine per question:

- factual: 0.788 — What is the benchmark of HSBC Large Cap Fund?
- factual: 0.811 — What is the benchmark of HSBC Midcap Fund?
- factual: 0.789 — What is the benchmark of HSBC Small Cap Fund?
- factual: 0.756 — What is the benchmark of HSBC Infrastructure Fund?
- factual: 0.797 — What is the benchmark of HSBC Liquid Fund?
- factual: 0.799 — What is the benchmark of HSBC Overnight Fund?
- factual: 0.779 — What is the benchmark of HSBC Gilt Fund?
- factual: 0.792 — When was HSBC Value Fund launched?
- factual: 0.806 — What is the inception date of HSBC Midcap Fund?
- factual: 0.763 — What is the allotment date of HSBC Credit Risk Fund?
- factual: 0.803 — What is the AUM of HSBC Small Cap Fund?
- factual: 0.797 — What is the AUM of HSBC Liquid Fund?
- factual: 0.790 — What is the riskometer level of HSBC Liquid Fund?
- factual: 0.790 — Who are the fund managers of HSBC Small Cap Fund?
- factual: 0.798 — What is the exit load of HSBC Value Fund?
- factual: 0.796 — When was Parag Parikh Flexi Cap Fund launched?
- factual: 0.788 — What is the benchmark of Parag Parikh Flexi Cap Fund?
- factual: 0.754 — Who is the Chief Investment Officer managing Parag Parikh Flexi Cap Fund?
- factual: 0.793 — What is the inception date of Parag Parikh ELSS Tax Saver Fund?
- factual: 0.795 — What is the exit load of Parag Parikh Liquid Fund on day 1?
- factual: 0.779 — What is the benchmark of Parag Parikh Liquid Fund?
- factual: 0.756 — Who bears the cost of intraday borrowing by a mutual fund scheme?
- factual: 0.721 — Which certification is needed to distribute SIF products?
- factual: 0.861 — How soon does compliance upload a new monthly factsheet?
- factual: 0.862 — Which phrases must advisors never use for a mutual fund scheme?
- multi_doc: 0.753 — Compare the benchmarks of HSBC Value Fund and HSBC Large Cap Fund.
- multi_doc: 0.779 — Which is older, HSBC Midcap Fund or HSBC Small Cap Fund?
- multi_doc: 0.776 — Compare the benchmarks of HSBC Liquid Fund and Parag Parikh Liquid Fund.
- multi_doc: 0.753 — When were HSBC Flexi Cap Fund and Parag Parikh Flexi Cap Fund launched?
- multi_doc: 0.785 — Compare the AUM of HSBC Small Cap Fund and HSBC Midcap Fund.
- unanswerable: 0.642 — What is the fund manager's personal portfolio?
- unanswerable: 0.766 — What was the NAV of HSBC Value Fund in 2015?
- unanswerable: 0.713 — What is the exit load of SBI Bluechip Fund?
- unanswerable: 0.666 — Has SEBI approved a Bitcoin ETF?
- unanswerable: 0.648 — What is the salary of the PPFAS CEO?
- unanswerable: 0.645 — What will the Nifty 50 close at tomorrow?
- advice: 0.765 — Should my client switch from HSBC Value Fund to HSBC Small Cap Fund?
- advice: 0.618 — Which is the best fund for retirement?
- advice: 0.672 — Can you recommend a liquid fund for my client?
- advice: 0.658 — Is now a good time to invest in small caps?
