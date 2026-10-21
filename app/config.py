"""Application settings loaded from environment variables (see .env.example)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# Free-tier quotas are per model, so when one model's daily quota runs out we try the next.
DEFAULT_FALLBACKS = "gemini-2.5-flash-lite,gemini-3-flash-preview,gemini-2.5-flash"


@dataclass(frozen=True)
class Settings:
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    llm_fallback_models: tuple[str, ...]
    llm_temperature: float
    llm_max_tokens: int
    llm_reasoning_effort: str
    embedding_model: str
    chroma_path: str
    chunk_size: int
    chunk_overlap: int
    top_k: int
    refusal_threshold: float


def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_base_url=os.getenv("LLM_BASE_URL", GEMINI_BASE_URL),
        llm_model=os.getenv("LLM_MODEL", "gemini-3.1-flash-lite"),
        llm_fallback_models=tuple(
            m.strip()
            for m in os.getenv("LLM_FALLBACK_MODELS", DEFAULT_FALLBACKS).split(",")
            if m.strip()
        ),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "600")),
        llm_reasoning_effort=os.getenv("LLM_REASONING_EFFORT", "none"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "gemini-embedding-001"),
        chroma_path=os.getenv("CHROMA_PATH", "data/chroma"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "400")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "60")),
        top_k=int(os.getenv("TOP_K", "5")),
        refusal_threshold=float(os.getenv("REFUSAL_THRESHOLD", "0.45")),
    )
