from __future__ import annotations

from .interfaces import LLM
from .models import Citation, RAGAnswer, SearchResult
from .retriever import Retriever

SYSTEM_PROMPT = (
    "You are a retrieval-augmented assistant. Answer the user's question using ONLY the "
    "provided context. Cite every fact with bracketed numbers that match the context blocks, "
    "for example [1] or [2][3]. If the context does not contain the answer, reply exactly: "
    '"I don\'t have enough information in the provided documents to answer that." '
    "Never use outside knowledge and never invent citations."
)

REFUSAL = "I don't have enough information in the provided documents to answer that."


def _snippet(text: str, limit: int = 240) -> str:
    cleaned = " ".join(text.split())
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 1].rstrip() + "…"


class RagPipeline:
    def __init__(
        self,
        retriever: Retriever,
        llm: LLM,
        min_score: float = 0.15,
    ) -> None:
        self._retriever = retriever
        self._llm = llm
        self._min_score = min_score

    @property
    def retriever(self) -> Retriever:
        return self._retriever

    @property
    def llm(self) -> LLM:
        return self._llm

    def answer(self, question: str, top_k: int | None = None) -> RAGAnswer:
        results = self._retriever.retrieve(question)
        if top_k is not None:
            results = results[:top_k]
        contexts = [r for r in results if r.score >= self._min_score]
        if not contexts:
            return RAGAnswer(
                question=question,
                answer=REFUSAL,
                citations=[],
                contexts=results,
                used_context=False,
            )

        prompt = self._build_prompt(question, contexts)
        answer = self._llm.chat(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
        citations = [
            Citation(
                index=i,
                source=result.document.source,
                chunk_id=result.document.id,
                score=result.score,
                snippet=_snippet(result.document.text),
            )
            for i, result in enumerate(contexts, start=1)
        ]
        return RAGAnswer(
            question=question,
            answer=answer,
            citations=citations,
            contexts=contexts,
            used_context=True,
        )

    def _build_prompt(self, question: str, contexts: list[SearchResult]) -> str:
        blocks = []
        for i, result in enumerate(contexts, start=1):
            blocks.append(f"[{i}] source: {result.document.source}\n{result.document.text}")
        context_text = "\n\n".join(blocks)
        return f"Context:\n{context_text}\n\nQuestion: {question}\n\nAnswer with citations:"
