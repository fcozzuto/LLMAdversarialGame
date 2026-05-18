from __future__ import annotations

import json
import math
import sys
from typing import Any

from .code_validation import validate_code
from .operator_schema import canonicalize_operator_spec, default_operator_code


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
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
}


def _emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def _materialize(code: str) -> dict[str, Any]:
    namespace: dict[str, Any] = {
        "__builtins__": SAFE_BUILTINS,
        "math": math,
    }
    exec(code, namespace, namespace)
    build_fn = namespace["build_operator"]
    first = canonicalize_operator_spec(build_fn())
    second = canonicalize_operator_spec(build_fn())
    if first != second:
        raise ValueError("build_operator returned inconsistent specs across repeated calls")
    return first


def main() -> None:
    init_line = sys.stdin.readline()
    if not init_line:
        return
    init_payload = json.loads(init_line)
    code = str(init_payload.get("code", ""))
    issues = validate_code(code)
    executed_code = default_operator_code() if issues else code
    materialized: dict[str, Any] | None = None
    init_error = None
    try:
        materialized = _materialize(executed_code)
    except Exception as exc:
        init_error = str(exc)
        executed_code = default_operator_code()
        materialized = _materialize(executed_code)

    _emit(
        {
            "type": "ready",
            "issues": issues,
            "used_fallback": bool(issues or init_error),
            "init_error": init_error,
            "executed_code": executed_code,
            "operator_spec": materialized,
        }
    )


if __name__ == "__main__":
    main()
