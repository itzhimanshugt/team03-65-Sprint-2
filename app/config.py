"""Application settings loaded from environment variables (see .env.example)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    llm_api_key: str
    llm_model: str
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
        llm_model=os.getenv("LLM_MODEL", ""),
        embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),
        chroma_path=os.getenv("CHROMA_PATH", "data/chroma"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "400")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "60")),
        top_k=int(os.getenv("TOP_K", "5")),
        refusal_threshold=float(os.getenv("REFUSAL_THRESHOLD", "0.45")),
    )
