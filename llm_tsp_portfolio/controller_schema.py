from __future__ import annotations

import copy
from typing import Any

from .portfolio_library import controller_supported_heuristics


DEFAULT_CONTROLLER_SPEC: dict[str, Any] = {
    "name": "clustered_switch_controller",
    "description": "Use cluster-aware construction on structured layouts and switch to restart-heavy search when improvement stalls.",
    "default_heuristic": "nearest_neighbor_multistart",
    "random_like_heuristic": "nearest_neighbor_multistart",
    "clustered_heuristic": "cluster_first_local_search",
    "grid_like_heuristic": "cheapest_insertion_two_opt",
    "two_cluster_bottleneck_heuristic": "edge_preserving_restart",
    "corridor_heuristic": "farthest_insertion_two_opt",
    "nearest_neighbor_trap_heuristic": "limited_three_opt",
    "stagnation_switch_heuristic": "annealed_multi_start",
    "stagnation_threshold": 3,
    "low_improvement_threshold": 0.08,
    "failed_perturbation_threshold": 2,
    "time_budget_trigger": 0.72,
    "candidate_limit_offset": 0,
    "restart_offset": 1,
    "temperature_scale": 1.0,
    "acceptance_bias": 0.001,
}


def default_controller_code() -> str:
    return """
def build_controller():
    return {
        "name": "clustered_switch_controller",
        "description": "Use cluster-aware construction on structured layouts and switch to restart-heavy search when improvement stalls.",
        "default_heuristic": "nearest_neighbor_multistart",
        "random_like_heuristic": "nearest_neighbor_multistart",
        "clustered_heuristic": "cluster_first_local_search",
        "grid_like_heuristic": "cheapest_insertion_two_opt",
        "two_cluster_bottleneck_heuristic": "edge_preserving_restart",
        "corridor_heuristic": "farthest_insertion_two_opt",
        "nearest_neighbor_trap_heuristic": "limited_three_opt",
        "stagnation_switch_heuristic": "annealed_multi_start",
        "stagnation_threshold": 3,
        "low_improvement_threshold": 0.08,
        "failed_perturbation_threshold": 2,
        "time_budget_trigger": 0.72,
        "candidate_limit_offset": 0,
        "restart_offset": 1,
        "temperature_scale": 1.0,
        "acceptance_bias": 0.001,
    }
""".strip()


def builtin_controller_code(name: str) -> str:
    normalized = name.lower()
    if normalized in {"portfolio_default", "static_selector"}:
        return default_controller_code()
    if normalized == "adaptive_controller":
        return """
def build_controller():
    return {
        "name": "adaptive_cluster_bottleneck_controller",
        "description": "Differentiate clustered, bottleneck, and corridor layouts and switch to annealed multi-start after stagnation.",
        "default_heuristic": "nearest_neighbor_multistart",
        "random_like_heuristic": "annealed_multi_start",
        "clustered_heuristic": "cluster_first_local_search",
        "grid_like_heuristic": "cheapest_insertion_two_opt",
        "two_cluster_bottleneck_heuristic": "edge_preserving_restart",
        "corridor_heuristic": "farthest_insertion_two_opt",
        "nearest_neighbor_trap_heuristic": "limited_three_opt",
        "stagnation_switch_heuristic": "edge_preserving_restart",
        "stagnation_threshold": 2,
        "low_improvement_threshold": 0.1,
        "failed_perturbation_threshold": 1,
        "time_budget_trigger": 0.78,
        "candidate_limit_offset": -1,
        "restart_offset": 2,
        "temperature_scale": 1.15,
        "acceptance_bias": 0.002,
    }
""".strip()
    if normalized == "replay_controller":
        return """
def build_controller():
    return {
        "name": "replay_aware_structure_controller",
        "description": "Keep structured layouts cluster-aware, protect bottleneck edges, and use restart-heavy search when transfer failures accumulate.",
        "default_heuristic": "nearest_neighbor_multistart",
        "random_like_heuristic": "nearest_neighbor_multistart",
        "clustered_heuristic": "cluster_first_local_search",
        "grid_like_heuristic": "candidate_pruned_two_opt",
        "two_cluster_bottleneck_heuristic": "edge_preserving_restart",
        "corridor_heuristic": "farthest_insertion_two_opt",
        "nearest_neighbor_trap_heuristic": "limited_three_opt",
        "stagnation_switch_heuristic": "annealed_multi_start",
        "stagnation_threshold": 2,
        "low_improvement_threshold": 0.09,
        "failed_perturbation_threshold": 1,
        "time_budget_trigger": 0.8,
        "candidate_limit_offset": -2,
        "restart_offset": 2,
        "temperature_scale": 1.1,
        "acceptance_bias": 0.0015,
    }
""".strip()
    return default_controller_code()


