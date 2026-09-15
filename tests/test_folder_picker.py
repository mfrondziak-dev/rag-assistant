from types import SimpleNamespace

from rag.folder_picker import pick_folder


def _which(names):
    def which(name):
        return f"/usr/bin/{name}" if name in names else None

    return which


def _run_returning(stdout, returncode=0):
    def run(command, **kwargs):
        return SimpleNamespace(returncode=returncode, stdout=stdout)

    return run


def test_zenity_returns_selected_path():
    picked = pick_folder(
        which=_which({"zenity"}),
        run=_run_returning("/home/user/Documents\n"),
        tkinter_picker=lambda: None,
    )
    assert picked == "/home/user/Documents"


def test_cancel_returns_none():
    picked = pick_folder(
        which=_which({"zenity"}),
        run=_run_returning("", returncode=1),
        tkinter_picker=lambda: None,
    )
    assert picked is None


def test_kdialog_fallback():
    picked = pick_folder(
        which=_which({"kdialog"}),
        run=_run_returning("/tmp\n"),
        tkinter_picker=lambda: None,
    )
    assert picked == "/tmp"


def test_tkinter_fallback_when_no_dialog_tool():
    picked = pick_folder(
        which=_which(set()),
        run=_run_returning(""),
        tkinter_picker=lambda: "/home/user/notes",
    )
    assert picked == "/home/user/notes"


def test_error_running_dialog_returns_none():
    def run(command, **kwargs):
        raise OSError("boom")

    picked = pick_folder(
        which=_which({"zenity"}),
        run=run,
        tkinter_picker=lambda: None,
    )
    assert picked is None


def test_windows_powershell_picker():
    def run(command, **kwargs):
        assert command[0] == "powershell"
        return SimpleNamespace(returncode=0, stdout="C:\\Users\\me\\Documents\r\n")

    picked = pick_folder(
        which=_which(set()),
        run=run,
        tkinter_picker=lambda: None,
        is_windows=True,
    )
    assert picked == "C:\\Users\\me\\Documents"


def test_windows_cancel_falls_through_to_tkinter():
    picked = pick_folder(
        which=_which(set()),
        run=_run_returning("", returncode=1),
        tkinter_picker=lambda: "C:\\fallback",
        is_windows=True,
    )
    assert picked == "C:\\fallback"
