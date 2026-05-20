from __future__ import annotations

from dataclasses import dataclass
import math
import statistics
import time
from typing import Any

from llm_tsp.benchmark import TSPInstance, build_distance_matrix
from llm_tsp.instance_features import descriptor_payload, ensure_instance_descriptors

from .operator_schema import SCAFFOLD_NAMES, canonicalize_operator_spec


SCAFFOLD_LIBRARY: dict[str, dict[str, Any]] = {
    "nearest_neighbor_2opt": {
        "construction_mode": "nearest_neighbor",
        "seed_mode": "farthest_from_centroid",
        "candidate_limit": 14,
        "lookahead_limit": 3,
        "cluster_mode": "none",
        "cluster_count": 1,
        "restart_count": 1,
        "seed_pool_size": 1,
        "use_perturbation_restarts": False,
        "perturbation_mode": "double_bridge",
        "perturbation_strength": 1,
        "perturbation_attempts": 1,
        "acceptance_mode": "improving_only",
        "base_threshold": 0.0,
        "temperature": 0.0,
        "two_opt_passes": 3,
        "two_opt_candidate_limit": 18,
        "use_three_opt": False,
        "three_opt_samples": 0,
        "or_opt_span": 2,
    },
    "cheapest_insertion_2opt": {
        "construction_mode": "cheapest_insertion",
        "seed_mode": "nearest_centroid",
        "candidate_limit": 18,
        "lookahead_limit": 2,
        "cluster_mode": "none",
        "cluster_count": 1,
        "restart_count": 1,
        "seed_pool_size": 1,
        "use_perturbation_restarts": False,
        "perturbation_mode": "segment_reversal",
        "perturbation_strength": 1,
        "perturbation_attempts": 1,
        "acceptance_mode": "improving_only",
        "base_threshold": 0.0,
        "temperature": 0.0,
        "two_opt_passes": 2,
        "two_opt_candidate_limit": 16,
        "use_three_opt": False,
        "three_opt_samples": 0,
        "or_opt_span": 1,
    },
    "random_restart_2opt": {
        "construction_mode": "nearest_neighbor",
        "seed_mode": "highest_y",
        "candidate_limit": 12,
        "lookahead_limit": 3,
        "cluster_mode": "none",
        "cluster_count": 1,
        "restart_count": 5,
        "seed_pool_size": 4,
        "use_perturbation_restarts": True,
        "perturbation_mode": "double_bridge",
        "perturbation_strength": 2,
        "perturbation_attempts": 2,
        "acceptance_mode": "threshold",
        "base_threshold": 0.004,
        "temperature": 0.0,
        "two_opt_passes": 3,
        "two_opt_candidate_limit": 16,
        "use_three_opt": False,
        "three_opt_samples": 0,
        "or_opt_span": 2,
    },
    "sparse_three_opt": {
        "construction_mode": "nearest_neighbor",
        "seed_mode": "lowest_x",
        "candidate_limit": 10,
        "lookahead_limit": 2,
        "cluster_mode": "none",
        "cluster_count": 1,
        "restart_count": 2,
        "seed_pool_size": 2,
        "use_perturbation_restarts": False,
        "perturbation_mode": "segment_reversal",
        "perturbation_strength": 1,
        "perturbation_attempts": 1,
        "acceptance_mode": "improving_only",
        "base_threshold": 0.0,
        "temperature": 0.0,
        "two_opt_passes": 2,
        "two_opt_candidate_limit": 12,
        "use_three_opt": True,
        "three_opt_samples": 4,
        "or_opt_span": 1,
    },
    "clustered_local_search": {
        "construction_mode": "clustered_nearest",
        "seed_mode": "farthest_from_centroid",
        "candidate_limit": 14,
        "lookahead_limit": 4,
        "cluster_mode": "x_sweep",
        "cluster_count": 4,
        "restart_count": 3,
        "seed_pool_size": 3,
        "use_perturbation_restarts": True,
        "perturbation_mode": "shuffle_window",
        "perturbation_strength": 2,
        "perturbation_attempts": 2,
        "acceptance_mode": "threshold",
        "base_threshold": 0.003,
        "temperature": 0.0,
        "two_opt_passes": 4,
        "two_opt_candidate_limit": 18,
        "use_three_opt": True,
        "three_opt_samples": 4,
        "or_opt_span": 2,
    },
    "farthest_insertion_2opt": {
        "construction_mode": "farthest_insertion",
        "seed_mode": "farthest_from_centroid",
        "candidate_limit": 18,
        "lookahead_limit": 2,
        "cluster_mode": "none",
        "cluster_count": 1,
        "restart_count": 1,
        "seed_pool_size": 1,
        "use_perturbation_restarts": False,
        "perturbation_mode": "segment_reversal",
        "perturbation_strength": 1,
        "perturbation_attempts": 1,
        "acceptance_mode": "improving_only",
        "base_threshold": 0.0,
        "temperature": 0.0,
        "two_opt_passes": 3,
        "two_opt_candidate_limit": 18,
        "use_three_opt": False,
        "three_opt_samples": 0,
        "or_opt_span": 1,
    },
}


