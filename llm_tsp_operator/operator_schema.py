from __future__ import annotations

import copy
from typing import Any


SUPPORTED_OPERATOR_TYPES = (
    "candidate_ranker",
    "perturbation",
    "candidate_pruner",
    "acceptance",
    "restart_controller",
    "scaffold_selector",
)

SCAFFOLD_NAMES = (
    "nearest_neighbor_2opt",
    "cheapest_insertion_2opt",
    "random_restart_2opt",
    "sparse_three_opt",
    "clustered_local_search",
)

DEFAULT_OPERATOR_SPEC: dict[str, Any] = {
    "name": "delta_ranker",
    "description": "Favor strong immediate edge-swap gains while staying mildly trap-aware.",
    "operator_type": "candidate_ranker",
    "move_delta_weight": 1.0,
    "crossing_bonus": 0.35,
    "span_bonus": 0.08,
    "nn_rank_penalty": 0.12,
    "trap_bonus": 0.18,
    "cluster_bonus": 0.06,
    "long_edge_bonus": 0.08,
}


def default_operator_code() -> str:
    return """
def build_operator():
    return {
        "name": "delta_ranker",
        "description": "Favor strong immediate edge-swap gains while staying mildly trap-aware.",
        "operator_type": "candidate_ranker",
        "move_delta_weight": 1.0,
        "crossing_bonus": 0.35,
        "span_bonus": 0.08,
        "nn_rank_penalty": 0.12,
        "trap_bonus": 0.18,
        "cluster_bonus": 0.06,
        "long_edge_bonus": 0.08,
    }
""".strip()


def builtin_operator_code(name: str) -> str:
    normalized = name.lower()
    if normalized in {"delta_ranker", "default_operator"}:
        return default_operator_code()
    if normalized == "adaptive_pruner":
        return """
def build_operator():
    return {
        "name": "adaptive_pruner",
        "description": "Expand candidates on trap-like instances and prune more on structured layouts.",
        "operator_type": "candidate_pruner",
        "base_candidate_limit": 16,
        "size_sensitivity": 5,
        "trap_bonus": 6,
        "grid_bonus": -3,
        "cluster_bonus": 2,
        "stagnation_bonus": 4,
    }
""".strip()
    if normalized == "escape_controller":
        return """
def build_operator():
    return {
        "name": "escape_controller",
        "description": "Escalate perturbation strength after stagnation while keeping early restarts mild.",
        "operator_type": "perturbation",
        "primary_mode": "double_bridge",
        "secondary_mode": "segment_reversal",
        "stagnation_threshold": 2,
        "strength": 2,
        "attempts": 2,
        "escalation_strength": 1,
    }
""".strip()
    if normalized == "annealed_acceptor":
        return """
def build_operator():
    return {
        "name": "annealed_acceptor",
        "description": "Allow modest worse-move acceptance early, then cool quickly.",
        "operator_type": "acceptance",
        "mode": "annealed",
        "base_threshold": 0.002,
        "temperature": 0.01,
        "stagnation_bonus": 0.004,
        "late_search_cooling": 0.006,
    }
""".strip()
    if normalized == "restart_controller":
        return """
def build_operator():
    return {
        "name": "restart_controller",
        "description": "Increase restart count when stagnation persists, but keep the seed pool compact.",
        "operator_type": "restart_controller",
        "base_restart_count": 3,
        "max_restart_count": 7,
        "stagnation_trigger": 2,
        "seed_pool_size": 3,
        "restart_growth": 2,
        "use_perturbation_restarts": True,
    }
""".strip()
    if normalized == "scaffold_selector":
        return """
def build_operator():
    return {
        "name": "structure_selector",
        "description": "Route clustered and bottlenecked layouts to cluster-aware scaffolds while keeping random-like layouts simple.",
        "operator_type": "scaffold_selector",
        "preferred_random_like": "nearest_neighbor_2opt",
        "preferred_clustered": "clustered_local_search",
        "preferred_grid_like": "cheapest_insertion_2opt",
        "preferred_two_cluster_bottleneck": "clustered_local_search",
        "preferred_elongated": "random_restart_2opt",
        "preferred_nearest_neighbor_trap": "sparse_three_opt",
        "fallback": "nearest_neighbor_2opt",
    }
""".strip()
    return default_operator_code()


