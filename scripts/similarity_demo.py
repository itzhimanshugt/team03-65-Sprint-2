"""Rank corpus chunks against a question with three metrics.

Run: python -m scripts.similarity_demo  (writes outputs/c18/similarity_demo.md)
"""

import json
from pathlib import Path

from embeddings.embedder import embed_texts
from embeddings.similarity import cosine, dot, euclidean, rank

QUESTION = "What is the exit load of Parag Parikh Flexi Cap Fund?"
chunks = [json.loads(line) for line in open("data/processed/chunks.jsonl", encoding="utf-8")]
ids = ["6fde0dc4cd3e-0003", "d15820b5bf72-0000", "6402ffa74560-0000"]
picked = [c for c in chunks if c["chunk_id"] in ids]
picked += [c for c in chunks if c["family"] == "motilal-exit-load"][:1]
picked += [c for c in chunks if c["family"] == "product-shelf-notes"][:1]
q, *vs = embed_texts([QUESTION] + [c["text"] for c in picked])
lines = ["# C18 — Similarity metrics", "", f"Question: _{QUESTION}_", ""]
lines += ["| Chunk | Source | Cosine | Dot | Euclidean |", "|---|---|---|---|---|"]
for c, v in zip(picked, vs, strict=True):
    lines.append(
        f"| `{c['chunk_id']}` | {c['source_name']} · p.{c['page']} | "
        f"{cosine(q, v):.3f} | {dot(q, v):.3f} | {euclidean(q, v):.3f} |"
    )
order = {
    name: [picked[i]["source_name"] for i, _ in rank(q, vs, m)]
    for name, m in (("cosine", cosine), ("dot", dot), ("euclidean", euclidean))
}
lines += ["", "Ranking (most similar first):", ""]
lines += [f"- **{k}:** " + " → ".join(v) for k, v in order.items()]
lines += [
    "",
    "Vectors are L2-normalised in `embed_texts` (truncated 768-dim Gemini vectors are not "
    "unit-length on their own), so cosine = dot and Euclidean = sqrt(2 − 2·cosine): all three "
    "metrics give the same ranking.",
]
out = Path("outputs/c18/similarity_demo.md")
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out.read_text(encoding="utf-8"))
