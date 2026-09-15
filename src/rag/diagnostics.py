from __future__ import annotations

import shutil
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .simple import list_uploads


class Status(str, Enum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class Check:
    key: str
    status: Status
    detail: str = ""


def check_ollama_installed(which=shutil.which) -> Check:
    if which("ollama"):
        return Check("diag_ollama_installed", Status.OK)
    return Check("diag_ollama_installed", Status.FAIL)


def check_ollama_running(client) -> Check:
    try:
        running = client.health()
    except Exception:
        running = False
    return Check("diag_ollama_running", Status.OK if running else Status.FAIL)


def check_models(client, models: list[str]) -> Check:
    try:
        available = {name.split(":")[0] for name in client.list_models()}
    except Exception:
        available = set()
    missing = [model for model in models if model.split(":")[0] not in available]
    if missing:
        status = Status.FAIL if len(missing) == len(models) else Status.WARN
        return Check("diag_models", status, ", ".join(missing))
    return Check("diag_models", Status.OK)


def check_documents(uploads_dir: str | Path) -> Check:
    count = len(list_uploads(uploads_dir))
    if count:
        return Check("diag_documents", Status.OK, str(count))
    return Check("diag_documents", Status.WARN)


def check_index(index_dir: str | Path) -> Check:
    if (Path(index_dir) / "vectors.npy").exists():
        return Check("diag_index", Status.OK)
    return Check("diag_index", Status.WARN)


def run_diagnostics(settings, client) -> list[Check]:
    from .simple import UPLOADS_DIR

    return [
        check_ollama_installed(),
        check_ollama_running(client),
        check_models(client, [settings.embed_model, settings.chat_model]),
        check_documents(UPLOADS_DIR),
        check_index(settings.index_dir),
    ]


def try_start_ollama(
    client,
    wait_seconds: int = 20,
    which=shutil.which,
    popen=subprocess.Popen,
    sleep=time.sleep,
) -> bool:
    if client.health():
        return True
    if which("ollama") is None:
        return False
    popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    for _ in range(wait_seconds):
        if client.health():
            return True
        sleep(1)
    return False
