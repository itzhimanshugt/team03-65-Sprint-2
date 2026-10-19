from app.config import get_settings


def test_defaults_match_prd(monkeypatch):
    for var in (
        "CHUNK_SIZE",
        "CHUNK_OVERLAP",
        "TOP_K",
        "REFUSAL_THRESHOLD",
        "EMBEDDING_MODEL",
        "LLM_MODEL",
    ):
        monkeypatch.delenv(var, raising=False)
    s = get_settings()
    assert (s.chunk_size, s.chunk_overlap, s.top_k) == (400, 60, 5)
    assert s.refusal_threshold == 0.45
    assert s.embedding_model == "gemini-embedding-001"
    assert s.llm_model == "gemini-2.5-flash"


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("TOP_K", "8")
    assert get_settings().top_k == 8
