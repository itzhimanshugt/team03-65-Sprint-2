"""Token counting and API cost estimation."""

from functools import lru_cache

import tiktoken

# USD per 1M tokens (input, output). Paid-tier list prices; check the provider's pricing
# page before relying on them. Gemini's free tier costs $0 within its rate limits.
PRICES_PER_MILLION = {
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-embedding-001": (0.15, 0.0),
    "gpt-4o-mini": (0.15, 0.60),
    "text-embedding-3-small": (0.02, 0.0),
}

# Overhead tokens the chat format adds per message (role markers, separators).
TOKENS_PER_MESSAGE = 4


@lru_cache
def _encoding() -> tiktoken.Encoding:
    # cl100k_base is OpenAI's tokenizer. Gemini tokenizes differently, so for Gemini this
    # is an estimate; the API's usage field gives the exact count after the call.
    return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_encoding().encode(text))


def count_message_tokens(messages: list[dict]) -> int:
    return sum(count_tokens(m["content"]) + TOKENS_PER_MESSAGE for m in messages)


def estimate_cost(model: str, input_tokens: int, output_tokens: int = 0) -> float:
    """Return the estimated cost in USD for one call."""
    if model not in PRICES_PER_MILLION:
        raise KeyError(f"No price configured for model '{model}'")
    in_price, out_price = PRICES_PER_MILLION[model]
    return (input_tokens * in_price + output_tokens * out_price) / 1_000_000
