from __future__ import annotations

import ast
import collections
import functools
import heapq
import json
import math
import sys
from typing import Any

from .code_validation import validate_code
from .llm import default_agent_code


SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "Exception": Exception,
    "filter": filter,
    "float": float,
    "int": int,
    "isinstance": isinstance,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "next": next,
    "pow": pow,
    "range": range,
    "reversed": reversed,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "TypeError": TypeError,
    "tuple": tuple,
    "ValueError": ValueError,
    "zip": zip,
}

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
