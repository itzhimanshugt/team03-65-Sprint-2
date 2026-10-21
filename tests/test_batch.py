import httpx
import pytest
from openai import RateLimitError

from embeddings.batch import BatchReport, VectorCache, embed_records

RECORDS = [{"chunk_id": f"c{i}", "text": f"text {i}", "token_count": 10} for i in range(5)]


def fake_embed(calls):
    def embed(texts):
        calls.append(len(texts))
        return [[float(len(t)), 1.0] for t in texts]

    return embed


def rate_limit(msg):
    return RateLimitError(
        msg, response=httpx.Response(429, request=httpx.Request("POST", "https://x")), body=None
    )


def test_batches_and_saves(tmp_path):
    calls = []
    rep = embed_records(
        RECORDS, VectorCache(tmp_path), batch_size=2, embed=fake_embed(calls), log=lambda *_: None
    )
    assert calls == [2, 2, 1] and rep.embedded == 5 and rep.requests == 3 and rep.tokens == 50
    reloaded = VectorCache(tmp_path)
    assert reloaded.ids == [f"c{i}" for i in range(5)] and reloaded.vectors.shape == (5, 2)


def test_rerun_skips_cached_chunks(tmp_path):
    embed_records(RECORDS[:3], VectorCache(tmp_path), embed=fake_embed([]), log=lambda *_: None)
    calls = []
    rep = embed_records(
        RECORDS, VectorCache(tmp_path), embed=fake_embed(calls), log=lambda *_: None
    )
    assert rep.skipped == 3 and calls == [2]


def test_waits_and_retries_on_short_rate_limit(tmp_path):
    inner, slept, failed = fake_embed([]), [], []

    def flaky(texts):
        if not failed:
            failed.append(1)
            raise rate_limit("Please retry in 3s.")
        return inner(texts)

    rep = embed_records(
        RECORDS, VectorCache(tmp_path), embed=flaky, sleep=slept.append, log=lambda *_: None
    )
    assert rep.retries == 1 and slept == [4] and rep.embedded == 5


def test_daily_quota_stops_but_keeps_progress(tmp_path):
    calls = []

    def quota_after_first(texts):
        if calls:
            raise rate_limit("Please retry in 20h1m2s.")
        calls.append(1)
        return [[1.0, 0.0]] * len(texts)

    rep = BatchReport()
    with pytest.raises(RateLimitError):
        embed_records(
            RECORDS,
            VectorCache(tmp_path),
            batch_size=2,
            embed=quota_after_first,
            log=lambda *_: None,
            report=rep,
        )
    assert VectorCache(tmp_path).ids == ["c0", "c1"]
    assert rep.embedded == 2  # the caller's report survives the error


def test_batches_respect_token_budget(tmp_path):
    calls = []
    recs = [{"chunk_id": f"t{i}", "text": "x", "token_count": 300} for i in range(10)]
    embed_records(
        recs, VectorCache(tmp_path), token_budget=1000, embed=fake_embed(calls), log=lambda *_: None
    )
    assert calls == [3, 3, 3, 1]


def test_rate_limit_without_delay_waits_a_minute(tmp_path):
    inner, slept, failed = fake_embed([]), [], []

    def flaky(texts):
        if not failed:
            failed.append(1)
            raise rate_limit("You exceeded your current quota")
        return inner(texts)

    embed_records(
        RECORDS, VectorCache(tmp_path), embed=flaky, sleep=slept.append, log=lambda *_: None
    )
    assert slept == [61]
