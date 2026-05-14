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
    if "cluster_mode" in lowered or "cluster_count" in lowered:
        tags.add("decomposition")
    if "two_opt" in lowered:
        tags.add("two_opt")
    if "three_opt" in lowered:
        tags.add("three_opt")
    if "perturbation" in lowered or "double_bridge" in lowered:
        tags.add("perturbation")
    if "restart" in lowered:
        tags.add("restart_logic")
    if "candidate_limit" in lowered:
        tags.add("candidate_pruning")
    if "acceptance" in lowered:
        tags.add("acceptance_schedule")
    if "seed_mode" in lowered:
        tags.add("seed_selection")
    if "density_penalty" in lowered or "angle_penalty" in lowered or "lookahead_weight" in lowered:
        tags.add("scored_nearest_neighbor")
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
            "dict_literals": 0,
        }
    counts = {
        "ifs": 0,
        "loops": 0,
        "comprehensions": 0,
        "helper_functions": 0,
        "returns": 0,
        "dict_literals": 0,
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            counts["ifs"] += 1
        elif isinstance(node, (ast.For, ast.While)):
            counts["loops"] += 1
        elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
            counts["comprehensions"] += 1
        elif isinstance(node, ast.FunctionDef) and node.name != "build_heuristic":
            counts["helper_functions"] += 1
        elif isinstance(node, ast.Return):
            counts["returns"] += 1
        elif isinstance(node, ast.Dict):
            counts["dict_literals"] += 1
    return counts


def code_fingerprint(code: str) -> str:
    return hashlib.sha1(normalize_code(code).encode("utf-8")).hexdigest()[:16]


def complexity_score(code: str) -> float:
    motifs = motif_counts(code)
    line_count = sum(1 for line in code.splitlines() if line.strip())
    score = (
        (0.02 * line_count)
        + (0.15 * motifs["ifs"])
        + (0.15 * motifs["loops"])
        + (0.1 * motifs["comprehensions"])
        + (0.2 * motifs["helper_functions"])
    )
    return round(score, 4)


def fingerprint_record(code: str) -> dict[str, Any]:
    return {
        "fingerprint": code_fingerprint(code),
        "normalized_code": normalize_code(code),
        "strategy_tags": strategy_tags(code),
        "motif_counts": motif_counts(code),
        "complexity_score": complexity_score(code),
    }
