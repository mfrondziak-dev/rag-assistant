from rag.config import Settings, _get_bool, _get_float, _get_int


def test_get_int_reads_value(monkeypatch):
    monkeypatch.setenv("X_TEST_INT", "12")
    assert _get_int("X_TEST_INT", 7) == 12


def test_get_int_falls_back_on_bad_value(monkeypatch):
    monkeypatch.setenv("X_TEST_INT", "abc")
    assert _get_int("X_TEST_INT", 7) == 7


def test_get_int_default_when_unset(monkeypatch):
    monkeypatch.delenv("X_TEST_INT", raising=False)
    assert _get_int("X_TEST_INT", 7) == 7


def test_get_float_falls_back_on_bad_value(monkeypatch):
    monkeypatch.setenv("X_TEST_FLOAT", "not-a-number")
    assert _get_float("X_TEST_FLOAT", 1.5) == 1.5


def test_get_bool_parses_truthy_and_falsy(monkeypatch):
    monkeypatch.setenv("X_TEST_BOOL", "YES")
    assert _get_bool("X_TEST_BOOL") is True
    monkeypatch.setenv("X_TEST_BOOL", "0")
    assert _get_bool("X_TEST_BOOL") is False


def test_followups_reads_env_at_instantiation(monkeypatch):
    monkeypatch.setenv("FOLLOWUPS", "0")
    assert Settings().followups == 0
    monkeypatch.setenv("FOLLOWUPS", "5")
    assert Settings().followups == 5


def test_followups_bad_value_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("FOLLOWUPS", "abc")
    assert Settings().followups == 3
