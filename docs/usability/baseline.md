# Baseline: how long does it take without VerifAI? (#43)

## 1. Timed manual lookup (10 questions)

**Setup.** Put the approved documents from `data/raw/` in one folder, the way an advisor's shared drive holds them. No VerifAI and no web search. The PDF viewer's own search (Ctrl+F) is fine; advisors use it too.

**For each question:** start a stopwatch, find the answer, and note the document and page you'd cite. Stop when you'd be confident telling a client. Record minutes (one decimal) in `results/baseline.csv` with the question id (`B1`…`B10`).

| # | Question |
|---|---|
| B1 | What is the benchmark of HSBC Large Cap Fund? |
| B2 | When was HSBC Value Fund launched? |
| B3 | What is the AUM of HSBC Small Cap Fund? |
| B4 | Who are the fund managers of HSBC Small Cap Fund? |
| B5 | What is the exit load of HSBC Value Fund? |
| B6 | What is the benchmark of Parag Parikh Flexi Cap Fund? |
| B7 | What is the exit load of Parag Parikh Liquid Fund on day 1? |
| B8 | Who bears the cost of intraday borrowing by a mutual fund scheme? |
| B9 | Which certification is needed to distribute SIF products? |
| B10 | Which phrases must advisors never use for a mutual fund scheme? |

<details><summary>Answer key (check after timing)</summary>

| # | Answer | Source |
|---|---|---|
| B1 | Nifty 100 TRI | hsbc-factsheet-2026-08.pdf p. 11 |
| B2 | 08 January 2010 | hsbc-factsheet-2026-08.pdf p. 39 |
| B3 | ₹ 19,076.35 Cr (31 Aug 2026) | hsbc-factsheet-2026-08.pdf p. 29 |
| B4 | Venugopal Manghat, Mayank Chaturvedi, Dipan S. Parikh | hsbc-factsheet-2026-08.pdf p. 29 |
| B5 | Nil up to 10% of units within 1 year; 1% above that within 1 year; Nil after 1 year | hsbc-factsheet-2026-08.pdf p. 39 |
| B6 | NIFTY 500 (TRI) | ppfas-factsheet-2026-09.pdf p. 2 |
| B7 | 0.0070% of redemption proceeds | ppfas-liquid-kim.pdf p. 13 |
| B8 | The AMC | sebi-circular-mf-intraday-borrowing-2026-07.pdf p. 3 |
| B9 | NISM Series-V-D (Specialized Investment Fund Distributors) | sebi-circular-sif-distribution-2026-07.pdf p. 2 |
| B10 | guaranteed returns, risk-free, sure-shot, can't lose | client-communication-guidelines.md |

</details>

Mark `correct = 1` only if the answer matches the key **and** came from the current version (the August 2026 HSBC factsheet, not July). A wrong-version answer is exactly the compliance risk PRD §1.2 sizes at 10%.

## 2. Short interviews (5 people)

Five minutes each, with advisors, relationship managers or finance students who have done client-facing work. Record in `results/interviews.csv`.

1. On a typical day, how many client questions do you check against a document before answering? → `checks_per_day`
2. Where do you look first? → `where`
3. Roughly how long does one check take, in minutes? → `minutes_per_check`
4. In the last month, did you ever answer from an older document version? (yes / no / unsure) → `outdated`
5. What would make you trust an automated answer? → `trust`

Don't suggest numbers. If they say "it depends", ask about yesterday.
