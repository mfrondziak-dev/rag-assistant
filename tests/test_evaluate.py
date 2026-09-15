from rag.evaluate import _parse_judgement, evaluate_retrieval
from rag.models import Document
from rag.retriever import Retriever
from rag.store import VectorStore


def test_parse_judgement_reads_json():
    verdict = _parse_judgement('Sure: {"grounded": true, "score": 0.9}')
    assert verdict.grounded is True
    assert verdict.score == 0.9


def test_parse_judgement_fallback_is_conservative():
    verdict = _parse_judgement("this is not json at all")
    assert verdict.grounded is False
    assert verdict.score == 0.0


def test_evaluate_retrieval_hit_rate(make_embedder):
    embedder = make_embedder(["alpha", "beta"])
    store = VectorStore()
    documents = [
        Document(id="a", text="alpha topic", source="alpha.md"),
        Document(id="b", text="beta topic", source="beta.md"),
    ]
    store.add(embedder.embed([d.text for d in documents]), documents)
    retriever = Retriever(store, embedder, top_k=2, mmr_lambda=1.0)

    dataset = [
        {"question": "alpha?", "relevant_sources": ["alpha.md"]},
        {"question": "gamma?", "relevant_sources": ["does-not-exist.md"]},
    ]
    metrics = evaluate_retrieval(retriever, dataset, k=2)

    assert metrics.questions == 2
    assert metrics.hit_rate == 0.5
    assert metrics.mrr == 0.5
