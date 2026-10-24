"""Run all 40 eval questions end to end; write metrics and a manual K3/K4 review sheet.

Run: python -m scripts.answer_eval  (writes outputs/c34/answer_eval.md and review_sheet.md)
"""

from pathlib import Path

from evaluation.answer_eval import latency_p95, refusal_metrics, run_eval
from evaluation.retrieval_eval import load_eval_set
from rag.pipeline import answer

runs = run_eval(load_eval_set(answerable_only=False), answer)
m = refusal_metrics(runs)
md = [
    "# C34 — Answer evaluation (40 questions)",
    "",
    "| Metric | Value | Target |",
    "|---|---|---|",
]
targets = {"K5 correct refusal rate": "≥ 90%", "K6 false refusal rate": "≤ 10%"}
md += [f"| {k} | {v:.0%} | {targets.get(k, '—')} |" for k, v in m.items()]
md += [f"| K8 p95 latency | {latency_p95(runs):.1f} s | ≤ 8 s |", "", "## Per question", ""]
md += ["| id | slice | expected | got | citations | s |", "|---|---|---|---|---|---|"]
for r in runs:
    got = r.answer.refusal or "answer"
    md.append(
        f"| {r.row['id']} | {r.row['slice']} | {r.row['expected']} | {got} | "
        f"{len(r.answer.citations)} | {r.seconds:.1f} |"
    )
sheet = ["# C34 — Manual review sheet (K3 citation accuracy, K4 hallucination)", ""]
for r in runs:
    if r.row["expected"] != "answer" or r.answer.refused:
        continue
    sheet += [
        f"## {r.row['id']} — {r.row['question']}",
        "",
        f"Reference: {r.row['reference_answer']}",
    ]
    sheet += ["", r.answer.text.strip(), ""]
    for c in r.answer.citations:
        hit = r.answer.sources[c.n - 1]
        sheet += [f"- [{c.n}] {c.source_name} p.{c.page}: {hit.text[:200].replace(chr(10), ' ')}…"]
    sheet += ["", "Supported: ☐ yes ☐ partly ☐ no · Unsupported claim: ☐", ""]
out = Path("outputs/c34")
out.mkdir(parents=True, exist_ok=True)
(out / "answer_eval.md").write_text("\n".join(md) + "\n", encoding="utf-8")
(out / "review_sheet.md").write_text("\n".join(sheet) + "\n", encoding="utf-8")
print("\n".join(md))
