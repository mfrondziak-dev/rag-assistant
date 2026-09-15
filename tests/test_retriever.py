from rag.models import Document
from rag.retriever import Retriever
from rag.store import VectorStore


def _store_with(embedder, items):
    store = VectorStore()
    documents = [Document(id=i, text=t, source=f"{i}.md") for i, t in items]
    store.add(embedder.embed([d.text for d in documents]), documents)
    return store


def test_retrieve_on_empty_store(make_embedder):
    store = VectorStore()
    retriever = Retriever(store, make_embedder(["alpha"]), top_k=3)
    assert retriever.retrieve("alpha") == []


def test_pure_relevance_selection(make_embedder):
    embedder = make_embedder(["alpha", "beta"])
    store = _store_with(embedder, [("a", "alpha"), ("b", "alpha"), ("c", "beta")])
    retriever = Retriever(store, embedder, top_k=2, mmr_lambda=1.0)

    ids = [r.document.id for r in retriever.retrieve("alpha")]

    assert ids == ["a", "b"]


def test_mmr_promotes_diversity(make_embedder):
    embedder = make_embedder(["alpha", "beta"])
    store = _store_with(embedder, [("a", "alpha"), ("b", "alpha"), ("c", "beta")])
    retriever = Retriever(store, embedder, top_k=2, mmr_lambda=0.0, fetch_k=3)

    ids = [r.document.id for r in retriever.retrieve("alpha")]

    assert "a" in ids
    assert "c" in ids
    assert "b" not in ids
