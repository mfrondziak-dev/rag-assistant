import numpy as np

from rag.models import Document
from rag.store import VectorStore


def _doc(doc_id, text):
    return Document(id=doc_id, text=text, source=f"{doc_id}.md")


def test_add_and_search_returns_closest():
    store = VectorStore()
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    store.add(vectors, [_doc("a", "alpha"), _doc("b", "beta")])

    results = store.search(np.array([1.0, 0.0], dtype=np.float32), k=1)

    assert len(results) == 1
    assert results[0].document.id == "a"
    assert results[0].score > 0.99


def test_dimension_mismatch_raises():
    store = VectorStore()
    store.add(np.array([[1.0, 0.0]], dtype=np.float32), [_doc("a", "alpha")])
    try:
        store.add(np.array([[1.0, 0.0, 0.0]], dtype=np.float32), [_doc("b", "beta")])
    except ValueError:
        return
    raise AssertionError("expected ValueError on dimension mismatch")


def test_save_and_load_round_trip(tmp_path):
    store = VectorStore()
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    store.add(vectors, [_doc("a", "alpha"), _doc("b", "beta")])
    store.save(tmp_path)

    restored = VectorStore.load(tmp_path)
    results = restored.search(np.array([0.0, 1.0], dtype=np.float32), k=1)

    assert len(restored) == 2
    assert results[0].document.id == "b"


def test_search_on_empty_store_returns_empty():
    assert VectorStore().search(np.array([1.0, 0.0], dtype=np.float32), k=3) == []
