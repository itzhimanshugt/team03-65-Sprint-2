"""Prompt templates (prompts/*.md) and chat messages with explicit system and user roles."""

from pathlib import Path
from string import Template

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


def render_prompt(name: str, **values: str) -> str:
    """Fill `$placeholders` in prompts/<name>.md. A missing value raises KeyError."""
    text = (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8").strip()
    return Template(text).substitute(values)


def load_system_prompt(name: str = "system") -> str:
    return render_prompt(name)


def build_messages(user_message: str, system_prompt: str | None = None) -> list[dict]:
    """Return [system?, user] messages.

    The system message sets behaviour and rules; the user message carries the task.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_message})
    return messages
