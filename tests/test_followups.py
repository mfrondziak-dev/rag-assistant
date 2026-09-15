from rag.models import Document
from rag.pipeline import RagPipeline, parse_followups
from rag.retriever import Retriever
from rag.store import VectorStore


def test_parse_followups_from_json():
    assert parse_followups('["What is X?", "What about Y?"]') == ["What is X?", "What about Y?"]


def test_parse_followups_from_bullet_list():
    raw = "Here you go:\n- What is X?\n2. What about Y?"
    assert parse_followups(raw) == ["What is X?", "What about Y?"]


def test_parse_followups_respects_limit():
    assert parse_followups('["A", "B", "C"]', limit=2) == ["A", "B"]


def _pipeline_with(embedder, llm):
    store = VectorStore()
    documents = [Document(id="d1", text="alpha project details", source="alpha.md")]
    store.add(embedder.embed([doc.text for doc in documents]), documents)
    retriever = Retriever(store, embedder, top_k=1, mmr_lambda=1.0)
    return RagPipeline(retriever=retriever, llm=llm)


def test_suggest_followups_returns_list(make_embedder, make_llm):
    llm = make_llm('["What is X?", "What about Y?"]')
    pipeline = _pipeline_with(make_embedder(["alpha", "beta"]), llm)

    suggestions = pipeline.suggest_followups("alpha?", "Alpha answer.", count=2)

    assert suggestions == ["What is X?", "What about Y?"]
    assert llm.calls


def test_suggest_followups_disabled_with_zero(make_embedder, make_llm):
    llm = make_llm('["A"]')
    pipeline = _pipeline_with(make_embedder(["alpha"]), llm)

    assert pipeline.suggest_followups("q", "a", count=0) == []
    assert llm.calls == []
