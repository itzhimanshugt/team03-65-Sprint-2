# C39 — Cache, request log and /stats (live)

Asked "What is the benchmark of HSBC Gilt Fund?" twice. Last 2 lines of `data/logs/requests.jsonl`:
```json
{"ts": "2026-10-24T15:32:27", "question": "What is the benchmark of HSBC Gilt Fund?", "cached": false, "refusal": null, "cited_doc_ids": ["dad15eb3423a"], "latency_s": 2.578}
{"ts": "2026-10-24T15:32:28", "question": "What is the benchmark of HSBC Gilt Fund?", "cached": true, "refusal": null, "latency_s": 6.430000212276354e-05}
```

`GET /stats`
```json
{"requests":14,"cache_hits":3,"refusals":1,"p95_latency_s":9.28}
```

The second request is `"cached": true`, with near-zero latency and no embedding or LLM call. The log holds the question, refusal, cited doc ids and latency only: no keys, no prompts.
