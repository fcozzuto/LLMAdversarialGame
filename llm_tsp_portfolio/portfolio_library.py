from __future__ import annotations

from dataclasses import dataclass
import copy
import math
import random
from typing import Any

from llm_tsp.benchmark import TSPInstance
from llm_tsp.instance_features import descriptor_payload, descriptor_vector, ensure_instance_descriptors
from llm_tsp_operator.scaffold_engine import SCAFFOLD_LIBRARY, aggregate_descriptor, solve_with_recipe


def _recipe(base_name: str, **overrides: Any) -> dict[str, Any]:
    base = copy.deepcopy(SCAFFOLD_LIBRARY[base_name])
    base.update(overrides)
    return base


FROZEN_HEURISTICS: dict[str, dict[str, Any]] = {
    "nearest_neighbor_multistart": {
        "description": "Multi-start nearest-neighbor construction with 2-opt and aggressive random restarts.",
        "components": ["nearest_neighbor", "2_opt", "random_restart", "multi_start_local_search"],
        "recipe": _recipe(
            "random_restart_2opt",
            construction_mode="nearest_neighbor",
            restart_count=6,
            seed_pool_size=5,
            two_opt_passes=3,
            perturbation_mode="double_bridge",
            acceptance_mode="improving_only",
            base_threshold=0.0,
        ),
    },
    "cheapest_insertion_two_opt": {
        "description": "Cheapest-insertion construction followed by compact 2-opt refinement.",
        "components": ["cheapest_insertion", "2_opt"],
        "recipe": _recipe(
            "cheapest_insertion_2opt",
            two_opt_passes=3,
            two_opt_candidate_limit=18,
        ),
    },
    "farthest_insertion_two_opt": {
        "description": "Farthest-insertion construction followed by 2-opt clean-up.",
        "components": ["farthest_insertion", "2_opt"],
        "recipe": _recipe(
            "farthest_insertion_2opt",
            two_opt_passes=3,
            two_opt_candidate_limit=18,
        ),
    },
    "candidate_pruned_two_opt": {
        "description": "Nearest-neighbor construction with tight candidate-list pruning and 2-opt.",
        "components": ["nearest_neighbor", "candidate_list_pruning", "2_opt"],
        "recipe": _recipe(
            "nearest_neighbor_2opt",
            candidate_limit=10,
            two_opt_candidate_limit=12,
            lookahead_limit=2,
            restart_count=2,
            seed_pool_size=2,
        ),
    },
    "limited_three_opt": {
        "description": "Simple sparse 3-opt schedule on top of a nearest-neighbor backbone.",
        "components": ["nearest_neighbor", "2_opt", "limited_3_opt"],
        "recipe": _recipe(
            "sparse_three_opt",
            three_opt_samples=5,
            two_opt_passes=2,
        ),
    },
    "cluster_first_local_search": {
        "description": "Cluster-first route construction with cluster-aware local search and bounded restarts.",
        "components": ["cluster_first_route_construction", "2_opt", "limited_3_opt", "candidate_list_pruning"],
        "recipe": _recipe(
            "clustered_local_search",
            cluster_mode="x_sweep",
            cluster_count=4,
            candidate_limit=16,
            restart_count=3,
        ),
    },
    "edge_preserving_restart": {
        "description": "Restart-heavy local search with edge-preserving perturbations for bottleneck-style layouts.",
        "components": ["nearest_neighbor", "2_opt", "edge_preserving_perturbation", "random_restart"],
        "recipe": _recipe(
            "random_restart_2opt",
            perturbation_mode="edge_preserving_shuffle",
            perturbation_strength=2,
            perturbation_attempts=2,
            restart_count=5,
            seed_pool_size=4,
            acceptance_mode="threshold",
            base_threshold=0.002,
        ),
    },
    "annealed_multi_start": {
        "description": "Multi-start local search with simple simulated-annealing style acceptance.",
        "components": ["nearest_neighbor", "2_opt", "double_bridge_perturbation", "simulated_annealing_acceptance", "multi_start_local_search"],
        "recipe": _recipe(
            "random_restart_2opt",
            perturbation_mode="double_bridge",
            acceptance_mode="annealed",
            temperature=0.012,
            base_threshold=0.003,
            restart_count=5,
            seed_pool_size=4,
        ),
    },
}


PORTFOLIO_COMPONENT_LIBRARY = [
    "nearest_neighbor",
    "cheapest_insertion",
    "farthest_insertion",
    "2_opt",
    "limited_3_opt",
    "double_bridge_perturbation",
    "random_restart",
    "candidate_list_pruning",
    "cluster_first_route_construction",
    "edge_preserving_perturbation",
    "simulated_annealing_acceptance",
    "multi_start_local_search",
]


def heuristic_names() -> list[str]:
    return list(FROZEN_HEURISTICS.keys())


def heuristic_catalog() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "description": spec["description"],
            "components": list(spec["components"]),
        }
        for name, spec in FROZEN_HEURISTICS.items()
    ]


def controller_supported_heuristics() -> set[str]:
    return set(FROZEN_HEURISTICS.keys())