def canonicalize_operator_spec(raw: dict[str, Any] | None) -> dict[str, Any]:
    merged = copy.deepcopy(DEFAULT_OPERATOR_SPEC)
    if raw:
        merged.update(copy.deepcopy(raw))

    operator_type = str(merged.get("operator_type", "candidate_ranker"))
    if operator_type not in SUPPORTED_OPERATOR_TYPES:
        operator_type = "candidate_ranker"
    merged["operator_type"] = operator_type
    merged["name"] = str(merged.get("name") or "unnamed_operator")[:80]
    merged["description"] = str(merged.get("description") or "")[:220]

    if operator_type == "candidate_ranker":
        merged["move_delta_weight"] = _bounded_float(merged.get("move_delta_weight", 1.0), 0.25, 2.5)
        merged["crossing_bonus"] = _bounded_float(merged.get("crossing_bonus", 0.35), 0.0, 1.5)
        merged["span_bonus"] = _bounded_float(merged.get("span_bonus", 0.08), -0.5, 1.0)
        merged["nn_rank_penalty"] = _bounded_float(merged.get("nn_rank_penalty", 0.12), 0.0, 1.2)
        merged["trap_bonus"] = _bounded_float(merged.get("trap_bonus", 0.18), 0.0, 1.2)
        merged["cluster_bonus"] = _bounded_float(merged.get("cluster_bonus", 0.06), -0.5, 1.0)
        merged["long_edge_bonus"] = _bounded_float(merged.get("long_edge_bonus", 0.08), -0.5, 1.0)
    elif operator_type == "perturbation":
        merged["primary_mode"] = _enum(str(merged.get("primary_mode", "double_bridge")), {"double_bridge", "segment_reversal", "shuffle_window"}, "double_bridge")
        merged["secondary_mode"] = _enum(str(merged.get("secondary_mode", "segment_reversal")), {"double_bridge", "segment_reversal", "shuffle_window"}, "segment_reversal")
        merged["stagnation_threshold"] = _bounded_int(merged.get("stagnation_threshold", 2), 1, 6)
        merged["strength"] = _bounded_int(merged.get("strength", 2), 1, 4)
        merged["attempts"] = _bounded_int(merged.get("attempts", 2), 1, 4)
        merged["escalation_strength"] = _bounded_int(merged.get("escalation_strength", 1), 0, 3)
    elif operator_type == "candidate_pruner":
        merged["base_candidate_limit"] = _bounded_int(merged.get("base_candidate_limit", 16), 6, 32)
        merged["size_sensitivity"] = _bounded_int(merged.get("size_sensitivity", 5), -8, 8)
        merged["trap_bonus"] = _bounded_int(merged.get("trap_bonus", 6), -8, 8)
        merged["grid_bonus"] = _bounded_int(merged.get("grid_bonus", -3), -8, 8)
        merged["cluster_bonus"] = _bounded_int(merged.get("cluster_bonus", 2), -8, 8)
        merged["stagnation_bonus"] = _bounded_int(merged.get("stagnation_bonus", 4), -8, 8)
    elif operator_type == "acceptance":
        merged["mode"] = _enum(str(merged.get("mode", "threshold")), {"improving_only", "threshold", "annealed"}, "threshold")
        merged["base_threshold"] = _bounded_float(merged.get("base_threshold", 0.002), 0.0, 0.04)
        merged["temperature"] = _bounded_float(merged.get("temperature", 0.01), 0.0, 0.05)
        merged["stagnation_bonus"] = _bounded_float(merged.get("stagnation_bonus", 0.004), 0.0, 0.02)
        merged["late_search_cooling"] = _bounded_float(merged.get("late_search_cooling", 0.006), 0.0, 0.02)
        if merged["mode"] == "improving_only":
            merged["base_threshold"] = 0.0
            merged["temperature"] = 0.0
            merged["stagnation_bonus"] = 0.0
            merged["late_search_cooling"] = 0.0
    elif operator_type == "restart_controller":
        merged["base_restart_count"] = _bounded_int(merged.get("base_restart_count", 3), 1, 8)
        merged["max_restart_count"] = _bounded_int(merged.get("max_restart_count", 7), 1, 10)
        merged["stagnation_trigger"] = _bounded_int(merged.get("stagnation_trigger", 2), 1, 6)
        merged["seed_pool_size"] = _bounded_int(merged.get("seed_pool_size", 3), 1, 6)
        merged["restart_growth"] = _bounded_int(merged.get("restart_growth", 2), 0, 3)
        merged["use_perturbation_restarts"] = bool(merged.get("use_perturbation_restarts", True))
        merged["max_restart_count"] = max(merged["base_restart_count"], merged["max_restart_count"])
    elif operator_type == "scaffold_selector":
        merged["preferred_random_like"] = _enum(str(merged.get("preferred_random_like", "nearest_neighbor_2opt")), set(SCAFFOLD_NAMES), "nearest_neighbor_2opt")
        merged["preferred_clustered"] = _enum(str(merged.get("preferred_clustered", "clustered_local_search")), set(SCAFFOLD_NAMES), "clustered_local_search")
        merged["preferred_grid_like"] = _enum(str(merged.get("preferred_grid_like", "cheapest_insertion_2opt")), set(SCAFFOLD_NAMES), "cheapest_insertion_2opt")
        merged["preferred_two_cluster_bottleneck"] = _enum(str(merged.get("preferred_two_cluster_bottleneck", "clustered_local_search")), set(SCAFFOLD_NAMES), "clustered_local_search")
        merged["preferred_elongated"] = _enum(str(merged.get("preferred_elongated", "random_restart_2opt")), set(SCAFFOLD_NAMES), "random_restart_2opt")
        merged["preferred_nearest_neighbor_trap"] = _enum(str(merged.get("preferred_nearest_neighbor_trap", "sparse_three_opt")), set(SCAFFOLD_NAMES), "sparse_three_opt")
        merged["fallback"] = _enum(str(merged.get("fallback", "nearest_neighbor_2opt")), set(SCAFFOLD_NAMES), "nearest_neighbor_2opt")
    return merged


