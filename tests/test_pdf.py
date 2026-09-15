import pytest

pytest.importorskip("pypdf")

from rag.text import load_documents, read_file  # noqa: E402


def build_pdf(text: str) -> bytes:
    content = f"BT /F1 24 Tf 72 720 Td ({text}) Tj ET".encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref_position = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_position}\n%%EOF"
    ).encode()
    return bytes(out)


def test_read_file_extracts_pdf_text(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(build_pdf("Hello RAG PDF"))

    assert "Hello RAG PDF" in read_file(pdf_path)


def test_load_documents_includes_pdf(tmp_path):
    (tmp_path / "note.md").write_text("markdown content about alpha.", encoding="utf-8")
    (tmp_path / "report.pdf").write_bytes(build_pdf("PDF report about beta"))

    documents = load_documents(tmp_path, chunk_size=200, chunk_overlap=20)

    assert len(documents) == 2
    assert any(d.metadata["suffix"] == ".pdf" for d in documents)
    assert any("alpha" in d.text for d in documents if d.metadata["suffix"] == ".md")