def apply_controller_adjustments(recipe: dict[str, Any], controller_spec: dict[str, Any]) -> dict[str, Any]:
    tuned = copy.deepcopy(recipe)
    tuned["candidate_limit"] = max(6, min(30, int(tuned.get("candidate_limit", 12)) + int(controller_spec.get("candidate_limit_offset", 0))))
    tuned["two_opt_candidate_limit"] = max(
        8,
        min(28, int(tuned.get("two_opt_candidate_limit", tuned["candidate_limit"] + 4)) + int(controller_spec.get("candidate_limit_offset", 0))),
    )
    tuned["restart_count"] = max(1, min(8, int(tuned.get("restart_count", 1)) + int(controller_spec.get("restart_offset", 0))))
    tuned["seed_pool_size"] = max(1, min(6, int(tuned.get("seed_pool_size", 1)) + max(0, int(controller_spec.get("restart_offset", 0)))))
    tuned["base_threshold"] = round(
        max(0.0, min(0.03, (float(tuned.get("base_threshold", 0.0)) + float(controller_spec.get("acceptance_bias", 0.0))))),
        6,
    )
    tuned["temperature"] = round(
        max(0.0, min(0.05, float(tuned.get("temperature", 0.0)) * float(controller_spec.get("temperature_scale", 1.0)))),
        6,
    )
    return tuned


def choose_controller_heuristic(instance: TSPInstance, controller_spec: dict[str, Any]) -> str:
    descriptors = descriptor_payload(instance)
    if float(descriptors.get("nearest_neighbor_trap_score", 0.0)) >= 0.16:
        key = "nearest_neighbor_trap_heuristic"
    elif float(descriptors.get("bottleneck_score", 0.0)) >= 0.42 or str(descriptors.get("structure_class", "")) == "two_cluster_bottleneck":
        key = "two_cluster_bottleneck_heuristic"
    elif float(descriptors.get("corridor_score", 0.0)) >= 0.45 or str(descriptors.get("structure_class", "")) == "corridor_like":
        key = "corridor_heuristic"
    else:
        structure = str(descriptors.get("structure_class", "random_like"))
        key = {
            "clustered": "clustered_heuristic",
            "grid_like": "grid_like_heuristic",
            "random_like": "random_like_heuristic",
        }.get(structure, "default_heuristic")
    choice = str(controller_spec.get(key) or controller_spec.get("default_heuristic", "nearest_neighbor_multistart"))
    return choice if choice in FROZEN_HEURISTICS else "nearest_neighbor_multistart"


def build_search_state(result: dict[str, Any], *, budget_ms: float) -> dict[str, float]:
    trace = result.get("trace", {})
    construction_cost = max(1.0, float(trace.get("construction_cost", result.get("cost", 1))))
    final_cost = float(result.get("cost", construction_cost))
    accepted_swaps = max(
        0.0,
        float(trace.get("two_opt_gain", 0.0)) / max(1.0, construction_cost * 0.01),
    )
    failed_perturbations = max(
        0.0,
        float(trace.get("perturbation_attempts", 0.0)) - float(trace.get("perturbation_accepts", 0.0)),
    )
    return {
        "stagnation_length": max(0.0, float(trace.get("restart_count", 1)) - float(trace.get("perturbation_accepts", 0.0))),
        "recent_improvement_rate": max(0.0, (construction_cost - final_cost) / construction_cost),
        "current_tour_length": final_cost,
        "accepted_swaps": accepted_swaps,
        "time_budget_used": float(trace.get("runtime_ms", 0.0)) / max(1.0, budget_ms),
        "edge_length_skew": float(trace.get("edge_length_cv", 0.0)),
        "failed_perturbation_count": failed_perturbations,
    }


def estimated_budget_ms(instance: TSPInstance) -> float:
    n = max(8, int(instance.dimension))
    return max(25.0, 0.6 * n * math.log2(n + 1.0))


def run_fixed_heuristic(instance: TSPInstance, heuristic_name: str, *, seed: int) -> dict[str, Any]:
    ensure_instance_descriptors(instance)
    spec = FROZEN_HEURISTICS[heuristic_name]
    result = solve_with_recipe(
        instance,
        scaffold_name=heuristic_name,
        recipe=copy.deepcopy(spec["recipe"]),
        seed=seed,
    )
    result["selected_heuristic"] = heuristic_name
    result["controller_trace"] = {
        "initial_heuristic": heuristic_name,
        "followup_heuristic": None,
        "switched": False,
    }
    return result


def run_static_controller(instance: TSPInstance, controller_spec: dict[str, Any], *, seed: int) -> dict[str, Any]:
    ensure_instance_descriptors(instance)
    heuristic_name = choose_controller_heuristic(instance, controller_spec)
    recipe = apply_controller_adjustments(FROZEN_HEURISTICS[heuristic_name]["recipe"], controller_spec)
    result = solve_with_recipe(
        instance,
        scaffold_name=heuristic_name,
        recipe=recipe,
        seed=seed,
    )
    result["controller_trace"] = {
        "initial_heuristic": heuristic_name,
        "followup_heuristic": None,
        "switched": False,
        "online_state_used": False,
    }
    result["selected_heuristic"] = heuristic_name
    return result


