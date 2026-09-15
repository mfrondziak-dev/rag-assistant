import pytest

docx = pytest.importorskip("docx")

from rag.text import load_documents, read_file  # noqa: E402


def _make_docx(path, paragraphs, table_rows=None):
    document = docx.Document()
    for paragraph in paragraphs:
        document.add_paragraph(paragraph)
    if table_rows:
        table = document.add_table(rows=len(table_rows), cols=len(table_rows[0]))
        for row_index, row in enumerate(table_rows):
            for col_index, value in enumerate(row):
                table.rows[row_index].cells[col_index].text = value
    document.save(path)


def test_read_file_extracts_docx_text(tmp_path):
    path = tmp_path / "cv.docx"
    _make_docx(path, ["Gamma content about vectors.", "Second paragraph."])

    text = read_file(path)

    assert "Gamma content about vectors." in text
    assert "Second paragraph." in text


def test_read_file_extracts_docx_tables(tmp_path):
    path = tmp_path / "pricing.docx"
    _make_docx(path, ["Plans below."], table_rows=[["Plan", "Price"], ["Team", "899 PLN"]])

    text = read_file(path)

    assert "899 PLN" in text
    assert "Plan | Price" in text


def test_load_documents_includes_docx(tmp_path):
    (tmp_path / "note.md").write_text("markdown about alpha.", encoding="utf-8")
    _make_docx(tmp_path / "report.docx", ["DOCX report about beta"])

    documents = load_documents(tmp_path, chunk_size=200, chunk_overlap=20)

    assert len(documents) == 2
    assert any(d.metadata["suffix"] == ".docx" for d in documents)
    assert any("beta" in d.text for d in documents if d.metadata["suffix"] == ".docx")
