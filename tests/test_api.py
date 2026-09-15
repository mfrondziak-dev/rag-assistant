import pytest
from fastapi.testclient import TestClient

from rag.api import app, get_pipeline
from rag.models import Document
from rag.pipeline import RagPipeline
from rag.rerank import LLMReranker
from rag.retriever import Retriever
from rag.store import VectorStore


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def _offline_pipeline(make_embedder, make_llm, reranker=None):
    embedder = make_embedder(["alpha", "beta"])
    store = VectorStore()
    documents = [
        Document(id="d1", text="alpha project details", source="alpha.md"),
        Document(id="d2", text="alpha secondary note", source="alpha2.md"),
        Document(id="d3", text="beta unrelated topic", source="beta.md"),
    ]
    store.add(embedder.embed([d.text for d in documents]), documents)
    retriever = Retriever(store, embedder, top_k=2, mmr_lambda=1.0, reranker=reranker)
    return RagPipeline(retriever=retriever, llm=make_llm("Answer with citation [1]."))


def test_health_reports_status():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "no_index"}
    assert {"index_size", "embed_model", "chat_model"} <= body.keys()


def test_ask_returns_answer_and_citations(make_embedder, make_llm):
    app.dependency_overrides[get_pipeline] = lambda: _offline_pipeline(make_embedder, make_llm)
    response = TestClient(app).post("/ask", json={"question": "alpha"})

    assert response.status_code == 200
    body = response.json()
    assert body["used_context"] is True
    assert body["answer"] == "Answer with citation [1]."
    assert len(body["citations"]) >= 1
    assert body["citations"][0]["source"].startswith("alpha")


def test_ask_validates_empty_question(make_embedder, make_llm):
    app.dependency_overrides[get_pipeline] = lambda: _offline_pipeline(make_embedder, make_llm)
    response = TestClient(app).post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_search_returns_hits(make_embedder, make_llm):
    app.dependency_overrides[get_pipeline] = lambda: _offline_pipeline(make_embedder, make_llm)
    response = TestClient(app).post("/search", json={"question": "alpha", "top_k": 2})

    assert response.status_code == 200
    results = response.json()["results"]
    assert 1 <= len(results) <= 2
    assert results[0]["score"] >= results[-1]["score"]


class _ScriptedLLM:
    def __init__(self, replies):
        self._replies = list(replies)

    def chat(self, messages, **options):
        return self._replies.pop(0)


def test_ask_pipeline_can_use_reranker(make_embedder, make_llm):
    reranker = LLMReranker(_ScriptedLLM(["1", "9", "5"]), top_n=2)
    pipeline = _offline_pipeline(make_embedder, make_llm, reranker=reranker)
    app.dependency_overrides[get_pipeline] = lambda: pipeline

    response = TestClient(app).post("/ask", json={"question": "alpha"})

    assert response.status_code == 200
    assert response.json()["citations"][0]["source"] == "alpha2.md"
