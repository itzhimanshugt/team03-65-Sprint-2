import pytest

from rag.guardrails import ADVICE_NOTICE, NO_EVIDENCE, is_advice_seeking
from rag.pipeline import answer
from retrieval.search import Hit


def hit(score):
    return Hit("a", "HSBC Value Fund exit load 1%.", score, {"source_name": "f.pdf", "page": 3})


def no_llm(messages):
    raise AssertionError("LLM must not be called")


@pytest.mark.parametrize(
    "q",
    [
        "Should my client switch from HSBC Value Fund to Small Cap?",
        "Which is the best fund for retirement?",
        "Can you recommend a liquid fund?",
        "Is now a good time to invest in small caps?",
    ],
)
def test_advice_questions_detected(q):
    assert is_advice_seeking(q)


@pytest.mark.parametrize(
    "q", ["What is the exit load of HSBC Value Fund?", "Who manages HSBC Small Cap Fund?"]
)
def test_factual_questions_pass(q):
    assert not is_advice_seeking(q)


def test_unanswerable_refused_with_mock_ux_copy():
    out = answer(
        "Fund manager's personal portfolio?",
        retrieve=lambda q: [hit(0.2)],
        generate=no_llm,
        threshold=0.5,
    )
    assert out.refusal == "no_evidence" and out.text == NO_EVIDENCE
    assert out.text.startswith("I couldn't find this in the approved documents")


def test_advice_declined_but_facts_offered():
    out = answer(
        "Should my client switch to HSBC Value Fund?",
        retrieve=lambda q: [hit(0.9)],
        generate=lambda m: "Exit load is 1% [1].",
        threshold=0.5,
    )
    assert out.refusal == "advice" and out.text.startswith(ADVICE_NOTICE)
    assert "Exit load is 1% [1]." in out.text and out.citations


def test_advice_without_evidence_gets_notice_only():
    out = answer("Should I buy it?", retrieve=lambda q: [hit(0.1)], generate=no_llm, threshold=0.5)
    assert out.refusal == "advice" and out.text == ADVICE_NOTICE
