from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import Settings
from .factory import build_pipeline
from .ollama_client import OllamaError
from .pipeline import RagPipeline
from .store import VectorStore


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class CitationModel(BaseModel):
    index: int
    source: str
    chunk_id: str
    score: float
    snippet: str


class AskResponse(BaseModel):
    question: str
    answer: str
    used_context: bool
    citations: list[CitationModel]


class SearchHit(BaseModel):
    chunk_id: str
    source: str
    score: float
    text: str


class SearchResponse(BaseModel):
    question: str
    results: list[SearchHit]


class HealthResponse(BaseModel):
    status: str
    index_size: int
    embed_model: str
    chat_model: str


@lru_cache(maxsize=4)
def _pipeline_for(index_dir: str, top_k: int, mmr_lambda: float, rerank: bool) -> RagPipeline:
    settings = Settings()
    settings.index_dir = Path(index_dir)
    settings.top_k = top_k
    settings.mmr_lambda = mmr_lambda
    settings.rerank = rerank
    store = VectorStore.load(settings.index_dir)
    return build_pipeline(settings, store)


def get_pipeline() -> RagPipeline:
    settings = Settings()
    try:
        return _pipeline_for(
            str(settings.index_dir), settings.top_k, settings.mmr_lambda, settings.rerank
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


app = FastAPI(title="Local RAG Assistant API", version="0.2.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = Settings()
    try:
        size = len(VectorStore.load(settings.index_dir))
        status = "ok"
    except FileNotFoundError:
        size = 0
        status = "no_index"
    return HealthResponse(
        status=status,
        index_size=size,
        embed_model=settings.embed_model,
        chat_model=settings.chat_model,
    )


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, pipeline: RagPipeline = Depends(get_pipeline)) -> AskResponse:
    try:
        result = pipeline.answer(request.question, top_k=request.top_k)
    except OllamaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return AskResponse(
        question=result.question,
        answer=result.answer,
        used_context=result.used_context,
        citations=[CitationModel(**citation.__dict__) for citation in result.citations],
    )


@app.post("/search", response_model=SearchResponse)
def search(request: AskRequest, pipeline: RagPipeline = Depends(get_pipeline)) -> SearchResponse:
    results = pipeline.retriever.retrieve(request.question)
    if request.top_k:
        results = results[: request.top_k]
    return SearchResponse(
        question=request.question,
        results=[
            SearchHit(
                chunk_id=result.document.id,
                source=result.document.source,
                score=result.score,
                text=result.document.text,
            )
            for result in results
        ],
    )
