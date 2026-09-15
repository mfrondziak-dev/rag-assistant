from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .models import Document, SearchResult


def l2_normalize(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.ndim == 1:
        norm = np.linalg.norm(matrix)
        return matrix / norm if norm > 0 else matrix
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


class VectorStore:
    def __init__(self) -> None:
        self._matrix: np.ndarray | None = None
        self._documents: list[Document] = []

    def __len__(self) -> int:
        return len(self._documents)

    @property
    def documents(self) -> list[Document]:
        return self._documents

    @property
    def matrix(self) -> np.ndarray:
        if self._matrix is None:
            return np.zeros((0, 0), dtype=np.float32)
        return self._matrix

    @property
    def dim(self) -> int:
        return self.matrix.shape[1] if self._matrix is not None else 0

    def add(self, vectors: np.ndarray, documents: list[Document]) -> None:
        if len(vectors) != len(documents):
            raise ValueError("vectors and documents must have the same length")
        if len(vectors) == 0:
            return
        normalized = l2_normalize(vectors)
        if self._matrix is None:
            self._matrix = normalized
        else:
            if normalized.shape[1] != self._matrix.shape[1]:
                raise ValueError(
                    f"embedding dimension mismatch: {normalized.shape[1]} != {self._matrix.shape[1]}"
                )
            self._matrix = np.vstack([self._matrix, normalized])
        self._documents.extend(documents)

    def search(self, query_vector: np.ndarray, k: int = 5) -> list[SearchResult]:
        if self._matrix is None or len(self._documents) == 0:
            return []
        query = l2_normalize(np.asarray(query_vector, dtype=np.float32).reshape(-1))
        scores = self._matrix @ query
        k = min(k, len(self._documents))
        top = np.argsort(-scores)[:k]
        return [
            SearchResult(document=self._documents[i], score=float(scores[i]))
            for i in top
        ]

    def save(self, directory: str | Path) -> None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        matrix = self._matrix if self._matrix is not None else np.zeros((0, 0), dtype=np.float32)
        np.save(directory / "vectors.npy", matrix)
        with (directory / "documents.jsonl").open("w", encoding="utf-8") as handle:
            for document in self._documents:
                handle.write(json.dumps(asdict(document), ensure_ascii=False) + "\n")

    @classmethod
    def load(cls, directory: str | Path) -> VectorStore:
        directory = Path(directory)
        vectors_path = directory / "vectors.npy"
        documents_path = directory / "documents.jsonl"
        if not vectors_path.exists() or not documents_path.exists():
            raise FileNotFoundError(f"No index found in {directory}. Run `rag ingest` first.")
        store = cls()
        matrix = np.load(vectors_path)
        store._matrix = matrix if matrix.size else None
        with documents_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                payload = json.loads(line)
                store._documents.append(Document(**payload))
        return store
