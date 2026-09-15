from __future__ import annotations

import re
from pathlib import Path

from .config import PROJECT_ROOT
from .text import SUPPORTED_SUFFIXES

UPLOADS_DIR = PROJECT_ROOT / "data" / "uploads"
SIMPLE_INDEX_DIR = PROJECT_ROOT / "data" / "index-simple"

_UNSAFE = re.compile(r"[^\w.\- ]+", flags=re.UNICODE)


def safe_filename(filename: str) -> str:
    name = Path(filename).name
    cleaned = _UNSAFE.sub("_", name).strip()
    return cleaned or "document"


def save_upload(uploads_dir: str | Path, filename: str, data: bytes) -> Path:
    directory = Path(uploads_dir)
    directory.mkdir(parents=True, exist_ok=True)
    name = safe_filename(filename)
    if Path(name).suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported file type: {name}")
    path = directory / name
    path.write_bytes(data)
    return path


def list_uploads(uploads_dir: str | Path) -> list[Path]:
    directory = Path(uploads_dir)
    if not directory.exists():
        return []
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )


def clear_uploads(uploads_dir: str | Path) -> None:
    directory = Path(uploads_dir)
    if not directory.exists():
        return
    for path in directory.rglob("*"):
        if path.is_file():
            path.unlink()
