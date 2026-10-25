"""Activity log: usage totals and recent questions (Mock UX S6, US-12)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st  # noqa: E402
from common import get, style  # noqa: E402

style()

st.markdown(
    '<h1 class="vf-h1">Activity log</h1>'
    '<p class="vf-lede">Every question, what it cited and whether it was declined. '
    "No API keys or prompts are logged.</p>",
    unsafe_allow_html=True,
)

s = get("/stats", {})
m1, m2, m3, m4 = st.columns(4)
m1.metric("Requests", s.get("requests", 0))
m2.metric("Served from cache", s.get("cache_hits", 0))
m3.metric("Declined", s.get("refusals", 0))
m4.metric("p95 latency", f'{s.get("p95_latency_s", 0):.1f} s')

rows = get("/activity", [])
if not rows:
    st.info("No questions yet. Ask one on the Ask page.", icon=":material/forum:")
else:
    st.dataframe(
        [
            {
                "Time": r.get("ts", ""),
                "Question": r.get("question", ""),
                "Outcome": r.get("refusal") or "answered",
                "Cited documents": ", ".join(r.get("cited_doc_ids", [])),
                "Cached": "yes" if r.get("cached") else "",
                "Latency (s)": round(r.get("latency_s", 0), 2),
            }
            for r in rows
        ],
        hide_index=True,
        use_container_width=True,
    )
