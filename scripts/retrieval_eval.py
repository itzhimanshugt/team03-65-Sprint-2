"""Score vector and hybrid retrieval on the eval set (answerable questions only).

Run: python -m scripts.retrieval_eval  (writes outputs/c27/retrieval_eval.md; 30 cached embeddings)
"""

import json
from pathlib import Path

from evaluation.retrieval_eval import evaluate, load_eval_set
from retrieval.hybrid import hybrid_search
from retrieval.search import search
from retrieval.vector_store import get_collection

K = 5
rows = load_eval_set()
text = {
    r["chunk_id"]: r["text"]
    for r in map(json.loads, open("data/processed/chunks.jsonl", encoding="utf-8"))
}
indexed = get_collection().count()
md = [
    f"# C27 — Retrieval evaluation (k={K}, {len(rows)} answerable questions, "
    f"{indexed:,} chunks indexed)",
    "",
    "| Retriever | Slice | Recall@5 | Precision@5 | MRR@5 |",
    "|---|---|---|---|---|",
]
for name, retrieve in (("vector", search), ("hybrid (BM25 + vector, RRF)", hybrid_search)):
    for slice_, s in evaluate(lambda q, r=retrieve: r(q, k=K), rows, text, K).items():
        md.append(f"| {name} | {slice_} | {s.recall:.2f} | {s.precision:.2f} | {s.mrr:.2f} |")
out = Path("outputs/c27/retrieval_eval.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
