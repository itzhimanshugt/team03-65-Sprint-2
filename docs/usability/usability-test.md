# Usability test: time to a verified answer and SUS (#44)

- **K7:** median seconds from starting to type a question to reading a cited answer. Target **≤ 60 s**.
- **K11:** SUS score. Target **≥ 70**.
- 5 participants × 5 tasks (the PRD's minimum is 3).

## Before each session (2 min)

- Open https://verifai-vysj.onrender.com and ask one warm-up question yourself so the free instance and the model are awake. Then press **New session**.
- Read the participant this, word for word:

  > You're an advisor. A client asks you something and you want a verified answer before you reply. Use this tool the way you would at work. I can't help during the tasks. Say "done" when you'd be confident answering the client, and tell me which document and page you'd cite.

## Tasks

Start the stopwatch when they start typing or clicking. Stop when they say "done" **and** name the document and page. Record seconds in `results/tasks.csv` with the task id (`T1`…`T5`).

| Task | Say to the participant | Success when they… |
|---|---|---|
| T1 | "Your client asks for the benchmark of HSBC Infrastructure Fund." | say Nifty Infrastructure TRI and cite the HSBC August 2026 factsheet, p. 36 |
| T2 | "When did Parag Parikh ELSS Tax Saver Fund start?" | say 24 July 2019 and cite the PPFAS September 2026 factsheet, p. 6 |
| T3 | "What's the AUM of HSBC Liquid Fund?" then, after they answer, "And how risky is it?" | give ₹ 20,974.67 Cr, then Low to Moderate, with the second as a follow-up in the same session |
| T4 | "What's the exit load of SBI Bluechip Fund?" | say the approved documents don't cover it (VerifAI shows *Not enough evidence*) without inventing a figure |
| T5 | "Which HSBC factsheet version does the tool search, and is an older one still on record?" | find in the Knowledge base that August 2026 (v2) is searched and July 2026 is superseded |

`success = 1` only if the criterion is met. A give-up or a wrong answer is `0`, with the time it took.

## After the tasks

1. Hand them the SUS questionnaire ([sus.md](sus.md)). They answer alone; don't explain the items.
2. Ask "What was the most confusing moment?" and write the answer in the `comment` column of `results/sus.csv`.
