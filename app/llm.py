"""Thin wrapper around an OpenAI-compatible chat API (Gemini by default, see .env.example)."""

import re
import time
from dataclasses import dataclass

from openai import OpenAI, RateLimitError

from app.config import Settings, get_settings


class MissingAPIKeyError(RuntimeError):
    pass


MAX_RATE_LIMIT_RETRIES = 3
MAX_WAIT_SECONDS = 90  # longer waits mean a daily quota: fail instead of hanging


def retry_delay_seconds(error_message: str) -> float | None:
    """Read the provider's suggested wait (e.g. 'retry in 15.2s') from a 429 message."""
    match = re.search(r"retry in (?:(\d+)h)?(?:(\d+)m)?([\d.]+)s", error_message)
    if not match:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours or 0) * 3600 + int(minutes or 0) * 60 + float(seconds)


@dataclass(frozen=True)
class Completion:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str = ""


def get_client(settings: Settings | None = None) -> OpenAI:
    settings = settings or get_settings()
    if not settings.llm_api_key or settings.llm_api_key == "your_api_key_here":
        raise MissingAPIKeyError(
            "LLM_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)


def complete(messages: list[dict], client: OpenAI | None = None, **params) -> Completion:
    """Send chat messages and return the reply text with token usage.

    Output-control parameters default to the settings (temperature, max_tokens and, when set,
    reasoning_effort); any keyword passed here overrides them for this call.
    """
    settings = get_settings()
    client = client or get_client(settings)
    defaults = {
        "model": settings.llm_model,
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_tokens,
    }
    if settings.llm_reasoning_effort:
        # Gemini 2.5 "thinks" by default and those hidden tokens count against max_tokens.
        defaults["reasoning_effort"] = settings.llm_reasoning_effort
    request = {**defaults, **params}
    # Only switch models when the caller didn't pin one.
    fallbacks = [] if "model" in params else list(settings.llm_fallback_models)
    retries = 0
    while True:
        try:
            response = client.chat.completions.create(messages=messages, **request)
            break
        except RateLimitError as error:
            wait = retry_delay_seconds(str(error))
            if wait is not None and wait <= MAX_WAIT_SECONDS and retries < MAX_RATE_LIMIT_RETRIES:
                retries += 1
                time.sleep(wait + 1)  # per-minute limit: wait and retry the same model
            elif fallbacks:
                request["model"] = fallbacks.pop(0)  # daily quota used up: next model
                retries = 0
            else:
                raise
    usage = response.usage
    return Completion(
        text=response.choices[0].message.content or "",
        model=response.model,
        prompt_tokens=usage.prompt_tokens if usage else 0,
        completion_tokens=usage.completion_tokens if usage else 0,
        finish_reason=response.choices[0].finish_reason or "",
    )


def stream_complete(messages: list[dict], client: OpenAI | None = None, **params):
    """Yield the reply text piece by piece as the model produces it (same defaults as complete)."""
    settings = get_settings()
    client = client or get_client(settings)
    request = {
        "model": settings.llm_model,
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_tokens,
        **(
            {"reasoning_effort": settings.llm_reasoning_effort}
            if settings.llm_reasoning_effort
            else {}
        ),
        **params,
    }
    for chunk in client.chat.completions.create(messages=messages, stream=True, **request):
        if chunk.choices and (piece := chunk.choices[0].delta.content):
            yield piece
