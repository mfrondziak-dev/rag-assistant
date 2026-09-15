from rag.text import chunk_text, load_documents


def test_short_text_single_chunk():
    assert chunk_text("Hello world.", size=100, overlap=10) == ["Hello world."]


def test_empty_text_returns_no_chunks():
    assert chunk_text("   \n  ") == []


def test_long_text_is_split_within_size():
    text = ". ".join(f"Sentence number {i} with some extra words" for i in range(200))
    chunks = chunk_text(text, size=300, overlap=50)
    assert len(chunks) > 1
    assert all(len(chunk) <= 300 for chunk in chunks)


def test_chunk_text_rejects_bad_overlap():
    try:
        chunk_text("abc", size=10, overlap=10)
    except ValueError:
        return
    raise AssertionError("expected ValueError for overlap >= size")


def test_load_documents_reads_supported_files(tmp_path):
    (tmp_path / "a.md").write_text("# Title\nalpha content goes here.", encoding="utf-8")
    (tmp_path / "b.txt").write_text("beta content goes here.", encoding="utf-8")
    (tmp_path / "ignore.bin").write_text("nope", encoding="utf-8")

    documents = load_documents(tmp_path, chunk_size=100, chunk_overlap=10)
    ids = {doc.id for doc in documents}
    sources = {doc.source for doc in documents}

    assert len(documents) == 2
    assert len(ids) == 2
    assert any(source.endswith("a.md") for source in sources)
    assert all(doc.text for doc in documents)
