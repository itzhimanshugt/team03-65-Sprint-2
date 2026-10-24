"""VerifAI HTTP API. Run: uvicorn app.api.main:app --reload  (Swagger docs at /docs)."""

import json
import queue
import shutil
import tempfile
import threading
import time
from datetime import date
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.llm import stream_complete
from app.observability import QueryCache, cache_key, log_request, stats
from ingestion.upload import UploadError, index_upload
from rag.conversation import condense
from rag.pipeline import answer
from retrieval.hybrid import build_where
from retrieval.search import search
from retrieval.vector_store import get_collection

app = FastAPI(
    title="VerifAI", version="0.1.0", description="Cited answers from approved documents."
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    history: list[tuple[str, str]] = Field(
        default_factory=list, description="(question, answer) turns"
    )
    issuer: str | None = None
    doc_type: str | None = None


class CitationOut(BaseModel):
    n: int
    source_name: str
    page: int | None
    title: str
    chunk_id: str
    text: str


class ChatResponse(BaseModel):
    answer: str
    standalone_question: str
    refused: bool
    refusal: str | None
    citations: list[CitationOut]


class DocumentOut(BaseModel):
    doc_id: str
    source_name: str
    title: str
    doc_type: str
    issuer: str
    published_date: str
    version: int
    is_latest: bool
    chunks: int


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "chunks_indexed": get_collection().count()}


CACHE = QueryCache()


@app.get("/stats")
def usage_stats() -> dict:
    return stats()


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    start = time.perf_counter()
    filters = {k: v for k, v in (("issuer", req.issuer), ("doc_type", req.doc_type)) if v}
    key = cache_key(req.question, req.history, filters)
    if cached := CACHE.get(key):
        log_request(
            {
                "question": req.question,
                "cached": True,
                "refusal": cached["refusal"],
                "latency_s": time.perf_counter() - start,
            }
        )
        return ChatResponse(**cached)
    question = condense(req.question, req.history)
    where = build_where(**filters)
    a = answer(question, retrieve=lambda q: search(q, k=20, where=where))
    by_id = {h.chunk_id: h for h in a.sources}
    resp = ChatResponse(
        answer=a.text,
        standalone_question=question,
        refused=a.refused,
        refusal=a.refusal,
        citations=[CitationOut(**vars(c), text=by_id[c.chunk_id].text) for c in a.citations],
    )
    CACHE.put(key, resp.model_dump())
    log_request(
        {
            "question": req.question,
            "cached": False,
            "refusal": a.refusal,
            "cited_doc_ids": sorted({c.chunk_id.split("-")[0] for c in a.citations}),
            "latency_s": round(time.perf_counter() - start, 3),
        }
    )
    return resp


def sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/chat/stream")
def chat_stream(req: ChatRequest) -> StreamingResponse:
    """Server-sent events: `token` events as the answer streams, then one `done` with citations."""
    start = time.perf_counter()
    filters = {k: v for k, v in (("issuer", req.issuer), ("doc_type", req.doc_type)) if v}
    question = condense(req.question, req.history)
    where = build_where(**filters)
    tokens: queue.Queue = queue.Queue()
    result: dict = {}

    def generate(messages: list[dict]) -> str:
        parts = []
        for piece in stream_complete(messages):
            parts.append(piece)
            tokens.put(piece)
        return "".join(parts)

    def run() -> None:
        try:
            retrieve = lambda q: search(q, k=20, where=where)  # noqa: E731
            result["answer"] = answer(question, retrieve=retrieve, generate=generate)
        except Exception as error:  # surfaced to the client as an `error` event (Mock UX S2e)
            result["error"] = type(error).__name__
        tokens.put(None)

    def events():
        threading.Thread(target=run, daemon=True).start()
        first = None
        while (piece := tokens.get()) is not None:
            first = first or time.perf_counter() - start
            yield sse("token", piece)
        if "error" in result:
            yield sse("error", {"message": "The answer couldn't be generated."})
            return
        a = result["answer"]
        by_id = {h.chunk_id: h for h in a.sources}
        cites = [
            CitationOut(**vars(c), text=by_id[c.chunk_id].text).model_dump() for c in a.citations
        ]
        total = time.perf_counter() - start
        first = round(first or total, 3)
        log_request(
            {
                "question": req.question,
                "cached": False,
                "stream": True,
                "refusal": a.refusal,
                "first_token_s": first,
                "latency_s": round(total, 3),
            }
        )
        done = {
            "answer": a.text,
            "refusal": a.refusal,
            "citations": cites,
            "standalone_question": question,
            "first_token_s": first,
        }
        yield sse("done", done)

    return StreamingResponse(events(), media_type="text/event-stream")


@app.get("/documents", response_model=list[DocumentOut])
def documents() -> list[DocumentOut]:
    docs: dict[str, dict] = {}
    for md in get_collection().get(include=["metadatas"])["metadatas"]:
        d = docs.setdefault(
            md["doc_id"], {**{f: md.get(f) for f in DocumentOut.model_fields}, "chunks": 0}
        )
        d["chunks"] += 1
    return [DocumentOut(**d) for d in sorted(docs.values(), key=lambda d: d["source_name"])]


class UploadOut(BaseModel):
    doc_id: str
    status: str
    chunks: int
    superseded_chunks: int


@app.post("/documents", response_model=UploadOut, status_code=201)
def upload_document(
    file: UploadFile,
    title: str = Form(...),
    doc_type: Literal["factsheet", "sid_kim", "circular", "research", "internal"] = Form(...),
    issuer: str = Form(...),
    family: str = Form(..., description="Versions of one document share a family"),
    published_date: date = Form(...),  # noqa: B008
    version: int = Form(1, ge=1),
) -> UploadOut:
    entry = {
        "title": title,
        "doc_type": doc_type,
        "issuer": issuer,
        "family": family,
        "published_date": published_date.isoformat(),
        "version": version,
    }
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / Path(file.filename or "upload").name
        with path.open("wb") as out:
            shutil.copyfileobj(file.file, out)
        try:
            r = index_upload(path, entry, get_collection())
        except UploadError as error:
            raise HTTPException(error.status, str(error)) from error
    CACHE.items.clear()  # answers may change once a new document or version is searchable
    return UploadOut(
        doc_id=r.doc_id, status="Indexed", chunks=r.chunks, superseded_chunks=r.superseded
    )
