from types import SimpleNamespace

from rag.ocr import ocr_image, should_ocr


def test_ocr_enabled_respects_env(monkeypatch):
    from rag.ocr import enabled

    which = lambda _name: "/usr/bin/tesseract"
    monkeypatch.setenv("OCR", "1")
    assert enabled(which=which) is True
    monkeypatch.setenv("OCR", "0")
    assert enabled(which=which) is False


def test_ocr_disabled_without_tesseract(monkeypatch):
    from rag.ocr import enabled

    monkeypatch.setenv("OCR", "1")
    assert enabled(which=lambda _name: None) is False


def test_should_ocr_only_for_scanned_pages(monkeypatch):
    monkeypatch.setenv("OCR", "1")
    which = lambda _name: "/usr/bin/tesseract"
    assert should_ocr(5, "", which=which) is True
    assert should_ocr(1, "x" * 500, which=which) is False
    assert should_ocr(0, "", which=which) is False


def test_ocr_image_runs_tesseract_with_language(monkeypatch):
    monkeypatch.setenv("OCR_LANG", "pol+eng")
    seen = {}

    def run(command, **kwargs):
        seen["command"] = command
        return SimpleNamespace(returncode=0, stdout="hello\n")

    assert ocr_image("page.png", run=run) == "hello\n"
    assert seen["command"][0] == "tesseract"
    assert "pol+eng" in seen["command"]
    assert "stdout" in seen["command"]


def test_ocr_image_returns_empty_on_failure():
    def run(command, **kwargs):
        return SimpleNamespace(returncode=1, stdout="boom")

    assert ocr_image("page.png", run=run) == ""
