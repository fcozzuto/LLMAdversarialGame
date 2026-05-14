from __future__ import annotations

from dataclasses import dataclass
import copy
import math
from typing import Any

from .benchmark import CVRPInstance, build_distance_matrix


DEFAULT_HEURISTIC_SPEC: dict[str, Any] = {
    "name": "cvrp_savings_restarts",
    "construction": {
        "seed_mode": "farthest_from_depot",
        "candidate_limit": 12,
        "lookahead_limit": 2,
        "distance_weight": 1.0,
        "demand_weight": 0.22,
        "savings_bonus": 0.28,
        "cluster_mode": "none",
        "cluster_count": 1,
        "cluster_bonus": 0.18,
        "route_fill_target": 0.88,
    },
    "local_search": {
        "two_opt_passes": 2,
        "route_relocate_passes": 1,
        "inter_route_relocate_samples": 10,
        "inter_route_swap_samples": 8,
        "use_three_opt": False,
        "three_opt_samples": 0,
    },
    "perturbation": {
        "enabled": True,
        "mode": "customer_reinsert",
        "strength": 1,
        "attempts": 1,
    },
    "restart": {
        "restart_count": 4,
        "seed_pool_size": 4,
        "use_perturbation_restarts": True,
    },
    "acceptance": {
        "mode": "improving_only",
        "worse_acceptance_threshold": 0.0,
        "annealing_temperature": 0.0,
    },
}


def default_heuristic_code() -> str:
    return """
def build_heuristic():
    return {
        "name": "cvrp_savings_restarts",
        "construction": {
            "seed_mode": "farthest_from_depot",
            "candidate_limit": 12,
            "lookahead_limit": 2,
            "distance_weight": 1.0,
            "demand_weight": 0.22,
            "savings_bonus": 0.28,
            "cluster_mode": "none",
            "cluster_count": 1,
            "cluster_bonus": 0.18,
            "route_fill_target": 0.88,
        },
        "local_search": {
            "two_opt_passes": 2,
            "route_relocate_passes": 1,
            "inter_route_relocate_samples": 10,
            "inter_route_swap_samples": 8,
            "use_three_opt": False,
            "three_opt_samples": 0,
        },
        "perturbation": {
            "enabled": True,
            "mode": "customer_reinsert",
            "strength": 1,
            "attempts": 1,
        },
        "restart": {
            "restart_count": 4,
            "seed_pool_size": 4,
            "use_perturbation_restarts": True,
        },
        "acceptance": {
            "mode": "improving_only",
            "worse_acceptance_threshold": 0.0,
            "annealing_temperature": 0.0,
        },
    }
""".strip()


def builtin_heuristic_code(name: str) -> str:
    normalized = name.lower()
    if normalized in {"cvrp_default", "cvrp_savings_restarts"}:
        return default_heuristic_code()
    if normalized == "clustered_routes":
        return """
def build_heuristic():
    return {
        "name": "clustered_routes",
        "construction": {
            "seed_mode": "angular_sweep",
            "candidate_limit": 10,
            "lookahead_limit": 3,
            "distance_weight": 1.0,
            "demand_weight": 0.28,
            "savings_bonus": 0.34,
            "cluster_mode": "angular",
            "cluster_count": 4,
            "cluster_bonus": 0.28,
            "route_fill_target": 0.9,
        },
        "local_search": {
            "two_opt_passes": 3,
            "route_relocate_passes": 2,
            "inter_route_relocate_samples": 12,
            "inter_route_swap_samples": 10,
            "use_three_opt": True,
            "three_opt_samples": 6,
        },
        "perturbation": {
            "enabled": True,
            "mode": "route_shuffle",
            "strength": 2,
            "attempts": 2,
        },
        "restart": {
            "restart_count": 5,
            "seed_pool_size": 5,
            "use_perturbation_restarts": True,
        },
        "acceptance": {
            "mode": "threshold",
            "worse_acceptance_threshold": 0.004,
            "annealing_temperature": 0.0,
        },
    }
""".strip()
    if normalized == "compact_transfer":
        return """
def build_heuristic():
    return {
        "name": "compact_transfer",
        "construction": {
            "seed_mode": "highest_demand",
            "candidate_limit": 9,
            "lookahead_limit": 2,
            "distance_weight": 1.0,
            "demand_weight": 0.2,
            "savings_bonus": 0.24,
            "cluster_mode": "x_sweep",
            "cluster_count": 3,
            "cluster_bonus": 0.18,
            "route_fill_target": 0.84,
        },
        "local_search": {
            "two_opt_passes": 2,
            "route_relocate_passes": 1,
            "inter_route_relocate_samples": 8,
            "inter_route_swap_samples": 6,
            "use_three_opt": False,
            "three_opt_samples": 0,
        },
        "perturbation": {
            "enabled": True,
            "mode": "customer_reinsert",
            "strength": 1,
            "attempts": 1,
        },
        "restart": {
            "restart_count": 3,
            "seed_pool_size": 3,
            "use_perturbation_restarts": True,
        },
        "acceptance": {
            "mode": "improving_only",
            "worse_acceptance_threshold": 0.0,
            "annealing_temperature": 0.0,
        },
    }
""".strip()
    return default_heuristic_code()


