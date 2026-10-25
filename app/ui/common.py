"""Shared bits for the VerifAI Streamlit pages: API calls, stylesheet, small HTML helpers."""

import html
import json
import os
from pathlib import Path

import httpx
import streamlit as st

API = os.getenv("VERIFAI_API", "http://127.0.0.1:8000")
CSS = Path(__file__).with_name("style.css").read_text(encoding="utf-8")


def style() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def esc(value) -> str:
    return html.escape(str(value))


def badge(text: str, tone: str = "") -> str:
    return f'<span class="vf-badge {tone}">{esc(text)}</span>'


def get(path: str, default=None):
    try:
        return httpx.get(f"{API}{path}", timeout=10).raise_for_status().json()
    except (httpx.HTTPError, ValueError):
        return default


def stream_answer(body: dict, done: dict):
    """Yield answer tokens from POST /chat/stream; the final `done` payload lands in `done`."""
    with httpx.stream("POST", f"{API}/chat/stream", json=body, timeout=120) as resp:
        resp.raise_for_status()
        event = None
        for line in resp.iter_lines():
            if line.startswith("event: "):
                event = line[7:]
            elif line.startswith("data: "):
                data = json.loads(line[6:])
                if event == "token":
                    yield data
                elif event == "done":
                    done.update(data)
                elif event == "error":
                    raise httpx.HTTPError(data["message"])
