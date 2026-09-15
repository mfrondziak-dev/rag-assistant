from pathlib import Path

import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest  # noqa: E402

APP = Path(__file__).resolve().parents[1] / "app" / "simple_app.py"


def _run_app(**session_state):
    app = AppTest.from_file(str(APP), default_timeout=30)
    for key, value in session_state.items():
        app.session_state[key] = value
    app.run()
    return app


def test_simple_app_runs_without_exception():
    app = _run_app()
    assert not app.exception


def test_simple_app_runs_in_english():
    app = _run_app(lang="en")
    assert not app.exception


def test_simple_app_folder_mode_renders():
    app = _run_app()
    if not app.radio:
        pytest.skip("app is gated by the Ollama check in this environment")
    app.radio[0].set_value("Wskaż folder").run()
    assert not app.exception
