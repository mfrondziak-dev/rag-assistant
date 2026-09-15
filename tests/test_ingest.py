from rag.config import Settings
from rag.ingest import ingest
from rag.store import VectorStore


def test_ingest_builds_and_persists_index(tmp_path, make_embedder):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "doc.md").write_text("alpha content for the index.", encoding="utf-8")

    settings = Settings()
    settings.index_dir = tmp_path / "index"
    settings.chunk_size = 100
    settings.chunk_overlap = 10

    store = ingest(settings, raw_dir, embedder=make_embedder(["alpha", "beta"]))

    assert len(store) >= 1
    restored = VectorStore.load(settings.index_dir)
    assert len(restored) == len(store)
