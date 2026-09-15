from rag.diagnostics import (
    Status,
    check_documents,
    check_index,
    check_models,
    check_ollama_installed,
    try_start_ollama,
)


class FakeClient:
    def __init__(self, health=True, models=None):
        self._health = health
        self._models = models or []

    def health(self):
        return self._health

    def list_models(self):
        return self._models


def test_ollama_installed():
    assert check_ollama_installed(which=lambda _: "/usr/bin/ollama").status is Status.OK
    assert check_ollama_installed(which=lambda _: None).status is Status.FAIL


def test_ollama_running():
    from rag.diagnostics import check_ollama_running

    assert check_ollama_running(FakeClient(health=True)).status is Status.OK
    assert check_ollama_running(FakeClient(health=False)).status is Status.FAIL


def test_models_all_present():
    client = FakeClient(models=["nomic-embed-text:latest", "llama3.1:latest"])
    assert check_models(client, ["nomic-embed-text", "llama3.1"]).status is Status.OK


def test_models_report_missing():
    client = FakeClient(models=["nomic-embed-text:latest"])
    check = check_models(client, ["nomic-embed-text", "llama3.1"])
    assert check.status is Status.WARN
    assert "llama3.1" in check.detail


def test_documents_check(tmp_path):
    assert check_documents(tmp_path).status is Status.WARN
    (tmp_path / "a.md").write_text("hello", encoding="utf-8")
    assert check_documents(tmp_path).status is Status.OK


def test_index_check(tmp_path):
    assert check_index(tmp_path).status is Status.WARN
    (tmp_path / "vectors.npy").write_bytes(b"x")
    assert check_index(tmp_path).status is Status.OK


def test_try_start_ollama_without_binary():
    assert try_start_ollama(FakeClient(health=False), wait_seconds=0, which=lambda _: None) is False


def test_try_start_ollama_already_running():
    assert try_start_ollama(FakeClient(health=True), wait_seconds=0, which=lambda _: None) is True
