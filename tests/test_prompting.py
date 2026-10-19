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
