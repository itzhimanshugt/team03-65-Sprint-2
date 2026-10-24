from fastapi.testclient import TestClient

import app.api.main as api
from rag.citations import Citation
from rag.pipeline import Answer
from retrieval.search import Hit


class FakeCollection:
    def count(self):
        return 2

    def get(self, include):
        md = {
            "doc_id": "d1",
            "source_name": "f.pdf",
            "title": "F",
            "doc_type": "factsheet",
            "issuer": "HSBC Mutual Fund",
            "published_date": "2026-08-31",
            "version": 1,
            "is_latest": True,
        }
        return {"metadatas": [md, md]}


def test_endpoints(monkeypatch):
    monkeypatch.setattr(api, "get_collection", lambda: FakeCollection())
    hit = Hit("c1", "Exit load 1%.", 0.9, {})
    monkeypatch.setattr(
        api,
        "answer",
        lambda q, retrieve: Answer("1% [1]", [hit], None, [Citation(1, "f.pdf", 3, "F", "c1")]),
    )
    client = TestClient(api.app)
    assert client.get("/health").json() == {"status": "ok", "chunks_indexed": 2}
    docs = client.get("/documents").json()
    assert docs[0]["chunks"] == 2 and docs[0]["is_latest"]
    r = client.post("/chat", json={"question": "Exit load of F?"}).json()
    assert (
        r["answer"] == "1% [1]"
        and r["citations"][0]["text"] == "Exit load 1%."
        and not r["refused"]
    )
    assert client.post("/chat", json={"question": ""}).status_code == 422
    assert "/chat" in client.get("/openapi.json").json()["paths"]
