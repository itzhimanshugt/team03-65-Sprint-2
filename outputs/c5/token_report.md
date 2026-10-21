# C5 — Tokens and cost

## 1. Tokenization example

Text: `The exit load of ABC Flexi Cap Fund is 1% if redeemed within 365 days.`

Characters: 70 · Tokens (cl100k_base): 20

## 2. Estimated vs actual input tokens (live call)

| Model | Estimated input (tiktoken) | Actual input (API usage) | Actual output |
|---|---|---|---|
| gemini-2.5-flash | 193 | 198 | 83 |

tiktoken is OpenAI's tokenizer, so for Gemini it is an estimate. The `usage` field returned by the API is the exact, billed count.

## 3. Projected costs (paid-tier list prices)

| Item | Tokens | Gemini | OpenAI |
|---|---|---|---|
| Embed full corpus once (1,500 pages × 450) | 675,000 | $0.1013 | $0.0135 |
| One question (3,400 in / 300 out) | 3,700 | $0.00177 | $0.00069 |
| 100-question eval run | 370,000 | $0.177 | $0.069 |

On Gemini's free tier these calls cost $0; the limit is requests per minute, not money.