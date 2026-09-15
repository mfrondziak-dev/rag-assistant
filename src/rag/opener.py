from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from .config import PROJECT_ROOT


def resolve_path(path: str | Path) -> Path:
    target = Path(path)
    if not target.is_absolute():
        target = PROJECT_ROOT / target
    return target


def open_path(path: str | Path, run=subprocess.Popen, platform=sys.platform) -> bool:
    """Open a file with the operating system's default application."""
    target = resolve_path(path)
    if not target.exists():
        return False
    try:
        if platform.startswith("win"):
            os.startfile(str(target))  # type: ignore[attr-defined]
            return True
        command = ["open", str(target)] if platform == "darwin" else ["xdg-open", str(target)]
        run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False
