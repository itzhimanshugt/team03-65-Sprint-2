"""Token counts and cost estimates for VerifAI.

Run: python -m scripts.token_report  (writes outputs/c5/token_report.md)
"""

from pathlib import Path

from app.llm import complete
from app.prompting import build_messages, load_system_prompt
from app.tokens import count_message_tokens, count_tokens, estimate_cost

lines = ["# C5 — Tokens and cost", ""]

# 1. How text splits into tokens
sample = "The exit load of ABC Flexi Cap Fund is 1% if redeemed within 365 days."
lines += [
    "## 1. Tokenization example",
    "",
    f"Text: `{sample}`",
    "",
    f"Characters: {len(sample)} · Tokens (cl100k_base): {count_tokens(sample)}",
    "",
]

# 2. Estimate vs actual usage on a live call
messages = build_messages("What is a mutual fund exit load?", load_system_prompt())
estimated = count_message_tokens(messages)
reply = complete(messages, temperature=0.1)
lines += [
    "## 2. Estimated vs actual input tokens (live call)",
    "",
    "| Model | Estimated input (tiktoken) | Actual input (API usage) | Actual output |",
    "|---|---|---|---|",
    f"| {reply.model} | {estimated} | {reply.prompt_tokens} | {reply.completion_tokens} |",
    "",
    "tiktoken is OpenAI's tokenizer, so for Gemini it is an estimate. The `usage` field "
    "returned by the API is the exact, billed count.",
    "",
]

# 3. Projected costs
pages, tokens_per_page = 1_500, 450  # PRD §6.1 corpus estimate
corpus_tokens = pages * tokens_per_page
per_question_in, per_question_out = 3_000 + 400, 300  # context budget + prompt, answer
lines += [
    "## 3. Projected costs (paid-tier list prices)",
    "",
    "| Item | Tokens | Gemini | OpenAI |",
    "|---|---|---|---|",
    f"| Embed full corpus once ({pages:,} pages × {tokens_per_page}) | {corpus_tokens:,} | "
    f"${estimate_cost('gemini-embedding-001', corpus_tokens):.4f} | "
    f"${estimate_cost('text-embedding-3-small', corpus_tokens):.4f} |",
    f"| One question ({per_question_in:,} in / {per_question_out} out) | "
    f"{per_question_in + per_question_out:,} | "
    f"${estimate_cost('gemini-2.5-flash', per_question_in, per_question_out):.5f} | "
    f"${estimate_cost('gpt-4o-mini', per_question_in, per_question_out):.5f} |",
    f"| 100-question eval run | {(per_question_in + per_question_out) * 100:,} | "
    f"${estimate_cost('gemini-2.5-flash', per_question_in * 100, per_question_out * 100):.3f} | "
    f"${estimate_cost('gpt-4o-mini', per_question_in * 100, per_question_out * 100):.3f} |",
    "",
    "On Gemini's free tier these calls cost $0; the limit is the request and token quota "
    "(requests per minute and per day, input tokens per minute), not money. Output assumes "
    "thinking is off; Gemini 2.5 thinking tokens are billed as output and would raise it.",
]

out = Path("outputs/c5/token_report.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines), encoding="utf-8")
print(out.read_text(encoding="utf-8"))