def canonicalize_heuristic_spec(raw: dict[str, Any] | None) -> dict[str, Any]:
    merged = copy.deepcopy(DEFAULT_HEURISTIC_SPEC)
    if raw:
        merged = _deep_merge(merged, raw)

    construction = merged["construction"]
    construction["seed_mode"] = _enum(
        str(construction.get("seed_mode", "")),
        {"farthest_from_depot", "highest_demand", "angular_sweep", "radial_sweep"},
        "farthest_from_depot",
    )
    construction["candidate_limit"] = _bounded_int(construction.get("candidate_limit", 12), 4, 30)
    construction["lookahead_limit"] = _bounded_int(construction.get("lookahead_limit", 2), 1, 6)
    construction["distance_weight"] = _bounded_float(construction.get("distance_weight", 1.0), 0.4, 2.5)
    construction["demand_weight"] = _bounded_float(construction.get("demand_weight", 0.22), 0.0, 1.2)
    construction["savings_bonus"] = _bounded_float(construction.get("savings_bonus", 0.28), 0.0, 1.5)
    construction["cluster_mode"] = _enum(
        str(construction.get("cluster_mode", "")),
        {"none", "angular", "x_sweep", "y_sweep"},
        "none",
    )
    construction["cluster_count"] = _bounded_int(construction.get("cluster_count", 1), 1, 6)
    construction["cluster_bonus"] = _bounded_float(construction.get("cluster_bonus", 0.18), 0.0, 1.0)
    construction["route_fill_target"] = _bounded_float(construction.get("route_fill_target", 0.88), 0.55, 0.99)
    if construction["cluster_mode"] == "none":
        construction["cluster_count"] = 1

    local_search = merged["local_search"]
    local_search["two_opt_passes"] = _bounded_int(local_search.get("two_opt_passes", 2), 1, 6)
    local_search["route_relocate_passes"] = _bounded_int(local_search.get("route_relocate_passes", 1), 0, 4)
    local_search["inter_route_relocate_samples"] = _bounded_int(local_search.get("inter_route_relocate_samples", 10), 0, 20)
    local_search["inter_route_swap_samples"] = _bounded_int(local_search.get("inter_route_swap_samples", 8), 0, 20)
    local_search["use_three_opt"] = bool(local_search.get("use_three_opt", False))
    local_search["three_opt_samples"] = _bounded_int(local_search.get("three_opt_samples", 0), 0, 12)
    if not local_search["use_three_opt"]:
        local_search["three_opt_samples"] = 0

    perturbation = merged["perturbation"]
    perturbation["enabled"] = bool(perturbation.get("enabled", True))
    perturbation["mode"] = _enum(
        str(perturbation.get("mode", "")),
        {"route_shuffle", "customer_reinsert", "segment_reversal"},
        "customer_reinsert",
    )
    perturbation["strength"] = _bounded_int(perturbation.get("strength", 1), 1, 4)
    perturbation["attempts"] = _bounded_int(perturbation.get("attempts", 1), 1, 4)

    restart = merged["restart"]
    restart["restart_count"] = _bounded_int(restart.get("restart_count", 4), 1, 10)
    restart["seed_pool_size"] = _bounded_int(restart.get("seed_pool_size", 4), 1, 10)
    restart["use_perturbation_restarts"] = bool(restart.get("use_perturbation_restarts", True))

    acceptance = merged["acceptance"]
    acceptance["mode"] = _enum(str(acceptance.get("mode", "")), {"improving_only", "threshold", "annealed"}, "improving_only")
    acceptance["worse_acceptance_threshold"] = _bounded_float(acceptance.get("worse_acceptance_threshold", 0.0), 0.0, 0.05)
    acceptance["annealing_temperature"] = _bounded_float(acceptance.get("annealing_temperature", 0.0), 0.0, 0.05)
    if acceptance["mode"] == "improving_only":
        acceptance["worse_acceptance_threshold"] = 0.0
        acceptance["annealing_temperature"] = 0.0

    merged["name"] = str(merged.get("name") or "unnamed_heuristic")[:80]
    return merged


