"""Knowledge base: indexed documents and the upload form (Mock UX S4/S5)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402
import streamlit as st  # noqa: E402
from common import API, get, style  # noqa: E402

style()

st.markdown(
    '<h1 class="vf-h1">Knowledge base</h1>'
    '<p class="vf-lede">The documents compliance has approved. Only the latest version of each '
    "is searched; older versions stay on record.</p>",
    unsafe_allow_html=True,
)

docs = get("/documents", [])
if not docs:  # Mock UX S4a
    st.info("No approved documents yet. Upload the first one below.", icon=":material/folder_open:")
else:
    m1, m2, m3 = st.columns(3)
    m1.metric("Documents", len(docs))
    m2.metric("Chunks indexed", f'{sum(d["chunks"] for d in docs):,}')
    m3.metric("Superseded versions", sum(not d["is_latest"] for d in docs))
    st.dataframe(
        [
            {
                "Title": d["title"],
                "Type": d["doc_type"],
                "Issuer": d["issuer"],
                "Published": d["published_date"],
                "Version": d["version"],
                "Status": "Latest" if d["is_latest"] else "Superseded",
                "Chunks": d["chunks"],
            }
            for d in docs
        ],
        hide_index=True,
        use_container_width=True,
    )

st.markdown('<h3 class="vf-h3">Upload an approved document</h3>', unsafe_allow_html=True)
with st.form("upload", border=True):
    file = st.file_uploader(
        "PDF, HTML, TXT or MD, up to 25 MB", type=["pdf", "html", "htm", "txt", "md"]
    )
    c1, c2 = st.columns(2)
    title = c1.text_input("Title")
    issuer = c2.text_input("Issuer", placeholder="e.g. HSBC Mutual Fund")
    c3, c4, c5, c6 = st.columns(4)
    doc_type = c3.selectbox("Type", ["factsheet", "sid_kim", "circular", "research", "internal"])
    family = c4.text_input("Family", help="Versions of the same document share a family")
    published = c5.date_input("Published")
    version = c6.number_input("Version", min_value=1, value=1)
    sent = st.form_submit_button("Index document", type="primary", icon=":material/upload:")

if sent:
    if not (file and title and issuer and family):
        st.warning("Add the file, title, issuer and family before indexing.")
    else:
        try:
            r = httpx.post(
                f"{API}/documents",
                files={"file": (file.name, file.getvalue())},
                data={
                    "title": title,
                    "doc_type": doc_type,
                    "issuer": issuer,
                    "family": family,
                    "published_date": published.isoformat(),
                    "version": version,
                },
                timeout=300,
            )
        except httpx.HTTPError:
            st.error("The API could not be reached. Nothing was indexed.")
        else:
            if r.status_code == 201:
                out = r.json()
                note = (
                    f", replacing {out['superseded_chunks']} older chunks"
                    if out["superseded_chunks"]
                    else ""
                )
                st.success(
                    f"Indexed: {out['chunks']} chunks{note}.", icon=":material/check_circle:"
                )
            else:  # Mock UX S5a: say exactly why
                st.error(f"We couldn't index this file. {r.json().get('detail', r.text)}")
