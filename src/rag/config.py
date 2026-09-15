from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _get_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if not raw:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    ollama_host: str = field(
        default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )
    embed_model: str = field(default_factory=lambda: os.getenv("EMBED_MODEL", "nomic-embed-text"))
    chat_model: str = field(default_factory=lambda: os.getenv("CHAT_MODEL", "llama3.1"))
    chunk_size: int = field(default_factory=lambda: _get_int("CHUNK_SIZE", 900))
    chunk_overlap: int = field(default_factory=lambda: _get_int("CHUNK_OVERLAP", 150))
    top_k: int = field(default_factory=lambda: _get_int("TOP_K", 5))
    mmr_lambda: float = field(default_factory=lambda: _get_float("MMR_LAMBDA", 0.5))
    rerank: bool = field(default_factory=lambda: _get_bool("RERANK", False))
    rerank_candidates: int = field(default_factory=lambda: _get_int("RERANK_CANDIDATES", 20))
    followups: int = field(default_factory=lambda: _get_int("FOLLOWUPS", 3))
    ocr: bool = field(default_factory=lambda: _get_bool("OCR", True))
    ocr_lang: str = field(default_factory=lambda: os.getenv("OCR_LANG", "eng"))
    ocr_dpi: int = field(default_factory=lambda: _get_int("OCR_DPI", 200))
    ocr_psm: int = field(default_factory=lambda: _get_int("OCR_PSM", 1))
    index_dir: Path = field(
        default_factory=lambda: PROJECT_ROOT / os.getenv("INDEX_DIR", "data/index")
    )
    request_timeout: float = field(default_factory=lambda: _get_float("REQUEST_TIMEOUT", 120.0))

    def validate(self) -> None:
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
        if not 0.0 <= self.mmr_lambda <= 1.0:
            raise ValueError("MMR_LAMBDA must be within [0, 1]")
        if self.top_k < 1:
            raise ValueError("TOP_K must be >= 1")
        if self.rerank_candidates < self.top_k:
            raise ValueError("RERANK_CANDIDATES must be >= TOP_K")
