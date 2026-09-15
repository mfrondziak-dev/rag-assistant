from __future__ import annotations

import json
import re

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

FOLLOWUP_PROMPT = (
    "You propose follow-up questions for a document assistant. Given the user's question and "
    "the assistant's answer, write {count} short follow-up questions the user could ask next, "
    "answerable from the same documents. Reply with a JSON array of strings and nothing else. "
    "Do not number them and do not add explanations."
)

REFUSAL = "I don't have enough information in the provided documents to answer that."


def parse_followups(raw: str, limit: int | None = None) -> list[str]:
    items: list[str] = []
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, list):
                items = [str(item).strip() for item in data if str(item).strip()]
        except (ValueError, TypeError):
            items = []
    if not items:
        bulleted: list[str] = []
        plain: list[str] = []
        for line in raw.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if re.match(r"^(?:\d+[.)]|[-*•])\s+", stripped):
                cleaned = re.sub(r"^(?:\d+[.)]|[-*•])\s+", "", stripped).strip().strip('"').strip()
                if cleaned:
                    bulleted.append(cleaned)
            else:
                plain.append(stripped.strip('"').strip())
        items = bulleted or [item for item in plain if item]
    return items[:limit] if limit else items



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

    def suggest_followups(
        self,
        question: str,
        answer: str,
        contexts: list[SearchResult] | None = None,
        count: int = 3,
    ) -> list[str]:
        if count <= 0:
            return []
        parts = [f"Question: {question}", f"Answer: {answer}"]
        if contexts:
            context_text = "\n\n".join(result.document.text for result in contexts[:2])
            parts.append(f"Context:\n{context_text}")
        raw = self._llm.chat(
            [
                {"role": "system", "content": FOLLOWUP_PROMPT.format(count=count)},
                {"role": "user", "content": "\n\n".join(parts)},
            ]
        )
        return parse_followups(raw, limit=count)
