"""Ask: question card, grounded answer, citation cards, pipeline audit, evidence panel (S1–S3)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # for `common` when run on its own

import httpx  # noqa: E402
import streamlit as st  # noqa: E402
from common import badge, esc, stream_answer, style  # noqa: E402

style()

EXAMPLES = [
    "What is the exit load of HSBC Value Fund?",
    "What is the benchmark of Parag Parikh Flexi Cap Fund?",
    "What is the cut-off time for liquid fund subscriptions?",
]
ISSUERS = ["All issuers", "HSBC Mutual Fund", "PPFAS Mutual Fund", "SEBI"]
DOC_TYPES = ["All document types", "factsheet", "sid_kim", "circular", "research", "internal"]
CONTEXT_BUDGET = 3000

st.session_state.setdefault("turns", [])  # each: question, answer, citations, refusal, trace
st.session_state.setdefault("evidence", None)  # citation number open in the evidence panel


def ask(question: str, issuer: str, doc_type: str) -> None:
    body = {
        "question": question,
        "history": [(t["question"], t["answer"]) for t in st.session_state.turns[-4:]],
        "issuer": None if issuer == ISSUERS[0] else issuer,
        "doc_type": None if doc_type == DOC_TYPES[0] else doc_type,
    }
    done: dict = {}
    with st.container(key="card-stream"):
        st.markdown(
            badge("Retrieving and verifying", "pending")
            + '<span class="vf-muted">The free-tier model can take up to a minute.</span>',
            unsafe_allow_html=True,
        )
        try:
            st.write_stream(stream_answer(body, done))
        except httpx.HTTPError:  # Mock UX S2e
            st.error(
                "Something went wrong. The answer couldn't be generated. Your question is saved."
            )
            st.session_state.draft = question
            st.stop()
    st.session_state.turns.append({"question": question, **done})
    st.session_state.evidence = None
    st.rerun()


def answer_card(turn: dict) -> None:
    trace, cites, refusal = turn.get("trace", {}), turn.get("citations", []), turn.get("refusal")
    with st.container(key="card-answer"):
        if refusal == "no_evidence":  # Mock UX S2c
            st.markdown(badge("Not enough evidence", "warn"), unsafe_allow_html=True)
            st.markdown(
                f'<div class="vf-answer">{esc(turn["answer"])}</div>', unsafe_allow_html=True
            )
            top = trace.get("top_score")
            if top is not None:
                st.caption(
                    f"Best match scored {top:.2f}, below the {trace.get('threshold', 0.72):.2f} "
                    "evidence threshold, so no answer was generated."
                )
            return
        badges = badge("Grounded in approved documents", "ok")
        if refusal == "advice":
            badges = badge("Facts only — advice declined", "red")
        st.markdown(badges, unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Top match", f"{trace.get('top_score', 0):.0%}")
        m2.metric("Sources cited", len(cites))
        model = trace.get("model", "—").removeprefix("gemini-").replace("-", " ").title()
        m3.metric("Model", model, help=trace.get("model"))
        text = turn["answer"]
        if refusal == "advice":  # Mock UX S2d: the boundary first, then the facts
            notice, _, text = text.partition("\n\n")
            st.markdown(
                f'<div class="vf-boundary"><b>Advice boundary</b><div>{esc(notice)}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown(text)
    if cites:
        st.markdown('<h3 class="vf-h3">Sources behind this answer</h3>', unsafe_allow_html=True)
        cols = st.columns(min(3, len(cites)))
        for i, c in enumerate(cites):
            match = badge(f"{c.get('score', 0):.0%} match", "ok")
            with cols[i % len(cols)].container(key=f"card-cite-{i}"):
                st.markdown(
                    f'<div class="vf-cite-head"><span class="vf-tag">[{c["n"]}]</span>{match}</div>'
                    f'<div class="vf-cite-title">{esc(c["title"])}</div>'
                    f'<div class="vf-num">Page {esc(c["page"])} · '
                    f'{esc(c.get("published_date", ""))}</div>'
                    f'<div class="vf-excerpt">“{esc(c["text"][:150].strip())}…”</div>',
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Inspect passage",
                    key=f"inspect-{len(st.session_state.turns)}-{c['n']}",
                    icon=":material/arrow_forward:",
                    type="tertiary",
                ):
                    st.session_state.evidence = c["n"]
                    st.rerun()
    if trace.get("candidates"):
        with st.expander(
            "Why this answer? How the pipeline got here", icon=":material/account_tree:"
        ):
            s1, s2, s3, s4 = st.columns(4)
            standalone = turn.get("standalone_question", turn["question"])
            stage(
                s1,
                "Query",
                "As asked" if standalone == turn["question"] else "Rewritten",
                standalone if standalone != turn["question"] else "No follow-up context needed",
            )
            stage(
                s2,
                "Vector search",
                f'{trace["candidates"]} candidates',
                f'Top cosine {trace["top_score"]:.2f} · latest versions',
            )
            stage(
                s3,
                "Re-rank + gate",
                f'{trace["reranked"]} kept',
                f'{trace["top_score"]:.2f} ≥ {trace["threshold"]:.2f} threshold — passed',
            )
            used = trace.get("context_tokens", 0)
            stage(
                s4,
                "Context",
                f"{used:,} / {CONTEXT_BUDGET:,} tokens",
                f'{trace.get("context_chunks", 0)} chunks, '
                f'{trace.get("neighbours", 0)} same-page neighbours',
            )


def stage(col, name: str, value: str, note: str) -> None:
    col.markdown(
        f'<div class="vf-stage"><div class="vf-stage-name">{esc(name)}</div>'
        f'<div class="vf-stage-value">{esc(value)}</div>'
        f'<div class="vf-muted">{esc(note)}</div></div>',
        unsafe_allow_html=True,
    )


def evidence_panel(turn: dict | None) -> None:
    cites = {c["n"]: c for c in (turn or {}).get("citations", [])}
    c = cites.get(st.session_state.evidence)
    with st.container(key="card-evidence"):
        st.markdown('<h3 class="vf-h3">Evidence</h3>', unsafe_allow_html=True)
        if not c:  # Mock UX S3 resting state
            st.markdown(
                '<div class="vf-muted">Pick “Inspect passage” on a source to read the exact text '
                "the answer was built from.</div>",
                unsafe_allow_html=True,
            )
            return
        st.markdown(
            f'<div class="vf-cite-title">[{c["n"]}] {esc(c["title"])}</div>'
            '<table class="vf-meta">'
            f'<tr><td>Document</td><td>{esc(c["source_name"])}</td></tr>'
            f'<tr><td>Page</td><td>{esc(c["page"])}</td></tr>'
            f'<tr><td>Published</td><td>{esc(c.get("published_date", ""))}</td></tr>'
            f'<tr><td>Version</td><td>v{esc(c.get("version", 1))} · latest</td></tr>'
            f'<tr><td>Match</td><td>{c.get("score", 0):.3f} cosine</td></tr>'
            f'<tr><td>Chunk</td><td>{esc(c["chunk_id"])}</td></tr></table>'
            f'<div class="vf-quote">{esc(c["text"].strip())}</div>',
            unsafe_allow_html=True,
        )


st.markdown(
    '<h1 class="vf-h1">Ask the approved documents</h1>'
    '<p class="vf-lede">Every answer is built only from compliance-approved factsheets, scheme '
    "documents, SEBI circulars and firm policy — with the page it came from.</p>",
    unsafe_allow_html=True,
)

main, side = st.columns([1.8, 1], gap="large")
current = st.session_state.turns[-1] if st.session_state.turns else None

with main:
    with st.container(key="card-ask"):
        with st.form("ask", clear_on_submit=True, border=False):
            question = st.text_area(
                "Question",
                value=st.session_state.pop("draft", ""),
                placeholder="e.g. What is the exit load of HSBC Value Fund?",
                height=96,
            )
            f1, f2 = st.columns(2)
            issuer = f1.selectbox("Issuer", ISSUERS)
            doc_type = f2.selectbox("Document type", DOC_TYPES)
            submitted = st.form_submit_button(
                "Verify with sources", type="primary", icon=":material/verified:"
            )
        if not st.session_state.turns:  # Mock UX S1a
            st.markdown('<div class="vf-muted">Or try one:</div>', unsafe_allow_html=True)
            for i, example in enumerate(EXAMPLES):
                if st.button(example, key=f"example{i}", icon=":material/north_east:"):
                    st.session_state.pending = example
    if submitted and question.strip():
        ask(question.strip(), issuer, doc_type)
    elif pending := st.session_state.pop("pending", None):
        ask(pending, ISSUERS[0], DOC_TYPES[0])
    if current:
        answer_card(current)

with side:
    evidence_panel(current)
    if st.session_state.turns:
        with st.container(key="card-session"):
            st.markdown('<h3 class="vf-h3">This session</h3>', unsafe_allow_html=True)
            for t in reversed(st.session_state.turns):
                mark = "declined" if t.get("refusal") else f'{len(t.get("citations", []))} sources'
                st.markdown(
                    f'<div class="vf-turn">{esc(t["question"])}'
                    f'<span class="vf-muted"> · {mark}</span></div>',
                    unsafe_allow_html=True,
                )
            if st.button("New session", icon=":material/restart_alt:"):
                st.session_state.turns, st.session_state.evidence = [], None
                st.rerun()
