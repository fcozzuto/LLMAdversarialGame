from __future__ import annotations

import ast
import difflib
import hashlib
from typing import Any


def normalize_code(code: str) -> str:
    lines: list[str] = []
    for line in code.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return " ".join(lines)


def code_similarity(left: str, right: str) -> float:
    return difflib.SequenceMatcher(None, normalize_code(left), normalize_code(right)).ratio()


def strategy_tags(code: str) -> list[str]:
    lowered = code.lower()
    tags: set[str] = set()
    if "opponent_position" in lowered or "opponent_" in lowered:
        tags.add("opponent_aware")
    if "scores" in lowered:
        tags.add("score_aware")
    if "sorted(" in lowered or ".sort(" in lowered:
        tags.add("global_sort")
    if "min(" in lowered and "resources" in lowered:
        tags.add("nearest_resource")
    if "queue" in lowered or "deque" in lowered or "heapq" in lowered:
        tags.add("graph_search")
    if "self_path" in lowered or "visited" in lowered or "memory" in lowered:
        tags.add("path_memory")
    if "y % 2" in lowered or "x % 2" in lowered:
        tags.add("sweep_pattern")
    if "return [0, 0]" in lowered:
        tags.add("stay_option")
    if not tags:
        tags.add("uncategorized")
    return sorted(tags)


def motif_counts(code: str) -> dict[str, int]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "ifs": 0,
            "loops": 0,
            "comprehensions": 0,
            "helper_functions": 0,
            "returns": 0,
        }
    counts = {
        "ifs": 0,
        "loops": 0,
        "comprehensions": 0,
        "helper_functions": 0,
        "returns": 0,
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            counts["ifs"] += 1
        elif isinstance(node, (ast.For, ast.While)):
            counts["loops"] += 1
        elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
            counts["comprehensions"] += 1
        elif isinstance(node, ast.FunctionDef) and node.name != "choose_move":
            counts["helper_functions"] += 1
        elif isinstance(node, ast.Return):
            counts["returns"] += 1
    return counts


def code_fingerprint(code: str) -> str:
    normalized = normalize_code(code)
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]


def fingerprint_record(code: str) -> dict[str, Any]:
    return {
        "fingerprint": code_fingerprint(code),
        "normalized_code": normalize_code(code),
        "strategy_tags": strategy_tags(code),
        "motif_counts": motif_counts(code),
    }
