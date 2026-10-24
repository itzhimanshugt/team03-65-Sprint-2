from evaluation.answer_eval import latency_p95, refusal_metrics, run_eval
from rag.citations import Citation
from rag.pipeline import Answer

ROWS = [
    {"question": "a", "expected": "answer"},
    {"question": "b", "expected": "answer"},
    {"question": "c", "expected": "no_evidence"},
    {"question": "d", "expected": "advice"},
]


def fake(q):
    if q in ("b", "c"):
        return Answer("no", refusal="no_evidence")
    return Answer("x [1]", citations=[Citation(1, "f", 1, "F", "id")])


def test_refusal_metrics():
    m = refusal_metrics(run_eval(ROWS, fake))
    assert m["K5 correct refusal rate"] == 0.5 and m["K6 false refusal rate"] == 0.5
    assert m["answers with ≥1 resolved citation"] == 1.0


def test_p95():
    runs = run_eval(ROWS, fake)
    for i, r in enumerate(runs):
        r.seconds = i
    assert latency_p95(runs) == 3
