from __future__ import annotations

from pathlib import Path
from typing import Callable

from .config import Settings
from .factory import build_ollama
from .interfaces import Embedder
from .ollama_client import OllamaEmbedder
from .store import VectorStore
from .text import load_documents

DEFAULT_BATCH_SIZE = 32

ProgressCallback = Callable[[str, int, int], None]


def ingest(
    settings: Settings,
    raw_dir: str | Path = "data/raw",
    batch_size: int = DEFAULT_BATCH_SIZE,
    embedder: Embedder | None = None,
    progress: ProgressCallback | None = None,
) -> VectorStore:
    settings.validate()

    def on_file(done: int, total: int) -> None:
        if progress:
            progress("reading", done, total)

    documents = load_documents(
        raw_dir,
        settings.chunk_size,
        settings.chunk_overlap,
        on_progress=on_file,
    )
    if not documents:
        raise RuntimeError(f"No supported documents found in {raw_dir}")

    if embedder is None:
        client = build_ollama(settings)
        embedder = OllamaEmbedder(client, settings.embed_model)

    total = len(documents)
    store = VectorStore()
    for start in range(0, total, batch_size):
        batch = documents[start : start + batch_size]
        vectors = embedder.embed([doc.text for doc in batch])
        store.add(vectors, batch)
        if progress:
            progress("embedding", min(start + batch_size, total), total)

    store.save(settings.index_dir)
    return store
