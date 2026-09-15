from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    id: str
    text: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    document: Document
    score: float


@dataclass
class Citation:
    index: int
    source: str
    chunk_id: str
    score: float
    snippet: str


@dataclass
class RAGAnswer:
    question: str
    answer: str
    citations: list[Citation]
    contexts: list[SearchResult]
    used_context: bool
