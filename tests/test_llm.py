from types import SimpleNamespace

import pytest

from app.config import get_settings
from app.llm import MissingAPIKeyError, complete, get_client


class FakeClient:
    def __init__(self):
        self.sent = None
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.sent = kwargs
        return SimpleNamespace(
            model=kwargs["model"],
            choices=[
                SimpleNamespace(message=SimpleNamespace(content="Hello"), finish_reason="stop")
            ],
            usage=SimpleNamespace(prompt_tokens=12, completion_tokens=3),
        )


def test_complete_returns_text_and_usage(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "test-model")
    client = FakeClient()
    result = complete([{"role": "user", "content": "Hi"}], client=client, temperature=0.1)
    assert result.text == "Hello"
    assert (result.prompt_tokens, result.completion_tokens) == (12, 3)
    assert client.sent["model"] == "test-model"
    assert client.sent["temperature"] == 0.1


def test_missing_key_gives_clear_error(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "your_api_key_here")
    with pytest.raises(MissingAPIKeyError, match="LLM_API_KEY"):
        get_client(get_settings())


def test_client_uses_configured_base_url(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.test/v1/")
    assert str(get_client().base_url) == "https://example.test/v1/"


def test_defaults_come_from_settings(monkeypatch):
    monkeypatch.setenv("LLM_TEMPERATURE", "0.3")
    monkeypatch.setenv("LLM_MAX_TOKENS", "123")
    monkeypatch.setenv("LLM_REASONING_EFFORT", "none")
    client = FakeClient()
    result = complete([{"role": "user", "content": "Hi"}], client=client)
    assert (client.sent["temperature"], client.sent["max_tokens"]) == (0.3, 123)
    assert client.sent["reasoning_effort"] == "none"
    assert result.finish_reason == "stop"


def test_call_params_override_defaults_and_empty_effort_is_not_sent(monkeypatch):
    monkeypatch.setenv("LLM_REASONING_EFFORT", "")
    client = FakeClient()
    complete([{"role": "user", "content": "Hi"}], client=client, max_tokens=5, stop=["."])
    assert client.sent["max_tokens"] == 5
    assert client.sent["stop"] == ["."]
    assert "reasoning_effort" not in client.sent


def test_retry_delay_parsing():
    from app.llm import retry_delay_seconds

    assert retry_delay_seconds("Please retry in 15.226875461s.") == pytest.approx(15.23, 0.01)
    assert retry_delay_seconds("Please retry in 21h7m15.5s.") == pytest.approx(76035.5)
    assert retry_delay_seconds("quota exceeded") is None


def _rate_limit_error(message: str):
    import httpx
    from openai import RateLimitError

    response = httpx.Response(429, request=httpx.Request("POST", "https://example.test"))
    return RateLimitError(message, response=response, body=None)


def test_retries_after_short_rate_limit(monkeypatch):
    import app.llm

    monkeypatch.setattr(app.llm.time, "sleep", lambda s: None)
    client = FakeClient()
    real_create, calls = client.create, []

    def flaky_create(**kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise _rate_limit_error("Please retry in 2s.")
        return real_create(**kwargs)

    client.chat.completions.create = flaky_create
    assert complete([{"role": "user", "content": "Hi"}], client=client).text == "Hello"
    assert len(calls) == 2


def test_daily_quota_fails_fast_without_fallbacks(monkeypatch):
    monkeypatch.setenv("LLM_FALLBACK_MODELS", "")
    from openai import RateLimitError

    import app.llm

    monkeypatch.setattr(app.llm.time, "sleep", lambda s: pytest.fail("should not wait"))
    client = FakeClient()

    def always_429(**kwargs):
        raise _rate_limit_error("Please retry in 21h7m15s.")

    client.chat.completions.create = always_429
    with pytest.raises(RateLimitError):
        complete([{"role": "user", "content": "Hi"}], client=client)


def test_daily_quota_falls_back_to_next_model(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "model-a")
    monkeypatch.setenv("LLM_FALLBACK_MODELS", "model-b")
    client = FakeClient()
    real_create = client.create

    def quota_on_a(**kwargs):
        if kwargs["model"] == "model-a":
            raise _rate_limit_error("Please retry in 20h1m2s.")
        return real_create(**kwargs)

    client.chat.completions.create = quota_on_a
    result = complete([{"role": "user", "content": "Hi"}], client=client)
    assert result.model == "model-b"
