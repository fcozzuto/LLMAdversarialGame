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
class AgentRuntime:
    process: subprocess.Popen[str]
    response_queue: queue.Queue[dict[str, Any]]
    stderr_queue: queue.Queue[str]
    issues: list[str]
    used_fallback: bool
    init_error: str | None
    executed_code: str
    is_alive: bool = True


def _reader_thread(stream: Any, sink: queue.Queue[Any], *, parse_json: bool) -> None:
    try:
        for line in iter(stream.readline, ""):
            stripped = line.strip()
            if not stripped:
                continue
            if parse_json:
                try:
                    sink.put(json.loads(stripped))
                except Exception:
                    sink.put({"type": "protocol_error", "raw": stripped})
            else:
                sink.put(stripped)
    finally:
        try:
            stream.close()
        except Exception:
            pass


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def launch_agent(code: str, _unused_context: Any = None) -> AgentRuntime:
    response_queue: queue.Queue[dict[str, Any]] = queue.Queue()
    stderr_queue: queue.Queue[str] = queue.Queue()
    process = subprocess.Popen(
        [sys.executable, "-m", "llm_grid_battle.agent_worker"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(_project_root()),
        bufsize=1,
    )

    stdout_thread = threading.Thread(
        target=_reader_thread,
        args=(process.stdout, response_queue),
        kwargs={"parse_json": True},
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=_reader_thread,
        args=(process.stderr, stderr_queue),
        kwargs={"parse_json": False},
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()

    try:
        assert process.stdin is not None
        process.stdin.write(json.dumps({"type": "init", "code": code}) + "\n")
        process.stdin.flush()
        ready = response_queue.get(timeout=10.0)
    except Exception as exc:
        process.kill()
        process.wait(timeout=2.0)
        return AgentRuntime(
            process=process,
            response_queue=response_queue,
            stderr_queue=stderr_queue,
            issues=["worker_start_failure"],
            used_fallback=True,
            init_error=str(exc),
            executed_code="",
            is_alive=False,
        )

    return AgentRuntime(
        process=process,
        response_queue=response_queue,
        stderr_queue=stderr_queue,
        issues=ready.get("issues", []),
        used_fallback=bool(ready.get("used_fallback")),
        init_error=ready.get("init_error"),
        executed_code=ready.get("executed_code", ""),
    )


def request_move(runtime: AgentRuntime, observation: dict[str, Any]) -> None:
    if not runtime.is_alive:
        return
    try:
        assert runtime.process.stdin is not None
        runtime.process.stdin.write(json.dumps({"type": "step", "observation": observation}) + "\n")
        runtime.process.stdin.flush()
    except Exception:
        runtime.is_alive = False


def collect_move(runtime: AgentRuntime, timeout_seconds: float) -> tuple[tuple[int, int], str | None]:
    if not runtime.is_alive:
        return (0, 0), "agent_dead"
    try:
        result = runtime.response_queue.get(timeout=timeout_seconds)
    except queue.Empty:
        runtime.process.kill()
        runtime.process.wait(timeout=2.0)
        runtime.is_alive = False
        return (0, 0), "timeout"

    if result.get("type") != "result":
        return (0, 0), "protocol_error"
    move = result.get("move") or [0, 0]
    return (int(move[0]), int(move[1])), result.get("runtime_issue")


def close_agent(runtime: AgentRuntime) -> None:
    if runtime.is_alive:
        try:
            assert runtime.process.stdin is not None
            runtime.process.stdin.write(json.dumps({"type": "close"}) + "\n")
            runtime.process.stdin.flush()
        except Exception:
            pass
    try:
        runtime.process.wait(timeout=1.0)
    except Exception:
        runtime.process.kill()
        runtime.process.wait(timeout=2.0)

