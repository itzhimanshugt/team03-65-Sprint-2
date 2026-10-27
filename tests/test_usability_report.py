from scripts.usability_report import report, sus_score


def test_sus_score_extremes_and_neutral():
    assert sus_score([5, 1] * 5) == 100
    assert sus_score([1, 5] * 5) == 0
    assert sus_score([3] * 10) == 50


def test_report_from_csvs(tmp_path):
    (tmp_path / "baseline.csv").write_text("question,minutes,correct\nB1,10,1\nB2,14,0\n")
    (tmp_path / "interviews.csv").write_text(
        "participant,checks_per_day,minutes_per_check,where,outdated,trust\nP1,6,,,,\n"
    )
    (tmp_path / "tasks.csv").write_text(
        "participant,task,seconds,success\nP1,T1,40,1\nP1,T2,80,0\nP2,T1,50,1\n"
    )
    (tmp_path / "sus.csv").write_text(
        "participant,q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,comment\nP1,5,1,5,1,5,1,5,1,5,1,\n"
    )
    out = report(tmp_path)
    assert "12.0 min (1/2 correct)" in out  # median of 10 and 14
    assert "| 6 |" in out
    assert "50 s (2/3 tasks succeeded)" in out and "| 2 |" in out
    assert "93% faster" in out  # 1 − 50 s / 720 s
    assert "100.0" in out


def test_report_includes_automated_k7(tmp_path):
    for f, h in [("baseline", "q"), ("interviews", "p"), ("tasks", "p"), ("sus", "p")]:
        (tmp_path / f"{f}.csv").write_text(h + "\n")
    (tmp_path / "k7_automated.csv").write_text(
        "run,task,seconds,success\nrun1,T1,10.0,1\nrun1,T2,30.0,1\nrun1,T4,20.0,0\n"
    )
    assert "20.0 s, slowest 30 s (2/3 succeeded)" in report(tmp_path)


def test_report_with_empty_csvs(tmp_path):
    for f, h in [
        ("baseline", "question"),
        ("interviews", "participant"),
        ("tasks", "participant"),
        ("sus", "participant"),
    ]:
        (tmp_path / f"{f}.csv").write_text(h + "\n")
    assert report(tmp_path).startswith("No results recorded yet")