@dataclass
class EvalCounter:
    distance_evaluations: int = 0


@dataclass
class OperatorTrace:
    construction_cost: int
    final_cost: int
    two_opt_gain: int
    three_opt_gain: int
    restart_gain: int
    crossings_before: int
    crossings_after: int
    candidate_limit: int
    cluster_count: int
    perturbation_attempts: int
    perturbation_accepts: int
    mean_edge_length: float
    edge_length_cv: float
    runtime_ms: float
    distance_evaluations: int
    restart_count: int
    scaffold_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "construction_cost": int(self.construction_cost),
            "final_cost": int(self.final_cost),
            "two_opt_gain": int(self.two_opt_gain),
            "three_opt_gain": int(self.three_opt_gain),
            "restart_gain": int(self.restart_gain),
            "crossings_before": int(self.crossings_before),
            "crossings_after": int(self.crossings_after),
            "candidate_limit": int(self.candidate_limit),
            "cluster_count": int(self.cluster_count),
            "perturbation_attempts": int(self.perturbation_attempts),
            "perturbation_accepts": int(self.perturbation_accepts),
            "mean_edge_length": round(self.mean_edge_length, 4),
            "edge_length_cv": round(self.edge_length_cv, 4),
            "runtime_ms": round(self.runtime_ms, 4),
            "distance_evaluations": int(self.distance_evaluations),
            "restart_count": int(self.restart_count),
            "scaffold_name": self.scaffold_name,
        }


