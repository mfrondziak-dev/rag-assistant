from rag.models import Document
from rag.pipeline import REFUSAL, RagPipeline
from rag.retriever import Retriever
from rag.store import VectorStore


def _pipeline(make_embedder, make_llm, reply="Alpha is documented here [1]."):
    embedder = make_embedder(["alpha", "beta"])
    store = VectorStore()
    documents = [
        Document(id="d1", text="alpha project details", source="alpha.md"),
        Document(id="d2", text="beta unrelated topic", source="beta.md"),
    ]
    store.add(embedder.embed([d.text for d in documents]), documents)
    retriever = Retriever(store, embedder, top_k=2, mmr_lambda=1.0)
    llm = make_llm(reply)
    return RagPipeline(retriever=retriever, llm=llm), llm


def test_answer_uses_context_and_cites_source(make_embedder, make_llm):
    pipeline, llm = _pipeline(make_embedder, make_llm)

    result = pipeline.answer("alpha")

    assert result.used_context is True
    assert result.answer == "Alpha is documented here [1]."
    assert len(result.citations) == 1
    assert result.citations[0].source == "alpha.md"
    assert result.citations[0].index == 1
    assert llm.calls


def test_refuses_without_relevant_context(make_embedder, make_llm):
    pipeline, llm = _pipeline(make_embedder, make_llm)

    result = pipeline.answer("gamma topic not present")

    assert result.used_context is False
    assert result.answer == REFUSAL
    assert result.citations == []
    assert llm.calls == []


def test_prompt_numbers_each_context(make_embedder, make_llm):
    pipeline, llm = _pipeline(make_embedder, make_llm)

    pipeline.answer("alpha")

    prompt = llm.calls[0][1]["content"]
    assert "[1]" in prompt
    assert "Question: alpha" in prompt
