from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class Embedder(Protocol):
    def embed(self, texts: list[str]) -> np.ndarray:
        ...


@runtime_checkable
class LLM(Protocol):
    def chat(self, messages: list[dict[str, str]], **options: object) -> str:
        ...