@dataclass
class SolveTrace:
    construction_cost: int
    final_cost: int
    two_opt_gain: int
    route_relocate_gain: int
    three_opt_gain: int
    inter_route_gain: int
    restart_gain: int
    route_count: int
    candidate_limit: int
    cluster_count: int
    perturbation_attempts: int
    perturbation_accepts: int
    mean_load_factor: float
    max_load_factor: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "construction_cost": self.construction_cost,
            "final_cost": self.final_cost,
            "two_opt_gain": self.two_opt_gain,
            "route_relocate_gain": self.route_relocate_gain,
            "three_opt_gain": self.three_opt_gain,
            "inter_route_gain": self.inter_route_gain,
            "restart_gain": self.restart_gain,
            "route_count": self.route_count,
            "candidate_limit": self.candidate_limit,
            "cluster_count": self.cluster_count,
            "perturbation_attempts": self.perturbation_attempts,
            "perturbation_accepts": self.perturbation_accepts,
            "mean_load_factor": round(self.mean_load_factor, 4),
            "max_load_factor": round(self.max_load_factor, 4),
        }


def solve_instance(instance: CVRPInstance, spec: dict[str, Any], *, seed: int = 0) -> dict[str, Any]:
    spec = canonicalize_heuristic_spec(spec)
    matrix = build_distance_matrix(instance)
    nearest = _nearest_candidates(matrix, max(6, spec["construction"]["candidate_limit"]))
    clusters = _cluster_labels(instance, spec["construction"]["cluster_mode"], spec["construction"]["cluster_count"])
    seed_order = _seed_candidates(instance, spec["construction"]["seed_mode"])

    best_routes: list[list[int]] | None = None
    best_cost: int | None = None
    best_construction_cost = 0
    best_two_opt_gain = 0
    best_route_relocate_gain = 0
    best_three_opt_gain = 0
    best_inter_route_gain = 0
    perturbation_attempts = 0
    perturbation_accepts = 0
    current_routes: list[list[int]] | None = None

    for restart_index in range(spec["restart"]["restart_count"]):
        if restart_index == 0 or not spec["restart"]["use_perturbation_restarts"] or current_routes is None:
            candidate_routes = _construct_routes(instance, matrix, nearest, clusters, seed_order, spec)
        else:
            candidate_routes = _perturb_routes(instance, [list(route) for route in current_routes], spec["perturbation"]["mode"], spec["perturbation"]["strength"], seed + restart_index)
            perturbation_attempts += spec["perturbation"]["attempts"]
        construction_cost = _solution_cost(matrix, instance.depot_index, candidate_routes)
        improved_routes, two_opt_gain, route_relocate_gain, three_opt_gain, inter_route_gain = _local_search(
            instance,
            matrix,
            candidate_routes,
            spec,
        )
        improved_cost = _solution_cost(matrix, instance.depot_index, improved_routes)
        accepted = _should_accept_restart(
            candidate_cost=improved_cost,
            incumbent_cost=best_cost,
            spec=spec,
            restart_index=restart_index,
        )
        if accepted:
            if best_cost is not None and improved_cost > best_cost:
                perturbation_accepts += 1
            best_routes = [list(route) for route in improved_routes]
            best_cost = improved_cost
            best_construction_cost = construction_cost
            best_two_opt_gain = two_opt_gain
            best_route_relocate_gain = route_relocate_gain
            best_three_opt_gain = three_opt_gain
            best_inter_route_gain = inter_route_gain
            current_routes = [list(route) for route in improved_routes]
        elif current_routes is None:
            current_routes = [list(route) for route in improved_routes]

    if best_routes is None or best_cost is None:
        raise RuntimeError("Heuristic engine failed to produce a CVRP solution.")

    route_loads = [_route_load(instance.demands, route) for route in best_routes] or [0]
    trace = SolveTrace(
        construction_cost=best_construction_cost,
        final_cost=best_cost,
        two_opt_gain=best_two_opt_gain,
        route_relocate_gain=best_route_relocate_gain,
        three_opt_gain=best_three_opt_gain,
        inter_route_gain=best_inter_route_gain,
        restart_gain=max(0, best_construction_cost - best_cost),
        route_count=len(best_routes),
        candidate_limit=spec["construction"]["candidate_limit"],
        cluster_count=spec["construction"]["cluster_count"] if spec["construction"]["cluster_mode"] != "none" else 1,
        perturbation_attempts=perturbation_attempts,
        perturbation_accepts=perturbation_accepts,
        mean_load_factor=sum(route_loads) / max(1, len(route_loads) * instance.capacity),
        max_load_factor=max(route_loads) / max(1, instance.capacity),
    )
    gap = ((best_cost - instance.best_known_cost) / instance.best_known_cost) if instance.best_known_cost else 0.0
    return {
        "instance": instance.to_dict(),
        "routes": [list(route) for route in best_routes],
        "cost": best_cost,
        "best_known_cost": instance.best_known_cost,
        "optimality_gap": round(gap, 6),
        "trace": trace.to_dict(),
        "heuristic_name": spec["name"],
    }


