import pytest
from pypdf import PdfReader, PdfWriter

from ingestion.loaders import UnsupportedDocumentError, load_document


def make_pdf(path, pages):
    """Write a minimal valid PDF with one text line per page."""
    objs = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        None,
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    kids = []
    for text in pages:
        stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET"
        objs.append(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
        objs.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {len(objs)} 0 R >>"
        )
        kids.append(f"{len(objs)} 0 R")
    objs[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>"
    out, offsets = b"%PDF-1.4\n", []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{body}\nendobj\n".encode()
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    out += "".join(f"{o:010d} 00000 n \n" for o in offsets).encode()
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    path.write_bytes(out)
    return path


def test_pdf_keeps_page_numbers(tmp_path):
    doc = load_document(make_pdf(tmp_path / "f.pdf", ["Exit load 1 percent", "Expense ratio 0.68"]))
    assert doc.format == "pdf"
    assert [p for p, _ in doc.pages] == [1, 2]
    assert "Expense ratio" in doc.pages[1][1]


def test_html_drops_scripts_and_splits_on_headings(tmp_path):
    f = tmp_path / "a.html"
    f.write_text(
        "<html><body><nav>Menu</nav><script>var x=1</script><article>"
        "<h1>NAV</h1><p>NAV is net asset value.</p><h2>Exit load</h2><p>A redemption fee.</p>"
        "</article><footer>Copyright</footer></body></html>",
        encoding="utf-8",
    )
    doc = load_document(f)
    assert doc.format == "html" and len(doc.pages) == 2
    assert "Menu" not in doc.text and "var x" not in doc.text and "Copyright" not in doc.text
    assert doc.pages[1][1].startswith("Exit load")


def test_markdown_sections_and_txt(tmp_path):
    md = tmp_path / "n.md"
    md.write_text("# FAQ\nIntro\n## Q1\nAnswer one\n## Q2\nAnswer two", encoding="utf-8")
    assert len(load_document(md).pages) == 3
    txt = tmp_path / "n.txt"
    txt.write_text("Shelf notes", encoding="utf-8")
    assert load_document(txt).pages == [(1, "Shelf notes")]


@pytest.mark.parametrize(
    "name, setup, reason",
    [
        ("x.docx", lambda p: p.write_bytes(b"x"), "Unsupported file type"),
        ("empty.txt", lambda p: p.write_text("   "), "No selectable text"),
    ],
)
def test_rejections(tmp_path, name, setup, reason):
    path = tmp_path / name
    setup(path)
    with pytest.raises(UnsupportedDocumentError, match=reason):
        load_document(path)


def test_scanned_and_encrypted_pdfs_rejected(tmp_path):
    writer = PdfWriter()
    writer.add_blank_page(612, 792)
    writer.write(tmp_path / "scan.pdf")
    with pytest.raises(UnsupportedDocumentError, match="No selectable text"):
        load_document(tmp_path / "scan.pdf")

    writer = PdfWriter(clone_from=PdfReader(make_pdf(tmp_path / "p.pdf", ["secret"])))
    writer.encrypt("pw")
    writer.write(tmp_path / "locked.pdf")
    with pytest.raises(UnsupportedDocumentError, match="password"):
        load_document(tmp_path / "locked.pdf")


def test_oversized_file_rejected(tmp_path, monkeypatch):
    import ingestion.loaders as loaders

    monkeypatch.setattr(loaders, "MAX_BYTES", 10)
    f = tmp_path / "big.txt"
    f.write_text("more than ten bytes", encoding="utf-8")
    with pytest.raises(UnsupportedDocumentError, match="25 MB"):
        load_document(f)
