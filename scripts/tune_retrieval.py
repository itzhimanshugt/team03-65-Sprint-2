"""Grid over k and the evidence threshold on the eval set (cached embeddings, no LLM calls).

Run: python -m scripts.tune_retrieval  (writes outputs/c25/tuning.md)
k is judged on Recall@k / MRR@k; the threshold on how many unanswerable questions it refuses
versus how many answerable ones it wrongly refuses (top cosine score below the threshold).
"""

import json
from pathlib import Path

from evaluation.retrieval_eval import evaluate, load_eval_set
from retrieval.search import search

rows = load_eval_set(answerable_only=False)
answerable = [r for r in rows if r["expected"] == "answer"]
unanswerable = [r for r in rows if r["expected"] == "no_evidence"]
text = {
    r["chunk_id"]: r["text"]
    for r in map(json.loads, open("data/processed/chunks.jsonl", encoding="utf-8"))
}
pool = {r["question"]: search(r["question"], k=8) for r in rows}  # one embedding per question

md = [
    "# C25 — Retrieval tuning",
    "",
    "## Top-k",
    "",
    "| k | Recall@k | Precision@k | MRR@k |",
    "|---|---|---|---|",
]
for k in (3, 5, 8):
    s = evaluate(lambda q, k=k: pool[q][:k], answerable, text, k)["all"]
    md.append(f"| {k} | {s.recall:.2f} | {s.precision:.2f} | {s.mrr:.2f} |")
top = {q: hits[0].score for q, hits in pool.items()}
md += ["", "## Evidence threshold (refuse if top cosine < t)", ""]
md += ["| t | Unanswerable refused (K5 part) | Answerable wrongly refused (K6) |", "|---|---|---|"]
for t in (0.45, 0.55, 0.60, 0.65, 0.70, 0.72, 0.75):
    ok = sum(top[r["question"]] < t for r in unanswerable) / len(unanswerable)
    bad = sum(top[r["question"]] < t for r in answerable) / len(answerable)
    md.append(f"| {t:.2f} | {ok:.0%} | {bad:.0%} |")
md += ["", "Top cosine per question:", ""]
md += [f"- {r['slice']}: {top[r['question']]:.3f} — {r['question']}" for r in rows]
out = Path("outputs/c25/tuning.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
