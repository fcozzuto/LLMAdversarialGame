from __future__ import annotations

import ast
import collections
import functools
import heapq
import json
import math
import sys
from typing import Any

from .llm import default_agent_code


SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "range": range,
    "reversed": reversed,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
}

DISALLOWED_CALLS = {
    "__import__",
    "compile",
    "delattr",
    "eval",
    "exec",
    "getattr",
    "globals",
    "help",
    "input",
    "locals",
    "open",
    "setattr",
    "vars",
}


def validate_code(code: str) -> list[str]:
    issues: list[str] = []
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [f"syntax_error:{exc.msg}"]

    has_entrypoint = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            issues.append("imports_not_allowed")
        elif isinstance(node, ast.Attribute) and str(node.attr).startswith("__"):
            issues.append("dunder_attribute_not_allowed")
        elif isinstance(node, ast.Name) and str(node.id).startswith("__"):
            issues.append("dunder_name_not_allowed")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in DISALLOWED_CALLS:
                issues.append(f"disallowed_call:{node.func.id}")
        elif isinstance(node, ast.FunctionDef) and node.name == "choose_move":
            has_entrypoint = True
    if not has_entrypoint:
        issues.append("missing_choose_move")
    return sorted(set(issues))


def parse_move(value: Any) -> tuple[int, int] | None:
    if isinstance(value, dict):
        dx = value.get("dx")
        dy = value.get("dy")
        if isinstance(dx, int) and isinstance(dy, int):
            return dx, dy
    if isinstance(value, (list, tuple)) and len(value) == 2:
        dx, dy = value
        if isinstance(dx, int) and isinstance(dy, int):
            return dx, dy
    return None


def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def main() -> None:
    init_line = sys.stdin.readline()
    if not init_line:
        return
    init_payload = json.loads(init_line)
    code = str(init_payload.get("code", ""))
    issues = validate_code(code)
    executed_code = default_agent_code() if issues else code
    namespace: dict[str, Any] = {
        "__builtins__": SAFE_BUILTINS,
        "collections": collections,
        "functools": functools,
        "heapq": heapq,
        "math": math,
    }
    init_error = None
    try:
        exec(executed_code, namespace, namespace)
        func = namespace["choose_move"]
    except Exception as exc:
        init_error = str(exc)
        executed_code = default_agent_code()
        namespace = {
            "__builtins__": SAFE_BUILTINS,
            "collections": collections,
            "functools": functools,
            "heapq": heapq,
            "math": math,
        }
        exec(executed_code, namespace, namespace)
        func = namespace["choose_move"]

    emit(
        {
            "type": "ready",
            "issues": issues,
            "used_fallback": bool(issues or init_error),
            "init_error": init_error,
            "executed_code": executed_code,
        }
    )

    for line in sys.stdin:
        if not line:
            break
        payload = json.loads(line)
        if payload["type"] == "close":
            break
        if payload["type"] != "step":
            emit({"type": "result", "move": [0, 0], "runtime_issue": "unknown_message"})
            continue
        try:
            move = parse_move(func(payload["observation"]))
            if move is None:
                emit({"type": "result", "move": [0, 0], "runtime_issue": "invalid_return"})
            else:
                emit({"type": "result", "move": [move[0], move[1]], "runtime_issue": None})
        except Exception as exc:
            emit({"type": "result", "move": [0, 0], "runtime_issue": f"runtime_error:{exc}"})


if __name__ == "__main__":
    main()
