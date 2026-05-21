from __future__ import annotations

import json
import sys
from typing import Any


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
    "pow": pow,
    "range": range,
    "reversed": reversed,
    "round": round,
    "set": set,
    "sorted": sorted,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
}


def _emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def main() -> None:
    payload = json.loads(sys.stdin.read())
    code = str(payload["code"])
    instance = payload["instance"]
    namespace: dict[str, Any] = {"__builtins__": SAFE_BUILTINS}
    try:
        exec(code, namespace, namespace)
        solver = namespace.get("solve_cvrp")
        if not callable(solver):
            raise TypeError("solve_cvrp was not defined")
        routes = solver(instance)
        _emit({"ok": True, "routes": routes})
    except Exception as exc:
        _emit({"ok": False, "error": f"{type(exc).__name__}: {exc}"})


if __name__ == "__main__":
    main()