def solve_with_scaffold(
    instance: TSPInstance,
    scaffold_name: str,
    operator_spec: dict[str, Any] | None = None,
    *,
    seed: int = 0,
    stagnation_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if scaffold_name not in SCAFFOLD_LIBRARY:
        raise ValueError(f"Unsupported scaffold: {scaffold_name}")
    return solve_with_recipe(
        instance=instance,
        scaffold_name=scaffold_name,
        recipe=dict(SCAFFOLD_LIBRARY[scaffold_name]),
        operator_spec=operator_spec,
        seed=seed,
        stagnation_state=stagnation_state,
    )


def solve_with_recipe(
    instance: TSPInstance,
    *,
    scaffold_name: str,
    recipe: dict[str, Any],
    operator_spec: dict[str, Any] | None = None,
    seed: int = 0,
    stagnation_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ensure_instance_descriptors(instance)
    descriptors = descriptor_payload(instance)
    scaffold = dict(recipe)
    operator = canonicalize_operator_spec(operator_spec) if operator_spec else None
    stagnation_state = dict(stagnation_state or {})
    counter = EvalCounter()
    matrix = build_distance_matrix(instance)
    nearest = _nearest_candidates(matrix, limit=40)
    clusters = _cluster_labels(instance, scaffold["cluster_mode"], scaffold["cluster_count"])
    seed_nodes = _seed_candidates(instance, scaffold["seed_mode"])
    candidate_limit = _candidate_limit(instance, scaffold, operator, stagnation_state)
    restart_plan = _restart_plan(scaffold, operator, stagnation_state)

    start_time = time.perf_counter()
    best_tour: list[int] | None = None
    best_cost: int | None = None
    best_construction_cost = 0
    best_crossings_before = 0
    total_two_opt_gain = 0
    total_three_opt_gain = 0
    best_restart_gain = 0
    perturbation_attempts = 0
    perturbation_accepts = 0
    current_tour: list[int] | None = None

    for restart_index in range(restart_plan["restart_count"]):
        if restart_index == 0 or not restart_plan["use_perturbation_restarts"] or current_tour is None:
            seed_node = seed_nodes[restart_index % min(len(seed_nodes), restart_plan["seed_pool_size"])]
            candidate_tour = _construct_tour(
                instance=instance,
                matrix=matrix,
                nearest=nearest,
                clusters=clusters,
                scaffold=scaffold,
                counter=counter,
                candidate_limit=candidate_limit,
                seed_node=seed_node,
            )
        else:
            perturbation = _perturbation_plan(scaffold, operator, stagnation_state)
            candidate_tour = _perturb_tour(
                list(current_tour),
                mode=perturbation["mode"],
                strength=perturbation["strength"],
                seed=seed + restart_index,
            )
            perturbation_attempts += int(perturbation["attempts"])
        construction_cost = _tour_cost(matrix, candidate_tour, counter)
        crossings_before = _count_crossings(instance, candidate_tour)
        improved_tour, two_opt_gain, three_opt_gain = _local_search(
            instance=instance,
            matrix=matrix,
            nearest=nearest,
            clusters=clusters,
            tour=candidate_tour,
            scaffold=scaffold,
            operator=operator,
            descriptors=descriptors,
            counter=counter,
            candidate_limit=candidate_limit,
            stagnation_state=stagnation_state,
        )
        improved_cost = _tour_cost(matrix, improved_tour, counter)
        if best_cost is None:
            best_restart_gain = max(0, construction_cost - improved_cost)
        else:
            best_restart_gain = max(best_restart_gain, max(0, best_cost - improved_cost))

        if best_tour is None or _should_accept_restart(
            candidate_cost=improved_cost,
            incumbent_cost=best_cost,
            scaffold=scaffold,
            operator=operator,
            stagnation_state=stagnation_state,
            restart_index=restart_index,
        ):
            if best_cost is not None and improved_cost > best_cost:
                perturbation_accepts += 1
            best_tour = improved_tour
            best_cost = improved_cost
            best_construction_cost = construction_cost
            best_crossings_before = crossings_before
            total_two_opt_gain = two_opt_gain
            total_three_opt_gain = three_opt_gain
            current_tour = improved_tour

    if best_tour is None or best_cost is None:
        raise RuntimeError("Operator scaffold failed to produce a tour.")

    runtime_ms = (time.perf_counter() - start_time) * 1000.0
    edge_lengths = _edge_lengths(matrix, best_tour, counter)
    mean_edge_length = sum(edge_lengths) / max(1, len(edge_lengths))
    variance = sum((item - mean_edge_length) ** 2 for item in edge_lengths) / max(1, len(edge_lengths))
    trace = OperatorTrace(
        construction_cost=best_construction_cost,
        final_cost=best_cost,
        two_opt_gain=total_two_opt_gain,
        three_opt_gain=total_three_opt_gain,
        restart_gain=max(0, best_construction_cost - best_cost),
        crossings_before=best_crossings_before,
        crossings_after=_count_crossings(instance, best_tour),
        candidate_limit=candidate_limit,
        cluster_count=scaffold["cluster_count"] if scaffold["cluster_mode"] != "none" else 1,
        perturbation_attempts=perturbation_attempts,
        perturbation_accepts=perturbation_accepts,
        mean_edge_length=mean_edge_length,
        edge_length_cv=(math.sqrt(variance) / mean_edge_length) if mean_edge_length > 0 else 0.0,
        runtime_ms=runtime_ms,
        distance_evaluations=counter.distance_evaluations,
        restart_count=restart_plan["restart_count"],
        scaffold_name=scaffold_name,
    )
    gap = ((best_cost - instance.best_known_cost) / instance.best_known_cost) if instance.best_known_cost else 0.0
    return {
        "instance": instance.to_dict(),
        "tour": list(best_tour),
        "cost": int(best_cost),
        "best_known_cost": int(instance.best_known_cost),
        "optimality_gap": round(gap, 6),
        "trace": trace.to_dict(),
        "scaffold_name": scaffold_name,
        "operator_type": operator.get("operator_type") if operator else None,
    }


def solve_with_portfolio(
    instance: TSPInstance,
    operator_spec: dict[str, Any],
    *,
    seed: int = 0,
    candidate_scaffolds: list[str] | None = None,
    stagnation_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    operator = canonicalize_operator_spec(operator_spec)
    descriptors = descriptor_payload(instance)
    candidate_scaffolds = list(candidate_scaffolds or SCAFFOLD_NAMES)
    scaffold_name = _select_scaffold(operator, descriptors, candidate_scaffolds)
    return solve_with_scaffold(
        instance,
        scaffold_name,
        operator if operator.get("operator_type") != "scaffold_selector" else None,
        seed=seed,
        stagnation_state=stagnation_state,
    )


def aggregate_descriptor(results: list[dict[str, Any]]) -> dict[str, float]:
    if not results:
        return {
            "mean_gap_ratio": 0.0,
            "construction_gain_ratio": 0.0,
            "two_opt_gain_ratio": 0.0,
            "three_opt_gain_ratio": 0.0,
            "restart_gain_ratio": 0.0,
            "crossing_reduction_ratio": 0.0,
            "candidate_pruning_ratio": 0.0,
            "cluster_usage_ratio": 0.0,
            "perturbation_accept_ratio": 0.0,
            "tour_length_cv": 0.0,
            "runtime_ratio": 0.0,
            "distance_eval_ratio": 0.0,
        }
    mean_gap = sum(float(item["optimality_gap"]) for item in results) / len(results)
    construction_gain = sum(
        max(0.0, (float(item["trace"]["construction_cost"]) - float(item["cost"])) / max(1.0, float(item["trace"]["construction_cost"])))
        for item in results
    ) / len(results)
    two_opt_gain = sum(
        max(0.0, float(item["trace"]["two_opt_gain"]) / max(1.0, float(item["trace"]["construction_cost"])))
        for item in results
    ) / len(results)
    three_opt_gain = sum(
        max(0.0, float(item["trace"]["three_opt_gain"]) / max(1.0, float(item["trace"]["construction_cost"])))
        for item in results
    ) / len(results)
    restart_gain = sum(
        max(0.0, float(item["trace"]["restart_gain"]) / max(1.0, float(item["trace"]["construction_cost"])))
        for item in results
    ) / len(results)
    crossing_reduction = sum(
        max(0.0, float(item["trace"]["crossings_before"] - item["trace"]["crossings_after"]) / max(1.0, float(item["trace"]["crossings_before"] or 1.0)))
        for item in results
    ) / len(results)
    candidate_pruning = sum(
        float(item["trace"]["candidate_limit"]) / max(1.0, float(item["instance"]["dimension"] - 1))
        for item in results
    ) / len(results)
    cluster_usage = sum(
        0.0 if int(item["trace"]["cluster_count"]) <= 1 else min(1.0, int(item["trace"]["cluster_count"]) / 6.0)
        for item in results
    ) / len(results)
    perturbation_accept = sum(
        float(item["trace"]["perturbation_accepts"]) / max(1.0, float(item["trace"]["perturbation_attempts"] or 1.0))
        for item in results
    ) / len(results)
    tour_cv = sum(float(item["trace"]["edge_length_cv"]) for item in results) / len(results)
    runtime_ratio = sum(float(item["trace"]["runtime_ms"]) / max(1.0, float(item["best_known_cost"])) for item in results) / len(results)
    distance_eval_ratio = sum(float(item["trace"]["distance_evaluations"]) / max(1.0, float(item["instance"]["dimension"] ** 2)) for item in results) / len(results)
    return {
        "mean_gap_ratio": round(mean_gap, 6),
        "construction_gain_ratio": round(construction_gain, 6),
        "two_opt_gain_ratio": round(two_opt_gain, 6),
        "three_opt_gain_ratio": round(three_opt_gain, 6),
        "restart_gain_ratio": round(restart_gain, 6),
        "crossing_reduction_ratio": round(crossing_reduction, 6),
        "candidate_pruning_ratio": round(candidate_pruning, 6),
        "cluster_usage_ratio": round(cluster_usage, 6),
        "perturbation_accept_ratio": round(perturbation_accept, 6),
        "tour_length_cv": round(tour_cv, 6),
        "runtime_ratio": round(runtime_ratio, 6),
        "distance_eval_ratio": round(distance_eval_ratio, 6),
    }


def _select_scaffold(operator_spec: dict[str, Any], descriptors: dict[str, Any], candidate_scaffolds: list[str]) -> str:
    if operator_spec.get("operator_type") != "scaffold_selector":
        return candidate_scaffolds[0]
    structure = str(descriptors.get("structure_class", "random_like"))
    if structure == "clustered":
        choice = str(operator_spec.get("preferred_clustered", operator_spec.get("fallback", candidate_scaffolds[0])))
    elif structure == "grid_like":
        choice = str(operator_spec.get("preferred_grid_like", operator_spec.get("fallback", candidate_scaffolds[0])))
    elif structure == "two_cluster_bottleneck":
        choice = str(operator_spec.get("preferred_two_cluster_bottleneck", operator_spec.get("fallback", candidate_scaffolds[0])))
    elif float(descriptors.get("aspect_ratio", 1.0)) >= 1.7:
        choice = str(operator_spec.get("preferred_elongated", operator_spec.get("fallback", candidate_scaffolds[0])))
    elif float(descriptors.get("nearest_neighbor_trap_score", 0.0)) >= 0.14:
        choice = str(operator_spec.get("preferred_nearest_neighbor_trap", operator_spec.get("fallback", candidate_scaffolds[0])))
    else:
        choice = str(operator_spec.get("preferred_random_like", operator_spec.get("fallback", candidate_scaffolds[0])))
    return choice if choice in candidate_scaffolds else candidate_scaffolds[0]


def _candidate_limit(
    instance: TSPInstance,
    scaffold: dict[str, Any],
    operator_spec: dict[str, Any] | None,
    stagnation_state: dict[str, Any],
) -> int:
    base_limit = int(scaffold["candidate_limit"])
    if not operator_spec or operator_spec.get("operator_type") != "candidate_pruner":
        return base_limit
    descriptors = descriptor_payload(instance)
    adjusted = int(operator_spec["base_candidate_limit"])
    adjusted += round(float(descriptors.get("city_count_norm", 0.0)) * int(operator_spec["size_sensitivity"]))
    adjusted += round(float(descriptors.get("nearest_neighbor_trap_score", 0.0)) * int(operator_spec["trap_bonus"]))
    adjusted += round(float(descriptors.get("grid_likeness", 0.0)) * int(operator_spec["grid_bonus"]))
    adjusted += round(float(descriptors.get("clusteredness_score", 0.0)) * int(operator_spec["cluster_bonus"]))
    adjusted += min(3, int(stagnation_state.get("stagnation_count", 0))) * int(operator_spec["stagnation_bonus"])
    return max(6, min(36, adjusted))


def _restart_plan(scaffold: dict[str, Any], operator_spec: dict[str, Any] | None, stagnation_state: dict[str, Any]) -> dict[str, Any]:
    if not operator_spec or operator_spec.get("operator_type") != "restart_controller":
        return {
            "restart_count": int(scaffold["restart_count"]),
            "seed_pool_size": int(scaffold["seed_pool_size"]),
            "use_perturbation_restarts": bool(scaffold["use_perturbation_restarts"]),
        }
    stagnation = int(stagnation_state.get("stagnation_count", 0))
    growth = int(operator_spec["restart_growth"]) if stagnation >= int(operator_spec["stagnation_trigger"]) else 0
    restart_count = min(int(operator_spec["max_restart_count"]), int(operator_spec["base_restart_count"]) + growth)
    return {
        "restart_count": restart_count,
        "seed_pool_size": int(operator_spec["seed_pool_size"]),
        "use_perturbation_restarts": bool(operator_spec["use_perturbation_restarts"]),
    }


def _perturbation_plan(scaffold: dict[str, Any], operator_spec: dict[str, Any] | None, stagnation_state: dict[str, Any]) -> dict[str, Any]:
    if not operator_spec or operator_spec.get("operator_type") != "perturbation":
        return {
            "mode": str(scaffold["perturbation_mode"]),
            "strength": int(scaffold["perturbation_strength"]),
            "attempts": int(scaffold["perturbation_attempts"]),
        }
    stagnation = int(stagnation_state.get("stagnation_count", 0))
    mode = str(operator_spec["primary_mode"])
    strength = int(operator_spec["strength"])
    if stagnation >= int(operator_spec["stagnation_threshold"]):
        mode = str(operator_spec["secondary_mode"])
        strength = min(4, strength + int(operator_spec["escalation_strength"]))
    return {
        "mode": mode,
        "strength": strength,
        "attempts": int(operator_spec["attempts"]),
    }


def _construct_tour(
    *,
    instance: TSPInstance,
    matrix: list[list[int]],
    nearest: list[list[int]],
    clusters: list[int],
    scaffold: dict[str, Any],
    counter: EvalCounter,
    candidate_limit: int,
    seed_node: int,
) -> list[int]:
    mode = str(scaffold["construction_mode"])
    if mode == "cheapest_insertion":
        return _construct_cheapest_insertion(instance, matrix, counter, seed_node)
    if mode == "farthest_insertion":
        return _construct_farthest_insertion(instance, matrix, counter, seed_node)
    return _construct_nearest_neighbor(
        instance=instance,
        matrix=matrix,
        nearest=nearest,
        clusters=clusters,
        scaffold=scaffold,
        counter=counter,
        candidate_limit=candidate_limit,
        seed_node=seed_node,
    )


def _construct_nearest_neighbor(
    *,
    instance: TSPInstance,
    matrix: list[list[int]],
    nearest: list[list[int]],
    clusters: list[int],
    scaffold: dict[str, Any],
    counter: EvalCounter,
    candidate_limit: int,
    seed_node: int,
) -> list[int]:
    n = instance.dimension
    visited = {seed_node}
    tour = [seed_node]
    current = seed_node
    while len(tour) < n:
        candidates = [node for node in nearest[current][:candidate_limit] if node not in visited]
        if not candidates:
            candidates = [node for node in range(n) if node not in visited]
        if scaffold["construction_mode"] == "clustered_nearest" and scaffold["cluster_mode"] != "none":
            current_cluster = clusters[current]
            same_cluster = [node for node in candidates if clusters[node] == current_cluster]
            if same_cluster:
                candidates = same_cluster
        best_node = min(
            candidates,
            key=lambda node: (
                _distance(matrix, current, node, counter),
                node,
            ),
        )
        tour.append(best_node)
        visited.add(best_node)
        current = best_node
    return tour


def _construct_cheapest_insertion(instance: TSPInstance, matrix: list[list[int]], counter: EvalCounter, seed_node: int) -> list[int]:
    n = instance.dimension
    if n <= 3:
        return list(range(n))
    farthest = max(range(n), key=lambda node: _distance(matrix, seed_node, node, counter) if node != seed_node else -1)
    third = max((node for node in range(n) if node not in {seed_node, farthest}), key=lambda node: _distance(matrix, seed_node, node, counter))
    tour = [seed_node, farthest, third]
    remaining = [node for node in range(n) if node not in set(tour)]
    while remaining:
        best_choice = None
        for node in remaining:
            for index in range(len(tour)):
                left = tour[index]
                right = tour[(index + 1) % len(tour)]
                increase = _distance(matrix, left, node, counter) + _distance(matrix, node, right, counter) - _distance(matrix, left, right, counter)
                candidate = (increase, node, index + 1)
                if best_choice is None or candidate < best_choice:
                    best_choice = candidate
        assert best_choice is not None
        _, node, insert_at = best_choice
        tour.insert(insert_at, node)
        remaining.remove(node)
    return tour


def _construct_farthest_insertion(instance: TSPInstance, matrix: list[list[int]], counter: EvalCounter, seed_node: int) -> list[int]:
    n = instance.dimension
    if n <= 3:
        return list(range(n))
    farthest = max(range(n), key=lambda node: _distance(matrix, seed_node, node, counter) if node != seed_node else -1)
    third = max(
        (node for node in range(n) if node not in {seed_node, farthest}),
        key=lambda node: min(
            _distance(matrix, node, seed_node, counter),
            _distance(matrix, node, farthest, counter),
        ),
    )
    tour = [seed_node, farthest, third]
    remaining = [node for node in range(n) if node not in set(tour)]
    while remaining:
        node = max(
            remaining,
            key=lambda candidate: min(_distance(matrix, candidate, existing, counter) for existing in tour),
        )
        best_choice = None
        for index in range(len(tour)):
            left = tour[index]
            right = tour[(index + 1) % len(tour)]
            increase = _distance(matrix, left, node, counter) + _distance(matrix, node, right, counter) - _distance(matrix, left, right, counter)
            candidate = (increase, index + 1)
            if best_choice is None or candidate < best_choice:
                best_choice = candidate
        assert best_choice is not None
        _, insert_at = best_choice
        tour.insert(insert_at, node)
        remaining.remove(node)
    return tour


def _local_search(
    *,
    instance: TSPInstance,
    matrix: list[list[int]],
    nearest: list[list[int]],
    clusters: list[int],
    tour: list[int],
    scaffold: dict[str, Any],
    operator: dict[str, Any] | None,
    descriptors: dict[str, Any],
    counter: EvalCounter,
    candidate_limit: int,
    stagnation_state: dict[str, Any],
) -> tuple[list[int], int, int]:
    current = list(tour)
    starting_cost = _tour_cost(matrix, current, counter)
    current = _apply_two_opt(
        instance=instance,
        matrix=matrix,
        nearest=nearest,
        clusters=clusters,
        tour=current,
        passes=int(scaffold["two_opt_passes"]),
        candidate_limit=int(scaffold["two_opt_candidate_limit"] if operator is None or operator.get("operator_type") != "candidate_pruner" else candidate_limit),
        operator=operator,
        descriptors=descriptors,
        counter=counter,
        stagnation_state=stagnation_state,
    )
    after_two_opt = _tour_cost(matrix, current, counter)
    current = _apply_or_opt(matrix, current, int(scaffold["or_opt_span"]), counter)
    after_or_opt = _tour_cost(matrix, current, counter)
    current = _apply_three_opt(instance, matrix, current, int(scaffold["three_opt_samples"]), counter) if scaffold["use_three_opt"] else current
    final_cost = _tour_cost(matrix, current, counter)
    two_opt_gain = max(0, starting_cost - after_or_opt)
    three_opt_gain = max(0, after_or_opt - final_cost)
    return current, two_opt_gain, three_opt_gain


def _apply_two_opt(
    *,
    instance: TSPInstance,
    matrix: list[list[int]],
    nearest: list[list[int]],
    clusters: list[int],
    tour: list[int],
    passes: int,
    candidate_limit: int,
    operator: dict[str, Any] | None,
    descriptors: dict[str, Any],
    counter: EvalCounter,
    stagnation_state: dict[str, Any],
) -> list[int]:
    n = len(tour)
    current = list(tour)
    for _ in range(passes):
        improved = False
        position = {node: index for index, node in enumerate(current)}
        for i in range(n - 1):
            a = current[i]
            b = current[(i + 1) % n]
            candidates: list[dict[str, Any]] = []
            for rank, candidate_node in enumerate(nearest[a][:candidate_limit]):
                j = position.get(candidate_node)
                if j is None or abs(i - j) <= 1 or (i == 0 and j == n - 1):
                    continue
                c = current[j]
                d = current[(j + 1) % n]
                removed = _distance(matrix, a, b, counter) + _distance(matrix, c, d, counter)
                added = _distance(matrix, a, c, counter) + _distance(matrix, b, d, counter)
                delta = added - removed
                span_ratio = abs(j - i) / max(1.0, n - 1.0)
                crossing_hint = 1.0 if _segments_cross(instance.coordinates[a], instance.coordinates[b], instance.coordinates[c], instance.coordinates[d]) else 0.0
                long_edge_ratio = removed / max(1.0, sum(_bbox_scale(instance.coordinates)))
                cluster_match = 1.0 if clusters[a] == clusters[c] else 0.0
                candidates.append(
                    {
                        "i": i,
                        "j": j,
                        "delta": delta,
                        "delta_norm": delta / max(1.0, removed),
                        "span_ratio": span_ratio,
                        "nn_rank_ratio": rank / max(1.0, candidate_limit - 1),
                        "crossing_hint": crossing_hint,
                        "trap_score": float(descriptors.get("nearest_neighbor_trap_score", 0.0)),
                        "clusteredness_score": float(descriptors.get("clusteredness_score", 0.0)),
                        "cluster_match": cluster_match,
                        "long_edge_ratio": long_edge_ratio,
                    }
                )
            ordered = _rank_two_opt_candidates(candidates, operator)
            for move in ordered:
                if float(move["delta"]) < 0:
                    left = min(int(move["i"]) + 1, int(move["j"]))
                    right = max(int(move["i"]) + 1, int(move["j"]))
                    current[left : right + 1] = reversed(current[left : right + 1])
                    improved = True
                    break
            if improved:
                break
        if not improved:
            stagnation_state["stagnation_count"] = int(stagnation_state.get("stagnation_count", 0)) + 1
            break
        stagnation_state["stagnation_count"] = 0
    return current


def _rank_two_opt_candidates(candidates: list[dict[str, Any]], operator: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not candidates:
        return []
    if operator and operator.get("operator_type") == "candidate_ranker":
        ordered = sorted(candidates, key=lambda item: _candidate_rank_score(item, operator))
    else:
        ordered = sorted(candidates, key=lambda item: (float(item["delta"]), -float(item["crossing_hint"]), -float(item["span_ratio"])))
    return ordered


def _candidate_rank_score(move: dict[str, Any], operator: dict[str, Any]) -> float:
    score = float(operator["move_delta_weight"]) * float(move["delta_norm"])
    score -= float(operator["crossing_bonus"]) * float(move["crossing_hint"])
    score -= float(operator["span_bonus"]) * float(move["span_ratio"])
    score += float(operator["nn_rank_penalty"]) * float(move["nn_rank_ratio"])
    score -= float(operator["trap_bonus"]) * float(move["trap_score"]) * max(0.2, float(move["span_ratio"]))
    score -= float(operator["cluster_bonus"]) * float(move["clusteredness_score"]) * float(move["cluster_match"])
    score -= float(operator["long_edge_bonus"]) * float(move["long_edge_ratio"])
    return score


def _apply_or_opt(matrix: list[list[int]], tour: list[int], span: int, counter: EvalCounter) -> list[int]:
    current = list(tour)
    n = len(current)
    if n > 80 or span <= 0:
        return current
    for window in range(span, 0, -1):
        improved = False
        for start in range(0, min(n - window, 10)):
            segment = current[start : start + window]
            remaining = current[:start] + current[start + window :]
            base_cost = _tour_cost(matrix, current, counter)
            best_cost = base_cost
            best_tour = current
            candidate_positions = {1, len(remaining) // 3, (2 * len(remaining)) // 3, max(1, len(remaining) - 1)}
            for insert_at in sorted(position for position in candidate_positions if 0 < position < len(remaining)):
                candidate = remaining[:insert_at] + segment + remaining[insert_at:]
                candidate_cost = _tour_cost(matrix, candidate, counter)
                if candidate_cost < best_cost:
                    best_cost = candidate_cost
                    best_tour = candidate
            if best_tour is not current:
                current = best_tour
                improved = True
                break
        if not improved:
            break
    return current


def _apply_three_opt(instance: TSPInstance, matrix: list[list[int]], tour: list[int], samples: int, counter: EvalCounter) -> list[int]:
    if samples <= 0 or len(tour) > 120:
        return tour
    current = list(tour)
    n = len(current)
    best_cost = _tour_cost(matrix, current, counter)
    for sample_index in range(samples):
        i = 1 + ((7 * sample_index) % max(1, n - 5))
        j = i + 2 + ((5 * sample_index) % max(1, n - i - 3))
        k = j + 2 + ((3 * sample_index) % max(1, n - j - 1))
        if k >= n:
            break
        a = current[:i]
        b = current[i:j]
        c = current[j:k]
        d = current[k:]
        candidates = [
            a + list(reversed(b)) + c + d,
            a + b + list(reversed(c)) + d,
            a + c + b + d,
            a + list(reversed(c)) + list(reversed(b)) + d,
        ]
        for candidate in candidates:
            candidate_cost = _tour_cost(matrix, candidate, counter)
            if candidate_cost < best_cost:
                current = candidate
                best_cost = candidate_cost
    return current


def _perturb_tour(tour: list[int], mode: str, strength: int, seed: int) -> list[int]:
    n = len(tour)
    if n < 8:
        return tour
    offset = max(2, (abs(seed) % max(3, n // 4)))
    current = list(tour)
    if mode == "segment_reversal":
        for attempt in range(strength):
            start = 1 + ((offset + (attempt * 3)) % max(2, n - 4))
            end = min(n - 1, start + 2 + attempt)
            current[start:end] = reversed(current[start:end])
        return current
    if mode == "shuffle_window":
        start = 1 + (offset % max(2, n - 5))
        window = current[start : start + 4]
        current[start : start + 4] = window[2:] + window[:2]
        return current
    if mode == "edge_preserving_shuffle":
        protected = {
            0,
            max(1, n // 4),
            max(2, n // 2),
            max(3, (3 * n) // 4),
        }
        movable = [node for index, node in enumerate(current) if index not in protected]
        if len(movable) < 4:
            return current
        rotate = 1 + (offset % max(1, min(4, len(movable) - 1)))
        rotated = movable[rotate:] + movable[:rotate]
        result = list(current)
        cursor = 0
        for index in range(n):
            if index in protected:
                continue
            result[index] = rotated[cursor]
            cursor += 1
        return result
    cut1 = 1 + (offset % max(2, n - 6))
    cut2 = cut1 + max(2, n // 6)
    cut3 = min(n - 2, cut2 + max(2, n // 6))
    cut4 = min(n, cut3 + max(2, n // 6))
    return current[:cut1] + current[cut3:cut4] + current[cut2:cut3] + current[cut1:cut2] + current[cut4:]


def _should_accept_restart(
    *,
    candidate_cost: int,
    incumbent_cost: int | None,
    scaffold: dict[str, Any],
    operator: dict[str, Any] | None,
    stagnation_state: dict[str, Any],
    restart_index: int,
) -> bool:
    if incumbent_cost is None:
        return True
    if candidate_cost <= incumbent_cost:
        return True
    mode = str(scaffold["acceptance_mode"])
    base_threshold = float(scaffold["base_threshold"])
    temperature = float(scaffold["temperature"])
    if operator and operator.get("operator_type") == "acceptance":
        mode = str(operator["mode"])
        base_threshold = float(operator["base_threshold"]) + (float(operator["stagnation_bonus"]) * min(3, int(stagnation_state.get("stagnation_count", 0))))
        temperature = max(0.0, float(operator["temperature"]) - (float(operator["late_search_cooling"]) * restart_index))
    if mode == "threshold":
        limit = incumbent_cost * (1.0 + base_threshold)
        return candidate_cost <= limit
    if mode == "annealed":
        limit = incumbent_cost * (1.0 + max(0.0, temperature))
        return candidate_cost <= limit
    return False


def _seed_candidates(instance: TSPInstance, seed_mode: str) -> list[int]:
    centroid_x = sum(point[0] for point in instance.coordinates) / max(1, len(instance.coordinates))
    centroid_y = sum(point[1] for point in instance.coordinates) / max(1, len(instance.coordinates))
    nodes = list(range(instance.dimension))
    if seed_mode == "nearest_centroid":
        return sorted(nodes, key=lambda node: abs(instance.coordinates[node][0] - centroid_x) + abs(instance.coordinates[node][1] - centroid_y))
    if seed_mode == "lowest_x":
        return sorted(nodes, key=lambda node: (instance.coordinates[node][0], instance.coordinates[node][1]))
    if seed_mode == "highest_y":
        return sorted(nodes, key=lambda node: (-instance.coordinates[node][1], instance.coordinates[node][0]))
    return sorted(nodes, key=lambda node: -(abs(instance.coordinates[node][0] - centroid_x) + abs(instance.coordinates[node][1] - centroid_y)))


def _nearest_candidates(matrix: list[list[int]], limit: int) -> list[list[int]]:
    candidates: list[list[int]] = []
    for row_index, row in enumerate(matrix):
        ordering = sorted((distance, column_index) for column_index, distance in enumerate(row) if column_index != row_index)
        candidates.append([column_index for _, column_index in ordering[:limit]])
    return candidates


def _cluster_labels(instance: TSPInstance, mode: str, cluster_count: int) -> list[int]:
    if mode == "none" or cluster_count <= 1:
        return [0 for _ in instance.coordinates]
    xs = [point[0] for point in instance.coordinates]
    ys = [point[1] for point in instance.coordinates]
    centroid_x = sum(xs) / max(1, len(xs))
    centroid_y = sum(ys) / max(1, len(ys))
    if mode == "x_sweep":
        ordered = sorted(range(len(xs)), key=lambda index: (xs[index], ys[index]))
    elif mode == "y_sweep":
        ordered = sorted(range(len(xs)), key=lambda index: (ys[index], xs[index]))
    else:
        ordered = sorted(range(len(xs)), key=lambda index: math.atan2(ys[index] - centroid_y, xs[index] - centroid_x))
    bucket_size = max(1, math.ceil(len(ordered) / cluster_count))
    labels = [0 for _ in ordered]
    for position, node in enumerate(ordered):
        labels[node] = min(cluster_count - 1, position // bucket_size)
    return labels


def _count_crossings(instance: TSPInstance, tour: list[int]) -> int:
    crossings = 0
    points = instance.coordinates
    n = len(tour)
    for left in range(n):
        a = points[tour[left]]
        b = points[tour[(left + 1) % n]]
        for right in range(left + 2, n):
            if right == left or (right + 1) % n == left:
                continue
            c = points[tour[right]]
            d = points[tour[(right + 1) % n]]
            if _segments_cross(a, b, c, d):
                crossings += 1
    return crossings


def _segments_cross(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> bool:
    def ccw(left: tuple[float, float], middle: tuple[float, float], right: tuple[float, float]) -> bool:
        return (right[1] - left[1]) * (middle[0] - left[0]) > (middle[1] - left[1]) * (right[0] - left[0])

    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)


def _edge_lengths(matrix: list[list[int]], tour: list[int], counter: EvalCounter) -> list[int]:
    return [_distance(matrix, tour[index], tour[(index + 1) % len(tour)], counter) for index in range(len(tour))]


def _tour_cost(matrix: list[list[int]], tour: list[int], counter: EvalCounter) -> int:
    return sum(_distance(matrix, tour[index], tour[(index + 1) % len(tour)], counter) for index in range(len(tour)))


def _distance(matrix: list[list[int]], left: int, right: int, counter: EvalCounter) -> int:
    counter.distance_evaluations += 1
    return matrix[left][right]


def _bbox_scale(coords: list[tuple[float, float]]) -> tuple[float, float]:
    xs = [point[0] for point in coords]
    ys = [point[1] for point in coords]
    return max(xs) - min(xs), max(ys) - min(ys)
