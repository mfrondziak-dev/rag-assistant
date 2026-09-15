from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}

MIN_CHARS_PER_PAGE = 20


def _settings():
    from .config import Settings

    return Settings()


def tesseract_available(which=shutil.which) -> bool:
    return which("tesseract") is not None


def pdftoppm_available(which=shutil.which) -> bool:
    return which("pdftoppm") is not None


def enabled(which=shutil.which) -> bool:
    return _settings().ocr and tesseract_available(which)


def should_ocr(page_count: int, text: str, which=shutil.which) -> bool:
    if page_count <= 0 or not enabled(which):
        return False
    return len(text.strip()) < MIN_CHARS_PER_PAGE * page_count


def ocr_image(path: str | Path, lang: str | None = None, run=subprocess.run) -> str:
    settings = _settings()
    base = ["tesseract", str(path), "stdout", "-l", lang or settings.ocr_lang]
    for psm in (settings.ocr_psm, 3):
        try:
            result = run(base + ["--psm", str(psm)], capture_output=True, text=True, timeout=600)
        except Exception:
            continue
        if getattr(result, "returncode", 1) == 0:
            return getattr(result, "stdout", "") or ""
    return ""


def render_pdf_pages(path: str | Path, out_dir: str | Path, run=subprocess.run) -> list[Path]:
    directory = Path(out_dir)
    command = [
        "pdftoppm",
        "-r",
        str(_settings().ocr_dpi),
        "-png",
        str(path),
        str(directory / "page"),
    ]
    try:
        run(command, capture_output=True, text=True, timeout=1800)
    except Exception:
        return []
    return sorted(directory.glob("page*.png"))


def ocr_pdf(path: str | Path, lang: str | None = None, run=subprocess.run) -> str:
    if not pdftoppm_available():
        return ""
    with tempfile.TemporaryDirectory(prefix="rag-ocr-") as tmp:
        pages = render_pdf_pages(path, tmp, run=run)
        texts = [ocr_image(page, lang=lang, run=run) for page in pages]
    return "\n\n".join(texts)
