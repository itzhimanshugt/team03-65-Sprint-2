import json

import httpx
from streamlit.testing.v1 import AppTest

ASK = "app/ui/pages/ask.py"
CITE = {
    "n": 1,
    "source_name": "f.pdf",
    "page": 39,
    "title": "HSBC Factsheet Aug 2026",
    "chunk_id": "c1",
    "text": "Exit load 1% within 1 year.",
    "score": 0.81,
    "published_date": "2026-08-31",
    "version": 2,
}
TRACE = {
    "candidates": 20,
    "reranked": 5,
    "top_score": 0.81,
    "threshold": 0.72,
    "neighbours": 1,
    "context_chunks": 6,
    "context_tokens": 1200,
    "model": "gemini-x",
}


class FakeStream:
    def __init__(self, body):
        words = body["answer"].split(" ") if not body["refusal"] else []
        self.lines = []
        for w in words:
            self.lines += ["event: token", "data: " + json.dumps(w + " "), ""]
        self.lines += ["event: done", "data: " + json.dumps(body), ""]

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def raise_for_status(self):
        return self

    def iter_lines(self):
        return iter(self.lines)


def ask(monkeypatch, body, question="Exit load of HSBC Value Fund?"):
    monkeypatch.setattr(httpx, "stream", lambda *a, **k: FakeStream(body))
    at = AppTest.from_file(ASK, default_timeout=30).run()
    at.text_area[0].set_value(question)
    at.button[0].click().run()  # "Verify with sources"
    return at


def html(at) -> str:
    return " ".join(m.value for m in at.markdown)


def test_empty_state_s1_offers_examples():
    at = AppTest.from_file(ASK, default_timeout=30).run()
    assert "Ask the approved documents" in html(at)
    assert at.button(key="example0").label == "What is the exit load of HSBC Value Fund?"


def test_grounded_answer_shows_cards_pipeline_and_evidence_s2_s3(monkeypatch):
    body = {
        "answer": "It is 1% [1].",
        "citations": [CITE],
        "refusal": None,
        "trace": TRACE,
        "standalone_question": "Exit load of HSBC Value Fund?",
    }
    at = ask(monkeypatch, body)
    page = html(at)
    assert "Grounded in approved documents" in page and "It is 1% [1]." in page
    assert "HSBC Factsheet Aug 2026" in page and "81% match" in page
    assert "20 candidates" in page and "1,200 / 3,000 tokens" in page
    at.button(key="inspect-1-1").click().run()
    assert "Exit load 1% within 1 year." in html(at) and "0.810 cosine" in html(at)


def test_not_enough_evidence_s2c(monkeypatch):
    body = {
        "answer": "I couldn't find this in the approved documents.",
        "citations": [],
        "refusal": "no_evidence",
        "trace": {"top_score": 0.61, "threshold": 0.72},
    }
    at = ask(monkeypatch, body)
    assert "Not enough evidence" in html(at) and "0.61" in at.caption[0].value


def test_advice_boundary_s2d(monkeypatch):
    body = {
        "answer": "I can share facts, not investment advice.\n\nIt is 1% [1].",
        "citations": [CITE],
        "refusal": "advice",
        "trace": TRACE,
    }
    at = ask(monkeypatch, body, "Should my client buy it?")
    assert "Advice boundary" in html(at) and "It is 1% [1]." in html(at)


def test_knowledge_base_lists_documents(monkeypatch):
    doc = {
        "title": "F",
        "doc_type": "factsheet",
        "issuer": "HSBC",
        "published_date": "2026-08-31",
        "version": 2,
        "is_latest": True,
        "chunks": 7,
        "doc_id": "d",
        "source_name": "f.pdf",
    }

    class Resp:
        def raise_for_status(self):
            return self

        def json(self):
            return [doc]

    monkeypatch.setattr(httpx, "get", lambda *a, **k: Resp())
    at = AppTest.from_file("app/ui/pages/knowledge.py", default_timeout=30).run()
    assert at.metric[0].value == "1" and len(at.dataframe) == 1
