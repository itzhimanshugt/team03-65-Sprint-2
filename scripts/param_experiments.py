"""Effect of temperature, max_tokens, stop sequences and thinking on the same prompt.

Run: python -m scripts.param_experiments  (writes outputs/c7/param_experiments.md)
"""

from pathlib import Path

from app.llm import complete


def ask(content: str, **params):
    reply = complete([{"role": "user", "content": content}], **params)
    return reply.text.strip().replace("\n", " "), reply.finish_reason, reply.completion_tokens


lines = ["# C7 — Model parameters and output control", ""]

# 1. Temperature: run the same creative prompt 3 times per setting
prompt = "Write a one-line tagline for a compliance assistant for financial advisors."
lines += ["## 1. Temperature (same prompt, 3 runs each)", "", f"Prompt: _{prompt}_", ""]
lines += ["| Temperature | Run 1 | Run 2 | Run 3 | Distinct |", "|---|---|---|---|---|"]
for t in (0.0, 0.7, 1.5):
    outs = [ask(prompt, temperature=t, max_tokens=60)[0] for _ in range(3)]
    lines.append(f"| {t} | {' | '.join(outs)} | {len(set(outs))}/3 |")

# 2. max_tokens and finish_reason
prompt = "Explain the NAV of a mutual fund in 3 sentences."
lines += ["", "## 2. max_tokens", "", f"Prompt: _{prompt}_", ""]
lines += ["| max_tokens | finish_reason | Output tokens | Output |", "|---|---|---|---|"]
for mt in (20, 60, 300):
    text, reason, n = ask(prompt, max_tokens=mt)
    lines.append(f"| {mt} | {reason} | {n} | {text} |")

# 3. Stop sequence
lines += ["", "## 3. Stop sequence", "", "| stop | finish_reason | Output |", "|---|---|---|"]
for stop in (None, ["."]):
    text, reason, _ = ask(prompt, **({"stop": stop} if stop else {}))
    lines.append(f"| {stop} | {reason} | {text} |")

# 4. Gemini thinking eats the max_tokens budget
lines += [
    "",
    "## 4. Hidden thinking tokens (Gemini reasoning)",
    "",
    "| reasoning_effort | max_tokens |",
]
lines[-1] += " Visible output |"
lines.append("|---|---|---|")
for effort in ("none", "low"):
    text, _, _ = ask(prompt, max_tokens=60, reasoning_effort=effort)
    lines.append(f"| {effort} | 60 | {text or '(empty)'} |")

out = Path("outputs/c7/param_experiments.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines), encoding="utf-8")
print(out.read_text(encoding="utf-8"))
