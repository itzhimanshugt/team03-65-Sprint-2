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


def test_repeat_question_served_from_cache(monkeypatch, tmp_path):
    import app.observability as obs

    log = tmp_path / "log.jsonl"
    monkeypatch.setattr(obs, "LOG", log)
    monkeypatch.setattr(api, "log_request", lambda e: obs.log_request(e, log))
    monkeypatch.setattr(api, "stats", lambda: obs.stats(log))
    monkeypatch.setattr(api, "CACHE", obs.QueryCache())
    calls = []
    monkeypatch.setattr(
        api, "answer", lambda q, retrieve: calls.append(q) or Answer("no", refusal="no_evidence")
    )
    client = TestClient(api.app)
    for _ in range(2):
        client.post("/chat", json={"question": "Unknown thing?"})
    assert len(calls) == 1
    s = client.get("/stats").json()
    assert s["requests"] == 2 and s["cache_hits"] == 1 and s["refusals"] == 2


def test_upload_clears_query_cache(monkeypatch):
    import app.observability as obs
    from ingestion.upload import UploadResult

    monkeypatch.setattr(api, "CACHE", obs.QueryCache())
    monkeypatch.setattr(api, "get_collection", lambda: FakeCollection())
    monkeypatch.setattr(api, "index_upload", lambda path, entry, col: UploadResult("d2", 1, 0))
    api.CACHE.put("k", {"answer": "old"})
    r = TestClient(api.app).post(
        "/documents",
        files={"file": ("n.md", b"# N\n\ntext")},
        data={
            "title": "N",
            "doc_type": "internal",
            "issuer": "F",
            "family": "n",
            "published_date": "2026-10-24",
        },
    )
    assert r.status_code == 201 and api.CACHE.get("k") is None


def test_chat_stream_sends_tokens_then_citations(monkeypatch, tmp_path):
    import app.observability as obs

    monkeypatch.setattr(api, "log_request", lambda e: obs.log_request(e, tmp_path / "l.jsonl"))
    monkeypatch.setattr(api, "condense", lambda q, h: q)
    hit = Hit("c1", "Exit load 1%.", 0.9, {})

    def fake_answer(q, retrieve, generate):
        text = generate([])
        return Answer(text, [hit], None, [Citation(1, "f.pdf", 3, "F", "c1")])

    monkeypatch.setattr(api, "answer", fake_answer)
    monkeypatch.setattr(api, "stream_complete", lambda m: iter(["It is ", "1% [1]."]))
    body = TestClient(api.app).post("/chat/stream", json={"question": "Exit load of F?"}).text
    assert body.count("event: token") == 2 and body.index("event: token") < body.index(
        "event: done"
    )
    assert '"chunk_id": "c1"' in body and '"answer": "It is 1% [1]."' in body