def aggregate_descriptor(results: list[dict[str, Any]]) -> dict[str, float]:
    if not results:
        return {
            "mean_gap_ratio": 0.0,
            "construction_gain_ratio": 0.0,
            "two_opt_gain_ratio": 0.0,
            "route_relocate_gain_ratio": 0.0,
            "three_opt_gain_ratio": 0.0,
            "inter_route_gain_ratio": 0.0,
            "restart_gain_ratio": 0.0,
            "candidate_pruning_ratio": 0.0,
            "cluster_usage_ratio": 0.0,
            "load_factor_ratio": 0.0,
            "perturbation_accept_ratio": 0.0,
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
    route_relocate_gain = sum(
        max(0.0, float(item["trace"]["route_relocate_gain"]) / max(1.0, float(item["trace"]["construction_cost"])))
        for item in results
    ) / len(results)
    three_opt_gain = sum(
        max(0.0, float(item["trace"]["three_opt_gain"]) / max(1.0, float(item["trace"]["construction_cost"])))
        for item in results
    ) / len(results)
    inter_route_gain = sum(
        max(0.0, float(item["trace"]["inter_route_gain"]) / max(1.0, float(item["trace"]["construction_cost"])))
        for item in results
    ) / len(results)
    restart_gain = sum(
        max(0.0, float(item["trace"]["restart_gain"]) / max(1.0, float(item["trace"]["construction_cost"])))
        for item in results
    ) / len(results)
    candidate_pruning = sum(
        float(item["trace"]["candidate_limit"]) / max(1.0, float(int(item["instance"]["dimension"]) - 1))
        for item in results
    ) / len(results)
    cluster_usage = sum(
        0.0 if int(item["trace"]["cluster_count"]) <= 1 else min(1.0, int(item["trace"]["cluster_count"]) / 6.0)
        for item in results
    ) / len(results)
    load_factor = sum(float(item["trace"]["mean_load_factor"]) for item in results) / len(results)
    perturbation_accept = sum(
        float(item["trace"]["perturbation_accepts"]) / max(1.0, float(item["trace"]["perturbation_attempts"] or 1.0))
        for item in results
    ) / len(results)
    return {
        "mean_gap_ratio": round(mean_gap, 6),
        "construction_gain_ratio": round(construction_gain, 6),
        "two_opt_gain_ratio": round(two_opt_gain, 6),
        "route_relocate_gain_ratio": round(route_relocate_gain, 6),
        "three_opt_gain_ratio": round(three_opt_gain, 6),
        "inter_route_gain_ratio": round(inter_route_gain, 6),
        "restart_gain_ratio": round(restart_gain, 6),
        "candidate_pruning_ratio": round(candidate_pruning, 6),
        "cluster_usage_ratio": round(cluster_usage, 6),
        "load_factor_ratio": round(load_factor, 6),
        "perturbation_accept_ratio": round(perturbation_accept, 6),
    }


def _construct_routes(
    instance: CVRPInstance,
    matrix: list[list[int]],
    nearest: list[list[int]],
    clusters: list[int],
    seed_order: list[int],
    spec: dict[str, Any],
) -> list[list[int]]:
    depot = instance.depot_index
    remaining = {node for node in range(instance.dimension) if node != depot}
    routes: list[list[int]] = []
    construction = spec["construction"]
    while remaining:
        seed = next(node for node in seed_order if node in remaining)
        route = [seed]
        remaining.remove(seed)
        current = seed
        load = instance.demands[seed]
        target_cluster = clusters[seed] if construction["cluster_mode"] != "none" else None
        while True:
            candidates = [
                node
                for node in nearest[current][: construction["candidate_limit"]]
                if node in remaining and load + instance.demands[node] <= instance.capacity
            ]
            if not candidates:
                candidates = [
                    node for node in remaining
                    if load + instance.demands[node] <= instance.capacity
                ]
            if not candidates:
                break
            best_node = min(
                candidates,
                key=lambda node: _candidate_score(
                    instance=instance,
                    matrix=matrix,
                    nearest=nearest,
                    current=current,
                    candidate=node,
                    remaining=remaining,
                    current_load=load,
                    clusters=clusters,
                    target_cluster=target_cluster,
                    spec=spec,
                ),
            )
            route.append(best_node)
            remaining.remove(best_node)
            load += instance.demands[best_node]
            current = best_node
        routes.append(route)
    return routes


def _candidate_score(
    *,
    instance: CVRPInstance,
    matrix: list[list[int]],
    nearest: list[list[int]],
    current: int,
    candidate: int,
    remaining: set[int],
    current_load: int,
    clusters: list[int],
    target_cluster: int | None,
    spec: dict[str, Any],
) -> float:
    construction = spec["construction"]
    base_distance = float(matrix[current][candidate]) * float(construction["distance_weight"])
    target_fill = float(construction["route_fill_target"]) * float(instance.capacity)
    projected_load = current_load + instance.demands[candidate]
    fill_penalty = float(construction["demand_weight"]) * abs(projected_load - target_fill) / max(1.0, instance.capacity)
    savings = float(matrix[instance.depot_index][current] + matrix[instance.depot_index][candidate] - matrix[current][candidate])
    lookahead = _lookahead_score(instance, matrix, nearest, candidate, remaining, current_load, spec["construction"]["lookahead_limit"])
    score = base_distance + (fill_penalty * max(1.0, base_distance * 0.3)) - (float(construction["savings_bonus"]) * savings * 0.35) - lookahead
    if target_cluster is not None and clusters[candidate] == target_cluster:
        score -= float(construction["cluster_bonus"]) * max(1.0, base_distance * 0.2)
    return score


def _lookahead_score(
    instance: CVRPInstance,
    matrix: list[list[int]],
    nearest: list[list[int]],
    candidate: int,
    remaining: set[int],
    current_load: int,
    lookahead_limit: int,
) -> float:
    feasible = [
        node
        for node in nearest[candidate][: lookahead_limit + 1]
        if node in remaining and node != candidate and current_load + instance.demands[candidate] + instance.demands[node] <= instance.capacity
    ][:lookahead_limit]
    if not feasible:
        return 0.0
    mean_cost = sum(matrix[candidate][node] for node in feasible) / len(feasible)
    return max(0.0, 8.0 / max(1.0, mean_cost))


def _local_search(
    instance: CVRPInstance,
    matrix: list[list[int]],
    routes: list[list[int]],
    spec: dict[str, Any],
) -> tuple[list[list[int]], int, int, int, int]:
    current = [list(route) for route in routes]
    starting_cost = _solution_cost(matrix, instance.depot_index, current)
    current = [_apply_two_opt_route(matrix, instance.depot_index, route, spec["local_search"]["two_opt_passes"]) for route in current]
    after_two_opt = _solution_cost(matrix, instance.depot_index, current)
    current = [
        _apply_route_relocate(matrix, instance.depot_index, route, spec["local_search"]["route_relocate_passes"])
        for route in current
    ]
    after_route_relocate = _solution_cost(matrix, instance.depot_index, current)
    if spec["local_search"]["use_three_opt"]:
        current = [
            _apply_three_opt_route(matrix, instance.depot_index, route, spec["local_search"]["three_opt_samples"])
            for route in current
        ]
    after_three_opt = _solution_cost(matrix, instance.depot_index, current)
    current = _apply_inter_route_relocate(instance, matrix, current, spec["local_search"]["inter_route_relocate_samples"])
    current = _apply_inter_route_swap(instance, matrix, current, spec["local_search"]["inter_route_swap_samples"])
    final_cost = _solution_cost(matrix, instance.depot_index, current)
    return (
        current,
        max(0, starting_cost - after_two_opt),
        max(0, after_two_opt - after_route_relocate),
        max(0, after_route_relocate - after_three_opt),
        max(0, after_three_opt - final_cost),
    )


def _apply_two_opt_route(matrix: list[list[int]], depot: int, route: list[int], passes: int) -> list[int]:
    current = list(route)
    n = len(current)
    if n < 4:
        return current
    for _ in range(passes):
        improved = False
        base_cost = _route_cost(matrix, depot, current)
        for left in range(0, n - 2):
            for right in range(left + 2, n):
                candidate = current[:left] + list(reversed(current[left:right + 1])) + current[right + 1 :]
                candidate_cost = _route_cost(matrix, depot, candidate)
                if candidate_cost < base_cost:
                    current = candidate
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break
    return current


def _apply_route_relocate(matrix: list[list[int]], depot: int, route: list[int], passes: int) -> list[int]:
    current = list(route)
    n = len(current)
    if n < 3 or passes <= 0:
        return current
    for _ in range(passes):
        improved = False
        base_cost = _route_cost(matrix, depot, current)
        for start in range(n):
            customer = current[start]
            remaining = current[:start] + current[start + 1 :]
            for insert_at in range(len(remaining) + 1):
                if insert_at == start:
                    continue
                candidate = remaining[:insert_at] + [customer] + remaining[insert_at:]
                candidate_cost = _route_cost(matrix, depot, candidate)
                if candidate_cost < base_cost:
                    current = candidate
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break
    return current


def _apply_three_opt_route(matrix: list[list[int]], depot: int, route: list[int], samples: int) -> list[int]:
    current = list(route)
    if samples <= 0 or len(current) < 6 or len(current) > 18:
        return current
    n = len(current)
    best_cost = _route_cost(matrix, depot, current)
    for sample_index in range(samples):
        i = 1 + ((5 * sample_index) % max(1, n - 4))
        j = i + 1 + ((3 * sample_index) % max(1, n - i - 2))
        k = j + 1 + ((2 * sample_index) % max(1, n - j - 1))
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
            candidate_cost = _route_cost(matrix, depot, candidate)
            if candidate_cost < best_cost:
                current = candidate
                best_cost = candidate_cost
    return current


def _apply_inter_route_relocate(
    instance: CVRPInstance,
    matrix: list[list[int]],
    routes: list[list[int]],
    samples: int,
) -> list[list[int]]:
    current = [list(route) for route in routes]
    if samples <= 0 or len(current) < 2:
        return current
    for sample_index in range(samples):
        source_idx = sample_index % len(current)
        target_idx = (source_idx + 1 + ((2 * sample_index) % max(1, len(current) - 1))) % len(current)
        if source_idx == target_idx or not current[source_idx]:
            continue
        source_route = current[source_idx]
        target_route = current[target_idx]
        customer_pos = (sample_index * 3) % len(source_route)
        customer = source_route[customer_pos]
        if _route_load(instance.demands, target_route) + instance.demands[customer] > instance.capacity:
            continue
        base_cost = _solution_cost(matrix, instance.depot_index, current)
        remaining_source = source_route[:customer_pos] + source_route[customer_pos + 1 :]
        for insert_at in {0, len(target_route) // 2, len(target_route)}:
            candidate_routes = [list(route) for route in current]
            candidate_routes[source_idx] = remaining_source
            candidate_routes[target_idx] = target_route[:insert_at] + [customer] + target_route[insert_at:]
            candidate_routes = [route for route in candidate_routes if route]
            candidate_cost = _solution_cost(matrix, instance.depot_index, candidate_routes)
            if candidate_cost < base_cost:
                current = candidate_routes
                break
    return current


def _apply_inter_route_swap(
    instance: CVRPInstance,
    matrix: list[list[int]],
    routes: list[list[int]],
    samples: int,
) -> list[list[int]]:
    current = [list(route) for route in routes]
    if samples <= 0 or len(current) < 2:
        return current
    for sample_index in range(samples):
        left_idx = sample_index % len(current)
        right_idx = (left_idx + 1 + ((3 * sample_index) % max(1, len(current) - 1))) % len(current)
        if left_idx == right_idx or not current[left_idx] or not current[right_idx]:
            continue
        left_route = current[left_idx]
        right_route = current[right_idx]
        left_pos = (sample_index * 2) % len(left_route)
        right_pos = (sample_index * 5) % len(right_route)
        left_customer = left_route[left_pos]
        right_customer = right_route[right_pos]
        left_load = _route_load(instance.demands, left_route) - instance.demands[left_customer] + instance.demands[right_customer]
        right_load = _route_load(instance.demands, right_route) - instance.demands[right_customer] + instance.demands[left_customer]
        if left_load > instance.capacity or right_load > instance.capacity:
            continue
        candidate_routes = [list(route) for route in current]
        candidate_routes[left_idx][left_pos] = right_customer
        candidate_routes[right_idx][right_pos] = left_customer
        if _solution_cost(matrix, instance.depot_index, candidate_routes) < _solution_cost(matrix, instance.depot_index, current):
            current = candidate_routes
    return current


def _perturb_routes(
    instance: CVRPInstance,
    routes: list[list[int]],
    mode: str,
    strength: int,
    seed: int,
) -> list[list[int]]:
    current = [list(route) for route in routes if route]
    if not current:
        return current
    if mode == "route_shuffle":
        return list(reversed(current))
    if mode == "segment_reversal":
        for index, route in enumerate(current):
            if len(route) >= 4:
                start = 1 + ((seed + index) % max(1, len(route) - 3))
                end = min(len(route), start + 2 + strength)
                route[start:end] = reversed(route[start:end])
                return current
        return current
    source_idx = abs(seed) % len(current)
    source_route = current[source_idx]
    if not source_route:
        return current
    customer_pos = (abs(seed) // 3) % len(source_route)
    customer = source_route.pop(customer_pos)
    for offset in range(1, len(current) + 1):
        target_idx = (source_idx + offset) % len(current)
        if _route_load(instance.demands, current[target_idx]) + instance.demands[customer] <= instance.capacity:
            insert_at = min(len(current[target_idx]), strength % (len(current[target_idx]) + 1))
            current[target_idx] = current[target_idx][:insert_at] + [customer] + current[target_idx][insert_at:]
            return [route for route in current if route]
    source_route.insert(customer_pos, customer)
    return [route for route in current if route]


def _should_accept_restart(*, candidate_cost: int, incumbent_cost: int | None, spec: dict[str, Any], restart_index: int) -> bool:
    if incumbent_cost is None:
        return True
    if candidate_cost <= incumbent_cost:
        return True
    mode = spec["acceptance"]["mode"]
    if mode == "threshold":
        limit = incumbent_cost * (1.0 + float(spec["acceptance"]["worse_acceptance_threshold"]))
        return candidate_cost <= limit
    if mode == "annealed":
        temperature = float(spec["acceptance"]["annealing_temperature"])
        limit = incumbent_cost * (1.0 + max(0.0, temperature - (0.001 * restart_index)))
        return candidate_cost <= limit
    return False


def _seed_candidates(instance: CVRPInstance, seed_mode: str) -> list[int]:
    depot = instance.coordinates[instance.depot_index]
    customers = [node for node in range(instance.dimension) if node != instance.depot_index]
    if seed_mode == "highest_demand":
        return sorted(customers, key=lambda node: (-instance.demands[node], -_distance(instance.coordinates[node], depot)))
    if seed_mode == "angular_sweep":
        return sorted(customers, key=lambda node: math.atan2(instance.coordinates[node][1] - depot[1], instance.coordinates[node][0] - depot[0]))
    if seed_mode == "radial_sweep":
        return sorted(customers, key=lambda node: (_distance(instance.coordinates[node], depot), math.atan2(instance.coordinates[node][1] - depot[1], instance.coordinates[node][0] - depot[0])))
    return sorted(customers, key=lambda node: -_distance(instance.coordinates[node], depot))


def _nearest_candidates(matrix: list[list[int]], limit: int) -> list[list[int]]:
    candidates: list[list[int]] = []
    for row_index, row in enumerate(matrix):
        ordering = sorted((distance, column_index) for column_index, distance in enumerate(row) if column_index != row_index)
        candidates.append([column_index for _, column_index in ordering[:limit]])
    return candidates


def _cluster_labels(instance: CVRPInstance, mode: str, cluster_count: int) -> list[int]:
    if mode == "none" or cluster_count <= 1:
        return [0 for _ in instance.coordinates]
    depot = instance.coordinates[instance.depot_index]
    customers = [node for node in range(instance.dimension) if node != instance.depot_index]
    if mode == "x_sweep":
        ordered = sorted(customers, key=lambda node: (instance.coordinates[node][0], instance.coordinates[node][1]))
    elif mode == "y_sweep":
        ordered = sorted(customers, key=lambda node: (instance.coordinates[node][1], instance.coordinates[node][0]))
    else:
        ordered = sorted(customers, key=lambda node: math.atan2(instance.coordinates[node][1] - depot[1], instance.coordinates[node][0] - depot[0]))
    bucket_size = max(1, math.ceil(len(ordered) / cluster_count))
    labels = [0 for _ in instance.coordinates]
    for position, node in enumerate(ordered):
        labels[node] = min(cluster_count - 1, position // bucket_size)
    return labels


def _route_cost(matrix: list[list[int]], depot: int, route: list[int]) -> int:
    if not route:
        return 0
    total = matrix[depot][route[0]]
    for index in range(len(route) - 1):
        total += matrix[route[index]][route[index + 1]]
    total += matrix[route[-1]][depot]
    return total


def _solution_cost(matrix: list[list[int]], depot: int, routes: list[list[int]]) -> int:
    return sum(_route_cost(matrix, depot, route) for route in routes if route)


def _route_load(demands: list[int], route: list[int]) -> int:
    return sum(demands[node] for node in route)


def _distance(left: tuple[float, float], right: tuple[float, float]) -> float:
    return math.sqrt(((left[0] - right[0]) ** 2) + ((left[1] - right[1]) ** 2))


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _bounded_int(value: Any, lower: int, upper: int) -> int:
    return max(lower, min(upper, int(value)))


def _bounded_float(value: Any, lower: float, upper: float) -> float:
    return max(lower, min(upper, float(value)))


def _enum(value: str, options: set[str], default: str) -> str:
    normalized = value.strip().lower()
    return normalized if normalized in options else default