def operator_signature(spec: dict[str, Any]) -> str:
    operator_type = str(spec.get("operator_type", "candidate_ranker"))
    if operator_type == "candidate_ranker":
        return "candidate_ranker:" + ",".join(
            [
                _quantized("delta", spec.get("move_delta_weight", 0.0), step=0.25),
                _quantized("cross", spec.get("crossing_bonus", 0.0), step=0.25),
                _quantized("span", spec.get("span_bonus", 0.0), step=0.2),
                _quantized("trap", spec.get("trap_bonus", 0.0), step=0.2),
            ]
        )
    if operator_type == "perturbation":
        return ":".join(
            [
                "perturbation",
                str(spec.get("primary_mode", "double_bridge")),
                str(spec.get("secondary_mode", "segment_reversal")),
                str(int(spec.get("strength", 1))),
                str(int(spec.get("stagnation_threshold", 1))),
            ]
        )
    if operator_type == "candidate_pruner":
        return ":".join(
            [
                "candidate_pruner",
                str(int(spec.get("base_candidate_limit", 16))),
                str(int(spec.get("trap_bonus", 0))),
                str(int(spec.get("grid_bonus", 0))),
                str(int(spec.get("stagnation_bonus", 0))),
            ]
        )
    if operator_type == "acceptance":
        return ":".join(
            [
                "acceptance",
                str(spec.get("mode", "threshold")),
                _quantized("thr", spec.get("base_threshold", 0.0), step=0.002),
                _quantized("temp", spec.get("temperature", 0.0), step=0.005),
            ]
        )
    if operator_type == "restart_controller":
        return ":".join(
            [
                "restart_controller",
                str(int(spec.get("base_restart_count", 1))),
                str(int(spec.get("max_restart_count", 1))),
                str(int(spec.get("restart_growth", 0))),
            ]
        )
    return ":".join(
        [
            "scaffold_selector",
            str(spec.get("preferred_random_like", "nearest_neighbor_2opt")),
            str(spec.get("preferred_clustered", "clustered_local_search")),
            str(spec.get("preferred_nearest_neighbor_trap", "sparse_three_opt")),
        ]
    )


