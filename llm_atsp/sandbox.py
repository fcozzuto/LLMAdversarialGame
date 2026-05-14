from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
from typing import Any


@dataclass
class HeuristicMaterialization:
    issues: list[str]
    used_fallback: bool
    init_error: str | None
    executed_code: str
    heuristic_spec: dict[str, Any]


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _reader_thread(stream: Any, sink: queue.Queue[dict[str, Any]]) -> None:
    try:
        for line in iter(stream.readline, ""):
            stripped = line.strip()
            if not stripped:
                continue
            sink.put(json.loads(stripped))
    finally:
        try:
            stream.close()
        except Exception:
            pass


def materialize_heuristic(code: str) -> HeuristicMaterialization:
    response_queue: queue.Queue[dict[str, Any]] = queue.Queue()
    process = subprocess.Popen(
        [sys.executable, "-m", "llm_atsp.heuristic_worker"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(_project_root()),
        bufsize=1,
    )
    stdout_thread = threading.Thread(target=_reader_thread, args=(process.stdout, response_queue), daemon=True)
    stdout_thread.start()
    try:
        assert process.stdin is not None
        process.stdin.write(json.dumps({"type": "init", "code": code}) + "\n")
        process.stdin.flush()
        payload = response_queue.get(timeout=10.0)
    finally:
        try:
            process.wait(timeout=1.0)
        except Exception:
            process.kill()
            process.wait(timeout=2.0)
    return HeuristicMaterialization(
        issues=list(payload.get("issues", [])),
        used_fallback=bool(payload.get("used_fallback", False)),
        init_error=payload.get("init_error"),
        executed_code=str(payload.get("executed_code", "")),
        heuristic_spec=dict(payload.get("heuristic_spec", {})),
    )

