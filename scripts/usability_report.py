"""KPI table from the usability kit's CSVs (issues #43, #44): baseline, K7, K11.

Run: python -m scripts.usability_report [results_dir]
"""

import csv
import sys
from pathlib import Path
from statistics import mean, median

RESULTS = Path("docs/usability/results")


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return [r for r in csv.DictReader(f) if any((v or "").strip() for v in r.values())]


def sus_score(answers: list[int]) -> float:
    """Brooke's SUS: odd items answer−1, even items 5−answer, sum × 2.5."""
    assert len(answers) == 10 and all(1 <= a <= 5 for a in answers), answers
    return 2.5 * sum(a - 1 if i % 2 == 0 else 5 - a for i, a in enumerate(answers))


def report(d: Path = RESULTS) -> str:
    base, intv, tasks, sus = (
        rows(d / f) for f in ("baseline.csv", "interviews.csv", "tasks.csv", "sus.csv")
    )
    out = ["| Measure | Result | Target | n |", "|---|---|---|---|"]

    def row(*cells) -> None:
        out.append("| " + " | ".join(map(str, cells)) + " |")

    if base:
        mins = median(float(r["minutes"]) for r in base)
        ok = sum(int(r["correct"]) for r in base)
        row("Manual lookup, median", f"{mins:.1f} min ({ok}/{len(base)} correct)", "—", len(base))
    if intv:
        per_day = median(float(r["checks_per_day"]) for r in intv)
        row("Checks per advisor per day, median", f"{per_day:g}", "—", len(intv))
    if tasks:
        k7 = median(float(r["seconds"]) for r in tasks)
        ok = sum(int(r["success"]) for r in tasks)
        people = len({r["participant"] for r in tasks})
        result = f"{k7:.0f} s ({ok}/{len(tasks)} tasks succeeded)"
        row("K7 time to verified answer, median", result, "≤ 60 s", people)
        if base:
            row(
                "K7 vs manual baseline", f"{100 * (1 - k7 / (60 * mins)):.0f}% faster", "≥ 90%", "—"
            )
    auto = rows(d / "k7_automated.csv") if (d / "k7_automated.csv").exists() else []
    if auto:
        secs = [float(r["seconds"]) for r in auto]
        ok = sum(int(r["success"]) for r in auto)
        result = f"{median(secs):.1f} s, slowest {max(secs):.0f} s ({ok}/{len(auto)} succeeded)"
        row("K7 system time, median (headless browser, no human)", result, "≤ 60 s", len(auto))
    if sus:
        scores = [sus_score([int(r[f"q{i}"]) for i in range(1, 11)]) for r in sus]
        row("K11 SUS, mean", f"{mean(scores):.1f}", "≥ 70", len(scores))
    if len(out) == 2:
        return "No results recorded yet: fill in docs/usability/results/*.csv."
    return "\n".join(out)


if __name__ == "__main__":
    print(report(Path(sys.argv[1]) if len(sys.argv) > 1 else RESULTS))
