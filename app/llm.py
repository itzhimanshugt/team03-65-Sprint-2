"""Thin wrapper around an OpenAI-compatible chat API (Gemini by default, see .env.example)."""

from dataclasses import dataclass

from openai import OpenAI

from app.config import Settings, get_settings


class MissingAPIKeyError(RuntimeError):
    pass


@dataclass(frozen=True)
class Completion:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int


def get_client(settings: Settings | None = None) -> OpenAI:
    settings = settings or get_settings()
    if not settings.llm_api_key or settings.llm_api_key == "your_api_key_here":
        raise MissingAPIKeyError(
            "LLM_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)


def complete(messages: list[dict], client: OpenAI | None = None, **params) -> Completion:
    """Send chat messages and return the reply text with token usage."""
    settings = get_settings()
    client = client or get_client(settings)
    response = client.chat.completions.create(
        model=params.pop("model", settings.llm_model), messages=messages, **params
    )
    usage = response.usage
    return Completion(
        text=response.choices[0].message.content or "",
        model=response.model,
        prompt_tokens=usage.prompt_tokens if usage else 0,
        completion_tokens=usage.completion_tokens if usage else 0,
    )
