# C23 — Similarity search, top-5 (latest versions only)

Live run on 21 Oct 2026 against the index built in C22. The index held 928 chunks from the two HSBC factsheets; the rest of the corpus was still waiting for embedding quota. Only the **August** (latest) factsheet appears: the July version is excluded by the default `is_latest` filter.

## What is the exit load of HSBC Value Fund?

| # | Score | Source | Chunk (start) |
|---|---|---|---|
| 1 | 0.798 | hsbc-factsheet-2026-08.pdf · p.39 | HSBC Value Fund Type of Scheme: An open ended equity scheme following a value investment s… |
| 2 | 0.755 | hsbc-factsheet-2026-08.pdf · p.52 | Load Structure Exit Load: i. If the units redeemed or switched out are up to 10% of the un… |
| 3 | 0.733 | hsbc-factsheet-2026-08.pdf · p.46 | the page. Load Structure Exit Load:If the units redeemed or switched out are upto 10% of t… |
| 4 | 0.731 | hsbc-factsheet-2026-08.pdf · p.96 | ID HSBC Mutual Fund The risk of the schem e i s Very High Ri sk… |
| 5 | 0.730 | hsbc-factsheet-2026-08.pdf · p.83 | Managing Since Jun 30, 2014 / Jul 15, 2023 / Feb 01, 2025/ Aug 26, 2026 Minimum Investment… |

## Who is the fund manager of HSBC Small Cap Fund?

| # | Score | Source | Chunk (start) |
|---|---|---|---|
| 1 | 0.798 | hsbc-factsheet-2026-08.pdf · p.29 | HSBC Small Cap Fund Type of Scheme: An open ended equity scheme predominantly investing in… |
| 2 | 0.741 | hsbc-factsheet-2026-08.pdf · p.30 | HSBC Small Cap Fund Major Changes w.r.t previous months - (July 2026)… |
| 3 | 0.739 | hsbc-factsheet-2026-08.pdf · p.32 | Past Performance is not an indicator or guarantee of future results 32 Industry Allocation… |
| 4 | 0.737 | hsbc-factsheet-2026-08.pdf · p.31 | Additional Disclosure Past Performance is not an indicator or guarantee of future results… |
| 5 | 0.734 | hsbc-factsheet-2026-08.pdf · p.25 | HSBC Multi Cap Fund Type of Scheme: An open endedequity scheme investing across large cap,… |

## What is the riskometer level of HSBC Liquid Fund?

| # | Score | Source | Chunk (start) |
|---|---|---|---|
| 1 | 0.790 | hsbc-factsheet-2026-08.pdf · p.111 | HSBC Liquid Fund Type of Scheme: An open ended Liquid Scheme. Relatively Low interest rate… |
| 2 | 0.789 | hsbc-factsheet-2026-08.pdf · p.113 | HSBC Liquid Fund As per clause 7.22 of the SEBI Master Circular for Mutual Funds… |
| 3 | 0.775 | hsbc-factsheet-2026-08.pdf · p.111 | 3.35 5.66 7.20 7.31 6.12 3.43 5.75 7.31 7.41 6.22… |
| 4 | 0.761 | hsbc-factsheet-2026-08.pdf · p.111 | Scheme Returns % - Regular Scheme Returns % - Direct Benchmark Returns %… |
| 5 | 0.752 | hsbc-factsheet-2026-08.pdf · p.108 | ID HSBC Mutual Fund The risk of the scheme is Low Risk The risk of the benchmark is Low Ri… |

**What this shows:** the fund's own page ranks first for every question. Hit 2 for the exit-load question is a real exit-load clause, but of a *neighbouring* fund's page. Pure vector search knows "this is about exit loads", not "this is HSBC Value Fund's exit load", which is the gap that C24 (hybrid keyword + metadata) and C26 (re-ranking) address.
