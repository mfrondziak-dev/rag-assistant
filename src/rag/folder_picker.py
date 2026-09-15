from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _run_dialog(command: list[str], run) -> str | None:
    try:
        result = run(command, capture_output=True, text=True, timeout=600)
    except Exception:
        return None
    if getattr(result, "returncode", 1) != 0:
        return None
    path = (getattr(result, "stdout", "") or "").strip()
    return path or None


def _tkinter_picker() -> str | None:
    try:
        import tkinter
        from tkinter import filedialog

        root = tkinter.Tk()
        root.withdraw()
        selected = filedialog.askdirectory()
        root.destroy()
        return selected or None
    except Exception:
        return None


def pick_folder(
    which=shutil.which,
    run=subprocess.run,
    tkinter_picker=_tkinter_picker,
) -> str | None:
    """Open a native folder chooser on the local machine and return the path.

    Tries zenity, then kdialog, then tkinter. Returns None if cancelled or unavailable.
    """
    if which("zenity"):
        picked = _run_dialog(
            ["zenity", "--file-selection", "--directory", "--title=Choose a folder"], run
        )
        if picked:
            return picked

    if which("kdialog"):
        picked = _run_dialog(["kdialog", "--getexistingdirectory", str(Path.home())], run)
        if picked:
            return picked

    return tkinter_picker()
