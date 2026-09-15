from rag.cli import main


def test_ask_rejects_empty_question(capsys):
    code = main(["ask", "   "])
    captured = capsys.readouterr()
    assert code == 2
    assert "empty" in captured.err.lower()
