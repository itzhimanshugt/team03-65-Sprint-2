import pytest

from app.tokens import TOKENS_PER_MESSAGE, count_message_tokens, count_tokens, estimate_cost


def test_count_tokens_basic():
    assert count_tokens("") == 0
    assert count_tokens("hello world") == 2


def test_longer_text_has_more_tokens():
    assert count_tokens("exit load " * 50) > count_tokens("exit load")


def test_message_tokens_include_overhead():
    msgs = [{"role": "user", "content": "hello world"}]
    assert count_message_tokens(msgs) == 2 + TOKENS_PER_MESSAGE


def test_estimate_cost():
    # 1M input at $0.15 + 1M output at $0.60
    assert estimate_cost("gpt-4o-mini", 1_000_000, 1_000_000) == pytest.approx(0.75)


def test_unknown_model_raises():
    with pytest.raises(KeyError):
        estimate_cost("unknown-model", 10)


def test_special_token_strings_are_counted_not_rejected():
    assert count_tokens("before <|endoftext|> after") > 3
