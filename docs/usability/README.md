# Usability kit (issues #43 and #44)

Two short studies that replace the PRD's assumed numbers with measured ones. Every figure in the final KPI table comes from `results/*.csv` through `python -m scripts.usability_report`, never typed in by hand.

| Study | Issue | What you measure | Time | File |
|---|---|---|---|---|
| Manual lookup baseline | #43 | Minutes to find and verify 10 answers **without** VerifAI | 30–60 min, one person | [baseline.md](baseline.md) |
| Advisor interviews | #43 | Questions per day that need a document check | 5 × 5 min | [baseline.md](baseline.md#2-short-interviews-5-people) |
| Usability test | #44 | Seconds to a verified answer **with** VerifAI (K7), and SUS (K11) | 5 × 15 min | [usability-test.md](usability-test.md), [sus.md](sus.md) |

## Order

1. Do the baseline lookup yourself first.
2. Run the 5 interviews and the 5 usability sessions with the same people if you can: interview, then the tasks, then SUS.
3. Type the results into the CSVs in [`results/`](results/). The headers are already there.
4. Run `python -m scripts.usability_report`. It prints the KPI table (baseline minutes, questions per day, K7, K11). Paste it into the README's **Usability results** section and PRD §1.2, then close #43 and #44.

## Rules that keep the numbers honest

- Record what happened, including failures and give-ups (`success = 0`, time = when they gave up).
- Don't help during a task. If a participant asks, say "do what you would do at work".
- Use the live site, https://verifai-vysj.onrender.com. Open it a minute before each session so the free instance is awake; a cold start is not part of the task time.
