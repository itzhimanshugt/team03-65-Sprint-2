from app.history import ChatHistory
from app.tokens import count_message_tokens


def make_history(n_turns: int, **kwargs) -> ChatHistory:
    h = ChatHistory(system_prompt="You are VerifAI.", **kwargs)
    for i in range(n_turns):
        h.add_turn(f"question {i}", f"answer {i}")
    return h


def test_system_first_question_last():
    msgs = make_history(2).messages("new question")
    assert msgs[0]["role"] == "system"
    assert msgs[-1] == {"role": "user", "content": "new question"}


def test_keeps_only_last_max_turns():
    msgs = make_history(10, max_turns=4).messages("q")
    contents = [m["content"] for m in msgs]
    assert "question 5" not in contents
    assert contents[1:3] == ["question 6", "answer 6"]
    assert len(msgs) == 1 + 4 * 2 + 1


def test_trims_oldest_turns_to_token_budget():
    h = ChatHistory(system_prompt="sys", token_budget=120)
    for i in range(4):
        h.add_turn("long question " * 10 + str(i), "long answer " * 10 + str(i))
    msgs = h.messages("q")
    assert count_message_tokens(msgs) <= 120
    assert msgs[-2]["content"].endswith("3")  # newest turn kept
    assert h.dropped_turns("q") > 0


def test_turns_are_never_split():
    msgs = make_history(3, token_budget=60).messages("q")
    roles = [m["role"] for m in msgs[1:-1]]
    assert roles == ["user", "assistant"] * (len(roles) // 2)
