from streamlit.testing.v1 import AppTest

APP = "app/ui/streamlit_app.py"
CITE = {
    "n": 1,
    "source_name": "f.pdf",
    "page": 39,
    "title": "F",
    "chunk_id": "c1",
    "text": "Exit load 1%.",
}


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        return self

    def json(self):
        return self.body


def run(monkeypatch, body, question="Exit load?"):
    import httpx

    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResponse(body))
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.chat_input[0].set_value(question).run()
    return at


def test_empty_state_s1():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert at.subheader[0].value == "Ask anything about your approved documents"


def test_answer_with_citation_chip_and_source_panel_s2(monkeypatch):
    at = run(monkeypatch, {"answer": "It is 1% [1].", "citations": [CITE], "refusal": None})
    assert "It is 1% [1]." in [m.value for m in at.markdown]
    assert "[1] f.pdf · p.39" in at.caption[-1].value and at.expander[0].label.startswith("[1] F")


def test_not_enough_evidence_s2c(monkeypatch):
    at = run(
        monkeypatch,
        {
            "answer": "I couldn't find this in the approved documents.",
            "citations": [],
            "refusal": "no_evidence",
        },
    )
    assert at.warning[0].value.startswith("I couldn't find this")
