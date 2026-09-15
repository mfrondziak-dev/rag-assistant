from __future__ import annotations

import re

from .interfaces import LLM
from .models import SearchResult

RERANK_PROMPT = (
    "You are a relevance judge for a retrieval system. Given a user question and a candidate "
    "passage, rate how relevant the passage is for answering the question on a scale from 0 "
    "(irrelevant) to 10 (essential). Reply with a single integer number and nothing else."
)


def parse_score(raw: str) -> float:
    match = re.search(r"-?\d+(?:[.,]\d+)?", raw)
    if not match:
        return 0.0
    value = float(match.group(0).replace(",", "."))
    return max(0.0, min(10.0, value))


class LLMReranker:
    def __init__(self, llm: LLM, top_n: int | None = None) -> None:
        self._llm = llm
        self._top_n = top_n

    def score(self, query: str, result: SearchResult) -> float:
        raw = self._llm.chat(
            [
                {"role": "system", "content": RERANK_PROMPT},
                {"role": "user", "content": f"Question: {query}\n\nPassage: {result.document.text}"},
            ]
        )
        return parse_score(raw)

    def rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        scored = [(self.score(query, result), result) for result in results]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        reranked = [result for _, result in scored]
        return reranked[: self._top_n] if self._top_n else reranked