def run_controller(
    instance: TSPInstance,
    controller_spec: dict[str, Any],
    *,
    seed: int,
    allow_online_state: bool = True,
) -> dict[str, Any]:
    if not allow_online_state:
        return run_static_controller(instance, controller_spec, seed=seed)
    ensure_instance_descriptors(instance)
    initial_name = choose_controller_heuristic(instance, controller_spec)
    base_recipe = apply_controller_adjustments(FROZEN_HEURISTICS[initial_name]["recipe"], controller_spec)
    base_result = solve_with_recipe(
        instance,
        scaffold_name=initial_name,
        recipe=base_recipe,
        seed=seed,
    )
    budget_ms = estimated_budget_ms(instance)
    search_state = build_search_state(base_result, budget_ms=budget_ms)

    switch_trigger = (
        search_state["stagnation_length"] >= float(controller_spec.get("stagnation_threshold", 3))
        or search_state["recent_improvement_rate"] <= float(controller_spec.get("low_improvement_threshold", 0.08))
        or search_state["failed_perturbation_count"] >= float(controller_spec.get("failed_perturbation_threshold", 2))
    )
    switch_allowed = search_state["time_budget_used"] <= float(controller_spec.get("time_budget_trigger", 0.7))
    followup_name = str(controller_spec.get("stagnation_switch_heuristic", initial_name))
    if followup_name not in FROZEN_HEURISTICS:
        followup_name = initial_name

    final_result = base_result
    switched = False
    if switch_trigger and switch_allowed and followup_name != initial_name:
        switched = True
        followup_recipe = apply_controller_adjustments(FROZEN_HEURISTICS[followup_name]["recipe"], controller_spec)
        followup_result = solve_with_recipe(
            instance,
            scaffold_name=followup_name,
            recipe=followup_recipe,
            seed=seed + 97,
            stagnation_state={
                "stagnation_count": int(search_state["stagnation_length"]),
            },
        )
        if int(followup_result["cost"]) <= int(base_result["cost"]):
            final_result = followup_result
        final_result["controller_trace"] = {
            "initial_heuristic": initial_name,
            "followup_heuristic": followup_name,
            "switched": switched,
            "online_state_used": True,
            "search_state": {key: round(value, 6) for key, value in search_state.items()},
        }
    else:
        final_result["controller_trace"] = {
            "initial_heuristic": initial_name,
            "followup_heuristic": None,
            "switched": False,
            "online_state_used": True,
            "search_state": {key: round(value, 6) for key, value in search_state.items()},
        }
    final_result["selected_heuristic"] = final_result["controller_trace"]["followup_heuristic"] or initial_name
    return final_result


@dataclass
class KnnPortfolioSelector:
    training_rows: list[dict[str, Any]]
    heuristic_names: list[str]
    neighbor_count: int

    def select(self, instance: TSPInstance) -> str:
        target = descriptor_vector(instance)
        if not self.training_rows:
            return self.heuristic_names[0]
        ranked = sorted(
            self.training_rows,
            key=lambda row: _vector_distance(target, row["vector"]),
        )[: max(1, self.neighbor_count)]
        scores: dict[str, float] = {}
        for heuristic_name in self.heuristic_names:
            weighted = 0.0
            weight_total = 0.0
            for row in ranked:
                distance = _vector_distance(target, row["vector"])
                weight = 1.0 / max(1e-6, distance + 1e-4)
                weighted += weight * float(row["gap_by_heuristic"][heuristic_name])
                weight_total += weight
            scores[heuristic_name] = weighted / max(1e-9, weight_total)
        return min(scores, key=scores.get)


def fit_knn_selector(
    *,
    training_instances: list[TSPInstance],
    heuristic_names_list: list[str],
    evaluation_table: dict[str, dict[str, dict[str, Any]]],
    neighbor_count: int,
) -> KnnPortfolioSelector:
    rows: list[dict[str, Any]] = []
    for instance in training_instances:
        rows.append(
            {
                "instance_name": instance.name,
                "vector": descriptor_vector(instance),
                "gap_by_heuristic": {
                    heuristic_name: float(evaluation_table[instance.name][heuristic_name]["optimality_gap"])
                    for heuristic_name in heuristic_names_list
                },
            }
        )
    return KnnPortfolioSelector(training_rows=rows, heuristic_names=heuristic_names_list, neighbor_count=neighbor_count)


def random_portfolio_choice(heuristic_names_list: list[str], *, seed: int) -> str:
    rng = random.Random(seed)
    return heuristic_names_list[rng.randrange(len(heuristic_names_list))]


def portfolio_descriptor(results: list[dict[str, Any]]) -> dict[str, float]:
    return aggregate_descriptor(results)


def _vector_distance(left: dict[str, float], right: dict[str, float]) -> float:
    if not left:
        return 0.0
    squared = 0.0
    for key, value in left.items():
        squared += (float(value) - float(right.get(key, 0.0))) ** 2
    return math.sqrt(squared / max(1, len(left)))
