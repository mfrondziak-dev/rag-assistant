from rag.config import PROJECT_ROOT
from rag.opener import open_path, resolve_path


def test_resolve_path_relative_uses_project_root():
    assert resolve_path("data/raw/x.md") == PROJECT_ROOT / "data/raw/x.md"


def test_open_path_missing_file_returns_false(tmp_path):
    assert open_path(tmp_path / "nope.md", run=lambda *a, **k: None, platform="linux") is False


def test_open_path_linux_uses_xdg_open(tmp_path):
    document = tmp_path / "doc.md"
    document.write_text("x", encoding="utf-8")
    seen = {}

    def run(command, **kwargs):
        seen["command"] = command

    assert open_path(document, run=run, platform="linux") is True
    assert seen["command"][0] == "xdg-open"
    assert seen["command"][1] == str(document)


def test_open_path_macos_uses_open(tmp_path):
    document = tmp_path / "doc.md"
    document.write_text("x", encoding="utf-8")
    seen = {}

    def run(command, **kwargs):
        seen["command"] = command

    assert open_path(document, run=run, platform="darwin") is True
    assert seen["command"][0] == "open"


def test_open_path_handles_error(tmp_path):
    document = tmp_path / "doc.md"
    document.write_text("x", encoding="utf-8")

    def run(command, **kwargs):
        raise OSError("boom")

    assert open_path(document, run=run, platform="linux") is False
