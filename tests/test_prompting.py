from app.prompting import build_messages, load_system_prompt


def test_messages_have_system_then_user():
    msgs = build_messages("What is the exit load?", "You are VerifAI.")
    assert [m["role"] for m in msgs] == ["system", "user"]
    assert msgs[1]["content"] == "What is the exit load?"


def test_system_message_is_optional():
    assert [m["role"] for m in build_messages("Hi")] == ["user"]


def test_system_prompt_contains_core_rules():
    prompt = load_system_prompt()
    assert "approved document" in prompt
    assert "investment advice" in prompt


def test_render_fills_placeholders():
    from app.prompting import render_prompt

    text = render_prompt("answer", context="[1] Exit load: 1%.", question="What is the exit load?")
    assert "[1] Exit load: 1%." in text and "Question: What is the exit load?" in text
    assert "$" not in text


def test_render_missing_value_raises():
    import pytest

    from app.prompting import render_prompt

    with pytest.raises(KeyError):
        render_prompt("answer", question="q")
