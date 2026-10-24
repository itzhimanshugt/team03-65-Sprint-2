from rag.conversation import Conversation, condense
from retrieval.search import Hit


def test_first_question_skips_the_llm():
    def no_llm(messages):
        raise AssertionError("no LLM call expected")

    assert condense("What is the exit load of X?", [], no_llm) == "What is the exit load of X?"


def test_follow_up_is_rewritten_from_recent_turns():
    seen = {}

    def fake(messages):
        seen["prompt"] = messages[-1]["content"]
        return " What is the expense ratio of HSBC Value Fund? "

    turns = [(f"old q{i}", "old answer") for i in range(5)] + [
        ("What is the exit load of HSBC Value Fund?", "Nil up to 10%… [1]")
    ]
    out = condense("and its expense ratio?", turns, fake)
    assert out == "What is the expense ratio of HSBC Value Fund?"
    assert "HSBC Value Fund" in seen["prompt"] and "old q0" not in seen["prompt"]  # last 4 only


def test_conversation_retrieves_with_the_standalone_query():
    asked = []
    hit = Hit("a", "Expense ratio 1.7%.", 0.9, {"source_name": "f.pdf", "page": 39})

    def fake(messages):
        text = messages[-1]["content"]
        if text.startswith("Rewrite"):
            return "What is the expense ratio of HSBC Value Fund?"
        return "It is 1.7% [1]."

    chat = Conversation(generate=fake, retrieve=lambda q: asked.append(q) or [hit], threshold=0.5)
    chat.ask("What is the exit load of HSBC Value Fund?")
    standalone, result = chat.ask("and its expense ratio?")
    assert asked == ["What is the exit load of HSBC Value Fund?", standalone]
    assert "HSBC Value Fund" in standalone and result.citations
