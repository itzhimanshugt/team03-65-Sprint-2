"""VerifAI chat UI. Run the API first, then: streamlit run app/ui/streamlit_app.py"""

import os

import httpx
import streamlit as st

API = os.getenv("VERIFAI_API", "http://127.0.0.1:8000")

st.set_page_config(page_title="VerifAI", page_icon="✅")
st.title("VerifAI")
st.caption("Cited answers from your firm's approved documents. Facts, not investment advice.")

with st.sidebar:
    st.header("Filters")
    issuer = st.selectbox("Issuer", ["Any", "HSBC Mutual Fund", "PPFAS Mutual Fund", "SEBI"])
    doc_type = st.selectbox(
        "Document type", ["Any", "factsheet", "sid_kim", "circular", "research", "internal"]
    )
    if st.button("New chat"):
        st.session_state.turns = []

st.session_state.setdefault("turns", [])  # [(question, answer, citations, refusal)]


def show(answer: str, citations: list[dict], refusal: str | None) -> None:
    if refusal == "no_evidence":  # Mock UX S2c
        st.warning(answer)
        return
    if refusal == "advice":  # Mock UX S2d
        st.info("I can share facts, not investment advice.")
    st.markdown(answer)
    if citations:
        st.caption(" ".join(f"`[{c['n']}] {c['source_name']} · p.{c['page']}`" for c in citations))
        for c in citations:  # Mock UX S3: source panel
            with st.expander(f"[{c['n']}] {c['title']} · p.{c['page']}"):
                st.text(c["text"])


if not st.session_state.turns:  # Mock UX S1a
    st.subheader("Ask anything about your approved documents")
    st.write("Every answer comes with its sources. Try:")
    for example in (
        "What is the exit load of HSBC Value Fund?",
        "What is the benchmark of Parag Parikh Flexi Cap Fund?",
    ):
        st.code(example, language=None)

for q, a, cites, refusal in st.session_state.turns:
    st.chat_message("user").write(q)
    with st.chat_message("assistant"):
        show(a, cites, refusal)

if question := st.chat_input("Ask about a fund, circular or firm policy"):
    st.chat_message("user").write(question)
    body = {
        "question": question,
        "history": [(q, a) for q, a, _, _ in st.session_state.turns[-4:]],
        "issuer": None if issuer == "Any" else issuer,
        "doc_type": None if doc_type == "Any" else doc_type,
    }
    with st.chat_message("assistant"):
        try:
            with st.spinner("Checking the approved documents…"):
                r = httpx.post(f"{API}/chat", json=body, timeout=60).raise_for_status().json()
        except httpx.HTTPError:  # Mock UX S2e
            st.error(
                "Something went wrong. The answer couldn't be generated. Your question is saved."
            )
            st.stop()
        show(r["answer"], r["citations"], r["refusal"])
    st.session_state.turns.append((question, r["answer"], r["citations"], r["refusal"]))
    st.rerun()  # redraw from history so the empty state (S1a) disappears