def operator_pseudocode(spec: dict[str, Any]) -> list[str]:
    operator_type = str(spec.get("operator_type", "candidate_ranker"))
    if operator_type == "candidate_ranker":
        return [
            "For each candidate move, compute a composite score from immediate delta, crossing removal, span, trap awareness, and local structure.",
            "Sort candidate moves by ascending composite score.",
            "Apply the first move that yields a genuine tour improvement.",
        ]
    if operator_type == "perturbation":
        return [
            "Track stagnation count during local search and restarts.",
            f"Use `{spec.get('primary_mode', 'double_bridge')}` by default and escalate toward `{spec.get('secondary_mode', 'segment_reversal')}` after the stagnation threshold.",
            "Increase perturbation strength deterministically when escape pressure rises.",
        ]
    if operator_type == "candidate_pruner":
        return [
            "Start from a base candidate-list size.",
            "Expand or shrink the list using instance descriptors such as size, trap score, grid-likeness, clustering, and current stagnation.",
            "Run the downstream local search only on the resulting pruned neighborhood.",
        ]
    if operator_type == "acceptance":
        return [
            f"Use `{spec.get('mode', 'threshold')}` acceptance when a restart solution is not immediately improving.",
            "Relax or tighten acceptance depending on stagnation and late-search cooling.",
            "Reject candidate restarts that exceed the configured worse-move budget.",
        ]
    if operator_type == "restart_controller":
        return [
            "Start from a conservative restart budget.",
            "Increase restart count only after the configured stagnation trigger.",
            "Keep perturbation restarts bounded by a deterministic maximum.",
        ]
    return [
        "Read instance descriptors to classify the layout family.",
        "Dispatch the instance to the preferred scaffold for that structure class.",
        "Fall back to a safe default scaffold when the structure is ambiguous.",
    ]


def novelty_classification(spec: dict[str, Any]) -> str:
    operator_type = str(spec.get("operator_type", "candidate_ranker"))
    if operator_type == "candidate_ranker":
        trap_bonus = float(spec.get("trap_bonus", 0.0))
        crossing_bonus = float(spec.get("crossing_bonus", 0.0))
        if trap_bonus >= 0.6 and crossing_bonus >= 0.6:
            return "trap_aware_ranker"
        if float(spec.get("span_bonus", 0.0)) >= 0.4:
            return "long_span_ranker"
        return "delta_weighted_ranker"
    if operator_type == "perturbation":
        if int(spec.get("escalation_strength", 0)) >= 2:
            return "stagnation_escalator"
        return "deterministic_perturbation_schedule"
    if operator_type == "candidate_pruner":
        if int(spec.get("trap_bonus", 0)) >= 4:
            return "trap_expanding_pruner"
        return "descriptor_adaptive_pruner"
    if operator_type == "acceptance":
        if str(spec.get("mode", "")) == "annealed":
            return "annealed_acceptance"
        if str(spec.get("mode", "")) == "threshold":
            return "threshold_acceptance"
        return "improving_only_acceptance"
    if operator_type == "restart_controller":
        return "adaptive_restart_controller"
    return "descriptor_based_scaffold_selector"


def _bounded_int(value: Any, lower: int, upper: int) -> int:
    try:
        numeric = int(round(float(value)))
    except Exception:
        numeric = lower
    return max(lower, min(upper, numeric))


def _bounded_float(value: Any, lower: float, upper: float) -> float:
    try:
        numeric = float(value)
    except Exception:
        numeric = lower
    return max(lower, min(upper, numeric))


def _enum(value: str, choices: set[str], fallback: str) -> str:
    return value if value in choices else fallback


def _quantized(name: str, value: Any, *, step: float) -> str:
    try:
        numeric = float(value)
    except Exception:
        numeric = 0.0
    return f"{name}={round(numeric / step) * step:.3f}"
