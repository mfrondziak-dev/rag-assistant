from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

_WINDOWS_DIALOG = (
    "Add-Type -AssemblyName System.Windows.Forms; "
    "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
    "$f.Description = 'Choose a folder'; "
    "if ($f.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $f.SelectedPath }"
)


def _run_dialog(command: list[str], run) -> str | None:
    try:
        result = run(command, capture_output=True, text=True, timeout=600)
    except Exception:
        return None
    if getattr(result, "returncode", 1) != 0:
        return None
    path = (getattr(result, "stdout", "") or "").strip()
    return path or None


def _windows_picker(run) -> str | None:
    return _run_dialog(
        ["powershell", "-NoProfile", "-STA", "-Command", _WINDOWS_DIALOG],
        run,
    )


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
    is_windows=os.name == "nt",
) -> str | None:
    """Open a native folder chooser on the local machine and return the path.

    Tries zenity and kdialog (Linux), a PowerShell dialog (Windows), then tkinter.
    Returns None if cancelled or unavailable.
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

    if is_windows:
        picked = _windows_picker(run)
        if picked:
            return picked

    return tkinter_picker()
