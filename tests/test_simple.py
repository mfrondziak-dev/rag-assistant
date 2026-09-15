import pytest

from rag.simple import clear_uploads, list_uploads, safe_filename, save_upload


def test_safe_filename_strips_directories():
    assert safe_filename("../../etc/passwd.md") == "passwd.md"
    assert safe_filename("a b!.txt") == "a b_.txt"


def test_safe_filename_never_returns_empty():
    assert safe_filename("!!!") == "_"


def test_save_upload_writes_inside_directory(tmp_path):
    path = save_upload(tmp_path, "notes.md", b"hello")
    assert path.read_bytes() == b"hello"
    assert path.parent == tmp_path


def test_save_upload_rejects_unsupported_type(tmp_path):
    with pytest.raises(ValueError):
        save_upload(tmp_path, "virus.exe", b"x")


def test_list_and_clear(tmp_path):
    save_upload(tmp_path, "a.md", b"a")
    save_upload(tmp_path, "b.txt", b"b")
    (tmp_path / "ignore.bin").write_bytes(b"x")

    assert [path.name for path in list_uploads(tmp_path)] == ["a.md", "b.txt"]

    clear_uploads(tmp_path)
    assert list_uploads(tmp_path) == []
