"""VerifAI HTTP API. Run: uvicorn app.api.main:app --reload  (Swagger docs at /docs)."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

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


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    question = condense(req.question, req.history)
    filters = {k: v for k, v in (("issuer", req.issuer), ("doc_type", req.doc_type)) if v}
    where = build_where(**filters)
    a = answer(question, retrieve=lambda q: search(q, k=20, where=where))
    by_id = {h.chunk_id: h for h in a.sources}
    return ChatResponse(
        answer=a.text,
        standalone_question=question,
        refused=a.refused,
        refusal=a.refusal,
        citations=[CitationOut(**vars(c), text=by_id[c.chunk_id].text) for c in a.citations],
    )


@app.get("/documents", response_model=list[DocumentOut])
def documents() -> list[DocumentOut]:
    docs: dict[str, dict] = {}
    for md in get_collection().get(include=["metadatas"])["metadatas"]:
        d = docs.setdefault(
            md["doc_id"], {**{f: md.get(f) for f in DocumentOut.model_fields}, "chunks": 0}
        )
        d["chunks"] += 1
    return [DocumentOut(**d) for d in sorted(docs.values(), key=lambda d: d["source_name"])]