def canonicalize_controller_spec(raw: dict[str, Any] | None) -> dict[str, Any]:
    merged = copy.deepcopy(DEFAULT_CONTROLLER_SPEC)
    if raw:
        merged.update(copy.deepcopy(raw))
    supported = controller_supported_heuristics()
    for key in (
        "default_heuristic",
        "random_like_heuristic",
        "clustered_heuristic",
        "grid_like_heuristic",
        "two_cluster_bottleneck_heuristic",
        "corridor_heuristic",
        "nearest_neighbor_trap_heuristic",
        "stagnation_switch_heuristic",
    ):
        merged[key] = _enum(str(merged.get(key, DEFAULT_CONTROLLER_SPEC[key])), supported, DEFAULT_CONTROLLER_SPEC[key])
    merged["name"] = str(merged.get("name") or "unnamed_controller")[:80]
    merged["description"] = str(merged.get("description") or "")[:260]
    merged["stagnation_threshold"] = _bounded_int(merged.get("stagnation_threshold", 3), 1, 6)
    merged["low_improvement_threshold"] = _bounded_float(merged.get("low_improvement_threshold", 0.08), 0.0, 0.25)
    merged["failed_perturbation_threshold"] = _bounded_int(merged.get("failed_perturbation_threshold", 2), 0, 4)
    merged["time_budget_trigger"] = _bounded_float(merged.get("time_budget_trigger", 0.72), 0.2, 1.0)
    merged["candidate_limit_offset"] = _bounded_int(merged.get("candidate_limit_offset", 0), -6, 6)
    merged["restart_offset"] = _bounded_int(merged.get("restart_offset", 1), -3, 4)
    merged["temperature_scale"] = _bounded_float(merged.get("temperature_scale", 1.0), 0.5, 1.8)
    merged["acceptance_bias"] = _bounded_float(merged.get("acceptance_bias", 0.001), -0.01, 0.02)
    return merged


def controller_signature(spec: dict[str, Any]) -> str:
    return ":".join(
        [
            str(spec.get("random_like_heuristic", "")),
            str(spec.get("clustered_heuristic", "")),
            str(spec.get("two_cluster_bottleneck_heuristic", "")),
            str(spec.get("stagnation_switch_heuristic", "")),
            f"stag{int(spec.get('stagnation_threshold', 0))}",
            f"cand{int(spec.get('candidate_limit_offset', 0))}",
            f"restart{int(spec.get('restart_offset', 0))}",
        ]
    )


def controller_rule_summary(spec: dict[str, Any]) -> list[str]:
    return [
        f"Random-like instances use `{spec.get('random_like_heuristic')}`.",
        f"Clustered instances use `{spec.get('clustered_heuristic')}`.",
        f"Grid-like instances use `{spec.get('grid_like_heuristic')}`.",
        f"Two-cluster bottleneck instances use `{spec.get('two_cluster_bottleneck_heuristic')}`.",
        f"Corridor-like instances use `{spec.get('corridor_heuristic')}`.",
        f"Nearest-neighbor trap instances use `{spec.get('nearest_neighbor_trap_heuristic')}`.",
        (
            f"When stagnation >= {spec.get('stagnation_threshold')}, improvement <= {spec.get('low_improvement_threshold')}, "
            f"or failed perturbations >= {spec.get('failed_perturbation_threshold')}, switch to "
            f"`{spec.get('stagnation_switch_heuristic')}` if the time budget share is <= {spec.get('time_budget_trigger')}."
        ),
        (
            f"Tuning offsets: candidate limit {spec.get('candidate_limit_offset')}, restart offset {spec.get('restart_offset')}, "
            f"temperature scale {spec.get('temperature_scale')}, acceptance bias {spec.get('acceptance_bias')}."
        ),
    ]


def _bounded_float(value: Any, lower: float, upper: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = lower
    return max(lower, min(upper, parsed))


def _bounded_int(value: Any, lower: int, upper: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = lower
    return max(lower, min(upper, parsed))


def _enum(value: str, allowed: set[str], fallback: str) -> str:
    return value if value in allowed else fallback
