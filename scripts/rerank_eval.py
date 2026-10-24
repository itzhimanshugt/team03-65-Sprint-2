"""Before/after re-ranking: MRR@5 on the eval set, and the top-5 for 5 questions.

Run: python -m scripts.rerank_eval  (writes outputs/c26/rerank_eval.md; cached embeddings only)
"""

import json
from pathlib import Path

from evaluation.retrieval_eval import evaluate, load_eval_set
from retrieval.reranker import rerank
from retrieval.search import search

rows = load_eval_set()
text = {
    r["chunk_id"]: r["text"]
    for r in map(json.loads, open("data/processed/chunks.jsonl", encoding="utf-8"))
}
plain = lambda q: search(q, k=5)  # noqa: E731
reranked = lambda q: rerank(q, search(q, k=20))  # noqa: E731
md = [
    "# C26 — Re-ranking top-20 → top-5 (lexical overlap)",
    "",
    "| Retrieval | Recall@5 | MRR@5 |",
    "|---|---|---|",
]
for name, fn in (("vector top-5", plain), ("vector top-20 → re-rank → top-5", reranked)):
    s = evaluate(fn, rows, text, 5)["all"]
    md.append(f"| {name} | {s.recall:.2f} | {s.mrr:.2f} |")
for row in rows[:5]:
    rel = set(row["relevant_chunk_ids"])
    md += ["", f"## {row['question']}", "", "| # | Before | After |", "|---|---|---|"]
    for n, (b, a) in enumerate(
        zip(plain(row["question"]), reranked(row["question"]), strict=True), 1
    ):
        cell = lambda h, rel=rel: ("✅ " if h.chunk_id in rel else "") + h.citation  # noqa: E731
        md.append(f"| {n} | {cell(b)} | {cell(a)} |")
out = Path("outputs/c26/rerank_eval.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
