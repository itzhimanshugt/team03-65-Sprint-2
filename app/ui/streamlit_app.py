"""VerifAI web app. Run the API first, then: streamlit run app/ui/streamlit_app.py

Layout and states follow the Mock UX (docs/MOCK_UX_ANNOTATIONS.md, Figma file linked there):
Ask (S1/S2 + S3 evidence panel), Knowledge base (S4/S5) and Activity log (S6).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # for `common` under any runner

import streamlit as st  # noqa: E402
from common import get, style  # noqa: E402

st.set_page_config(page_title="VerifAI", page_icon=":material/verified:", layout="wide")
style()

with st.sidebar:
    st.markdown(
        '<div class="vf-brand">VerifAI</div>'
        '<div class="vf-tagline">Answers from approved documents only</div>',
        unsafe_allow_html=True,
    )

PAGES = [
    st.Page("pages/ask.py", title="Ask", icon=":material/forum:", default=True),
    st.Page("pages/knowledge.py", title="Knowledge base", icon=":material/folder_open:"),
    st.Page("pages/activity.py", title="Activity log", icon=":material/receipt_long:"),
]
nav = st.navigation(PAGES, position="hidden")  # links drawn below the brand, as in the Mock UX

with st.sidebar:
    for page in PAGES:
        st.page_link(page)
    health = get("/health", {})
    if health.get("chunks_indexed"):
        st.markdown(
            '<div class="vf-corpus"><span class="vf-dot"></span><b>Corpus verified</b>'
            f'<div class="vf-num">{health["chunks_indexed"]:,} chunks indexed</div>'
            '<div class="vf-muted">Latest document versions only</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="vf-corpus warn"><b>API unreachable</b>'
            '<div class="vf-muted">Start it with: uvicorn app.api.main:app</div></div>',
            unsafe_allow_html=True,
        )

nav.run()
