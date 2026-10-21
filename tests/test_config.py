from app.config import get_settings


def test_defaults_match_prd(monkeypatch):
    for var in (
        "CHUNK_SIZE",
        "CHUNK_OVERLAP",
        "TOP_K",
        "REFUSAL_THRESHOLD",
        "EMBEDDING_MODEL",
        "LLM_MODEL",
        "LLM_FALLBACK_MODELS",
    ):
        monkeypatch.delenv(var, raising=False)
    s = get_settings()
    assert (s.chunk_size, s.chunk_overlap, s.top_k) == (400, 60, 5)
    assert s.refusal_threshold == 0.45
    assert s.embedding_model == "gemini-embedding-001"
    assert s.llm_model == "gemini-3.1-flash-lite"
    assert s.llm_fallback_models[0] == "gemini-2.5-flash-lite"


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("TOP_K", "8")
    assert get_settings().top_k == 8
