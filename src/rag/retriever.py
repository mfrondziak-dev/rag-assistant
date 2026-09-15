from __future__ import annotations

import numpy as np

from .interfaces import Embedder
from .models import SearchResult
from .store import VectorStore, l2_normalize


class Retriever:
    def __init__(
        self,
        store: VectorStore,
        embedder: Embedder,
        top_k: int = 5,
        mmr_lambda: float = 0.5,
        fetch_k: int | None = None,
    ) -> None:
        self._store = store
        self._embedder = embedder
        self._top_k = top_k
        self._mmr_lambda = mmr_lambda
        self._fetch_k = fetch_k or max(top_k * 4, top_k)

    def retrieve(self, query: str) -> list[SearchResult]:
        if len(self._store) == 0:
            return []
        query_vector = self._embedder.embed([query])[0]
        return self.retrieve_by_vector(query_vector)

    def retrieve_by_vector(self, query_vector: np.ndarray) -> list[SearchResult]:
        if len(self._store) == 0:
            return []
        query = l2_normalize(np.asarray(query_vector, dtype=np.float32).reshape(-1))
        scores = self._store.matrix @ query
        pool_size = min(self._fetch_k, len(self._store))
        candidates = list(np.argsort(-scores)[:pool_size])
        if self._mmr_lambda >= 1.0 or len(candidates) <= self._top_k:
            selected = candidates[: self._top_k]
        else:
            selected = self._mmr(query, candidates, scores)
        return [
            SearchResult(document=self._store.documents[i], score=float(scores[i]))
            for i in selected
        ]

    def _mmr(self, query: np.ndarray, candidates: list[int], scores: np.ndarray) -> list[int]:
        selected: list[int] = []
        remaining = candidates[:]
        while remaining and len(selected) < self._top_k:
            best_index = None
            best_score = float("-inf")
            for index in remaining:
                relevance = float(scores[index])
                if selected:
                    similarities = self._store.matrix[selected] @ self._store.matrix[index]
                    redundancy = float(np.max(similarities))
                else:
                    redundancy = 0.0
                value = self._mmr_lambda * relevance - (1.0 - self._mmr_lambda) * redundancy
                if value > best_score:
                    best_score = value
                    best_index = index
            if best_index is None:
                break
            selected.append(best_index)
            remaining.remove(best_index)
        return selected
