from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter
from typing import Any


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def run_solver(code: str, instance_payload: dict[str, Any], *, timeout_seconds: float) -> dict[str, Any]:
    started = perf_counter()
    try:
        process = subprocess.run(
            [sys.executable, "-m", "llm_cvrp_phase9.solver_worker"],
            input=json.dumps({"code": code, "instance": instance_payload}),
            capture_output=True,
            text=True,
            cwd=str(_project_root()),
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        elapsed_ms = round((perf_counter() - started) * 1000.0, 6)
        return {
            "ok": False,
            "runtime_ms": elapsed_ms,
            "error": f"solver worker timed out after {timeout_seconds:.1f} seconds",
            "routes": [],
        }
    elapsed_ms = round((perf_counter() - started) * 1000.0, 6)
    if process.returncode != 0:
        stderr = (process.stderr or "").strip()
        return {
            "ok": False,
            "runtime_ms": elapsed_ms,
            "error": stderr or f"worker exited with code {process.returncode}",
            "routes": [],
        }
    lines = [line.strip() for line in process.stdout.splitlines() if line.strip()]
    if not lines:
        return {
            "ok": False,
            "runtime_ms": elapsed_ms,
            "error": "worker produced no output",
            "routes": [],
        }
    try:
        payload = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "runtime_ms": elapsed_ms,
            "error": f"worker produced invalid JSON: {exc}",
            "routes": [],
        }
    return {
        "ok": bool(payload.get("ok", False)),
        "runtime_ms": elapsed_ms,
        "error": payload.get("error"),
        "routes": payload.get("routes", []),
    }
