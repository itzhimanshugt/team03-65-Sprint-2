import pytest

import app.structured as structured
from app.llm import Completion
from app.structured import Answer, StructuredOutputError, complete_json

VALID = '{"answer": "1% within 365 days [1]", "citations": [{"n": 1, "chunk_id": "d1-0003", "source": "ABC Factsheet.pdf", "page": 4}], "refused": false}'  # noqa: E501


def fake_replies(monkeypatch, texts):
    sent = []

    def fake_complete(messages, **params):
        sent.append((messages, params))
        return Completion(
            text=texts[len(sent) - 1], model="m", prompt_tokens=0, completion_tokens=0
        )

    monkeypatch.setattr(structured, "complete", fake_complete)
    return sent


def test_valid_json_parses(monkeypatch):
    sent = fake_replies(monkeypatch, [VALID])
    result = complete_json([{"role": "user", "content": "q"}], Answer)
    assert result.citations[0].page == 4 and not result.refused
    assert sent[0][1]["response_format"] == {"type": "json_object"}
    assert "JSON schema" in sent[0][0][-1]["content"]


def test_invalid_json_retries_once_with_error(monkeypatch):
    sent = fake_replies(monkeypatch, ['{"answer": 5', VALID])
    assert complete_json([{"role": "user", "content": "q"}], Answer).answer.startswith("1%")
    assert "invalid" in sent[1][0][-1]["content"]


def test_wrong_shape_twice_raises(monkeypatch):
    fake_replies(monkeypatch, ['{"citations": "none"}', '{"citations": "none"}'])
    with pytest.raises(StructuredOutputError):
        complete_json([{"role": "user", "content": "q"}], Answer)


def test_partial_json_uses_defaults(monkeypatch):
    fake_replies(monkeypatch, ['{"answer": "Not in the approved documents.", "refused": true}'])
    result = complete_json([{"role": "user", "content": "q"}], Answer)
    assert result.refused and result.citations == []
