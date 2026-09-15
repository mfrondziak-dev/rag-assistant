from __future__ import annotations

from pathlib import Path

from .config import Settings
from .factory import build_ollama
from .interfaces import Embedder
from .ollama_client import OllamaEmbedder
from .store import VectorStore
from .text import load_documents

DEFAULT_BATCH_SIZE = 32


def ingest(
    settings: Settings,
    raw_dir: str | Path = "data/raw",
    batch_size: int = DEFAULT_BATCH_SIZE,
    embedder: Embedder | None = None,
) -> VectorStore:
    settings.validate()
    documents = load_documents(raw_dir, settings.chunk_size, settings.chunk_overlap)
    if not documents:
        raise RuntimeError(f"No supported documents found in {raw_dir}")

    if embedder is None:
        client = build_ollama(settings)
        embedder = OllamaEmbedder(client, settings.embed_model)

    store = VectorStore()
    for start in range(0, len(documents), batch_size):
        batch = documents[start : start + batch_size]
        vectors = embedder.embed([doc.text for doc in batch])
        store.add(vectors, batch)

    store.save(settings.index_dir)
    return store
