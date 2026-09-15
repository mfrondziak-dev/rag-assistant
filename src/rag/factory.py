from __future__ import annotations

from .config import Settings
from .ollama_client import OllamaClient, OllamaEmbedder, OllamaLLM
from .pipeline import RagPipeline
from .retriever import Retriever
from .store import VectorStore


def build_ollama(settings: Settings) -> OllamaClient:
    return OllamaClient(host=settings.ollama_host, timeout=settings.request_timeout)


def build_pipeline(settings: Settings, store: VectorStore) -> RagPipeline:
    settings.validate()
    client = build_ollama(settings)
    embedder = OllamaEmbedder(client, settings.embed_model)
    retriever = Retriever(
        store=store,
        embedder=embedder,
        top_k=settings.top_k,
        mmr_lambda=settings.mmr_lambda,
    )
    llm = OllamaLLM(client, settings.chat_model)
    return RagPipeline(retriever=retriever, llm=llm)
