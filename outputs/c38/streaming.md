# C38 — Streaming (POST /chat/stream, server-sent events)

Raw stream for "What is the benchmark of HSBC Short Term Fund?" (first lines):
```text
event: token
data: "The benchmark"

event: token
data: " for the HSBC Short Term Fund is the NIFTY Short Duration Debt Index A-II"

event: token
data: " [2]."

event: done
data: {"answer": "The benchmark for the HSBC Short Term Fund is the NIFTY Short Duration Debt Index A-II [2].", "refusal": null, "citations": [{"n": 2, "source_name": "hsbc-factsheet-2026-08.pdf", "page": 123, "title": "HSBC MF Factsheet (The Asset) - August 2026", "chunk_id": "dad15eb3423a-0428", "text": "HSBC Short Term Fund\nType of Scheme: An open ended short term debt scheme investing in instruments such that the Macaulay Duration of the\nportfolio is between 1 year to 3 years A Moderate interest rate risk and Relatively Low credit risk.\nProduct labelling: This product is suitable for investors who are seeking*:\n• Generation of regular returns over short term\n• Investment in fixed income securities of shorter-term maturity\n*Investors should consult their financial advisers if in doubt about whether the product is suitable for them.\nFund Details\nDate of Inception / Allotment: 27 December 2011\nBenchmark Name:NIFTY Short Duration Debt\nIndex A-II\nNAV(as on 31.08.26)\nRegular Plan - Growth Option ₹ 28.1083\nRegular Plan - Monthly IDCW\nOption ₹ 11.0409\nRegular Plan - Quarterly IDCW\nOption ₹ 10.3952\nRegular Plan - Annual IDCW\nOption ₹ 11.6401\nRegular Plan - Bonus Option ₹ 28.1072\nDirect Plan - Growth Option ₹ 29.9127\nDirect Plan - Monthly IDCW\nOption ₹ 11.7101\nDirect Plan - Quarterly IDCW\nOption ₹ 11.2574\nDirect Plan - Annual IDCW Option ₹ 12.2296\nAUM(as on 31.08.26) ₹ 3,869.86 Cr\nAAUM(for the month of Aug) ₹ 4,078.07 Cr\nFund Performance (CAGR)\nCompounded\nAnnualised\nReturns\nScheme\nReturns %\n- Regular\nScheme\nReturns %\n- Direct\nBenchmark\nReturns %\nReturns for last 1\nyear 5.20 5.54 4.87\nReturns for last 3\nyears 6.87 7.31 6.72"}], "standalone_question": "What is the benchmark of HSBC Short Term Fund?", "first_token_s": 6.32}

```

| Question | First token (s) | Total (s) |
|---|---|---|
| What is the AUM of HSBC Midcap Fund? | 4.232 | 4.325 |
| When was HSBC Gilt Fund launched? | 3.931 | 4.001 |
| What is the benchmark of Parag Parikh ELSS Tax Saver Fund? | 4.561 | 4.603 |
| Which certification is needed to distribute SIF products? | 2.313 | 2.659 |
| How soon does compliance upload a new monthly factsheet? | 2.245 | 2.3 |
