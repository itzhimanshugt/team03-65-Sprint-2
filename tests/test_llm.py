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
            choices=[SimpleNamespace(message=SimpleNamespace(content="Hello"))],
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
