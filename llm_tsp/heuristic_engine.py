from __future__ import annotations

from dataclasses import dataclass
import copy
import math
from typing import Any

from .benchmark import TSPInstance, build_distance_matrix


DEFAULT_HEURISTIC_SPEC: dict[str, Any] = {
    "name": "nn_restarts_2opt",
    "construction": {
        "seed_mode": "farthest_from_centroid",
        "candidate_limit": 14,
        "lookahead_limit": 3,
        "distance_weight": 1.0,
        "density_penalty": 0.18,
        "angle_penalty": 0.08,
        "regret_bonus": 0.06,
        "cluster_mode": "none",
        "cluster_count": 1,
        "cluster_bonus": 0.16,
    },
    "local_search": {
        "two_opt_passes": 3,
        "two_opt_candidate_limit": 18,
        "use_three_opt": False,
        "three_opt_samples": 0,
        "or_opt_span": 2,
    },
    "perturbation": {
        "enabled": True,
        "mode": "double_bridge",
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
        "name": "nn_restarts_2opt",
        "construction": {
            "seed_mode": "farthest_from_centroid",
            "candidate_limit": 14,
            "lookahead_limit": 3,
            "distance_weight": 1.0,
            "density_penalty": 0.18,
            "angle_penalty": 0.08,
            "regret_bonus": 0.06,
            "cluster_mode": "none",
            "cluster_count": 1,
            "cluster_bonus": 0.16,
        },
        "local_search": {
            "two_opt_passes": 3,
            "two_opt_candidate_limit": 18,
            "use_three_opt": False,
            "three_opt_samples": 0,
            "or_opt_span": 2,
        },
        "perturbation": {
            "enabled": True,
            "mode": "double_bridge",
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
    if normalized in {"tsp_default", "nn_restarts_2opt"}:
        return default_heuristic_code()
    if normalized == "clustered_search":
        return """
def build_heuristic():
    return {
        "name": "clustered_search",
        "construction": {
            "seed_mode": "farthest_from_centroid",
            "candidate_limit": 12,
            "lookahead_limit": 4,
            "distance_weight": 1.0,
            "density_penalty": 0.28,
            "angle_penalty": 0.06,
            "regret_bonus": 0.08,
            "cluster_mode": "x_sweep",
            "cluster_count": 4,
            "cluster_bonus": 0.32,
        },
        "local_search": {
            "two_opt_passes": 4,
            "two_opt_candidate_limit": 18,
            "use_three_opt": True,
            "three_opt_samples": 6,
            "or_opt_span": 2,
        },
        "perturbation": {
            "enabled": True,
            "mode": "segment_reversal",
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
            "seed_mode": "nearest_centroid",
            "candidate_limit": 10,
            "lookahead_limit": 2,
            "distance_weight": 1.0,
            "density_penalty": 0.12,
            "angle_penalty": 0.1,
            "regret_bonus": 0.04,
            "cluster_mode": "radial",
            "cluster_count": 3,
            "cluster_bonus": 0.18,
        },
        "local_search": {
            "two_opt_passes": 3,
            "two_opt_candidate_limit": 14,
            "use_three_opt": False,
            "three_opt_samples": 0,
            "or_opt_span": 1,
        },
        "perturbation": {
            "enabled": True,
            "mode": "double_bridge",
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
    construction["seed_mode"] = _enum(str(construction.get("seed_mode", "")), {"farthest_from_centroid", "nearest_centroid", "lowest_x", "highest_y"}, "farthest_from_centroid")
    construction["candidate_limit"] = _bounded_int(construction.get("candidate_limit", 14), 4, 40)
    construction["lookahead_limit"] = _bounded_int(construction.get("lookahead_limit", 3), 1, 8)
    construction["distance_weight"] = _bounded_float(construction.get("distance_weight", 1.0), 0.4, 2.5)
    construction["density_penalty"] = _bounded_float(construction.get("density_penalty", 0.18), 0.0, 1.2)
    construction["angle_penalty"] = _bounded_float(construction.get("angle_penalty", 0.08), 0.0, 1.0)
    construction["regret_bonus"] = _bounded_float(construction.get("regret_bonus", 0.06), 0.0, 1.0)
    construction["cluster_mode"] = _enum(str(construction.get("cluster_mode", "")), {"none", "x_sweep", "y_sweep", "radial"}, "none")
    construction["cluster_count"] = _bounded_int(construction.get("cluster_count", 1), 1, 6)
    construction["cluster_bonus"] = _bounded_float(construction.get("cluster_bonus", 0.16), 0.0, 1.0)
    if construction["cluster_mode"] == "none":
        construction["cluster_count"] = 1

    local_search = merged["local_search"]
    local_search["two_opt_passes"] = _bounded_int(local_search.get("two_opt_passes", 3), 1, 8)
    local_search["two_opt_candidate_limit"] = _bounded_int(local_search.get("two_opt_candidate_limit", 18), 6, 40)
    local_search["use_three_opt"] = bool(local_search.get("use_three_opt", False))
    local_search["three_opt_samples"] = _bounded_int(local_search.get("three_opt_samples", 0), 0, 20)
    local_search["or_opt_span"] = _bounded_int(local_search.get("or_opt_span", 2), 1, 3)
    if not local_search["use_three_opt"]:
        local_search["three_opt_samples"] = 0

    perturbation = merged["perturbation"]
    perturbation["enabled"] = bool(perturbation.get("enabled", True))
    perturbation["mode"] = _enum(str(perturbation.get("mode", "")), {"double_bridge", "segment_reversal", "shuffle_window"}, "double_bridge")
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "construction_cost": self.construction_cost,
            "final_cost": self.final_cost,
            "two_opt_gain": self.two_opt_gain,
            "three_opt_gain": self.three_opt_gain,
            "restart_gain": self.restart_gain,
            "crossings_before": self.crossings_before,
            "crossings_after": self.crossings_after,
            "candidate_limit": self.candidate_limit,
            "cluster_count": self.cluster_count,
            "perturbation_attempts": self.perturbation_attempts,
            "perturbation_accepts": self.perturbation_accepts,
            "mean_edge_length": round(self.mean_edge_length, 4),
            "edge_length_cv": round(self.edge_length_cv, 4),
        }


def solve_instance(instance: TSPInstance, spec: dict[str, Any], *, seed: int = 0) -> dict[str, Any]:
    spec = canonicalize_heuristic_spec(spec)
    matrix = build_distance_matrix(instance)
    densities = [_node_density(matrix, node) for node in range(instance.dimension)]
    nearest = _nearest_candidates(matrix, max(spec["construction"]["candidate_limit"], spec["local_search"]["two_opt_candidate_limit"]))
    clusters = _cluster_labels(instance, spec["construction"]["cluster_mode"], spec["construction"]["cluster_count"])
    seed_nodes = _seed_candidates(instance, matrix, spec["construction"]["seed_mode"])

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
    current_cost: int | None = None
    for restart_index in range(spec["restart"]["restart_count"]):
        if restart_index == 0 or not spec["restart"]["use_perturbation_restarts"] or current_tour is None:
            seed_node = seed_nodes[restart_index % min(len(seed_nodes), spec["restart"]["seed_pool_size"])]
            candidate_tour = _construct_tour(instance, matrix, densities, nearest, clusters, spec, seed_node=seed_node)
        else:
            candidate_tour = _perturb_tour(list(current_tour), spec["perturbation"]["mode"], spec["perturbation"]["strength"], seed + restart_index)
        perturbation_attempts += spec["perturbation"]["attempts"] if restart_index > 0 else 0
        construction_cost = _tour_cost(matrix, candidate_tour)
        crossings_before = _count_crossings(instance, candidate_tour)
        improved_tour, two_opt_gain, three_opt_gain = _local_search(instance, matrix, nearest, candidate_tour, spec)
        improved_cost = _tour_cost(matrix, improved_tour)
        if best_cost is None:
            best_restart_gain = max(0, construction_cost - improved_cost)
        else:
            best_restart_gain = max(best_restart_gain, max(0, best_cost - improved_cost))

        if best_tour is None or _should_accept_restart(
            candidate_cost=improved_cost,
            incumbent_cost=best_cost,
            spec=spec,
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
            current_cost = improved_cost

    if best_tour is None or best_cost is None:
        raise RuntimeError("Heuristic engine failed to produce a tour.")

    edge_lengths = _edge_lengths(matrix, best_tour)
    mean_edge_length = sum(edge_lengths) / max(1, len(edge_lengths))
    variance = sum((item - mean_edge_length) ** 2 for item in edge_lengths) / max(1, len(edge_lengths))
    trace = SolveTrace(
        construction_cost=best_construction_cost,
        final_cost=best_cost,
        two_opt_gain=total_two_opt_gain,
        three_opt_gain=total_three_opt_gain,
        restart_gain=max(0, best_construction_cost - best_cost),
        crossings_before=best_crossings_before,
        crossings_after=_count_crossings(instance, best_tour),
        candidate_limit=spec["construction"]["candidate_limit"],
        cluster_count=spec["construction"]["cluster_count"] if spec["construction"]["cluster_mode"] != "none" else 1,
        perturbation_attempts=perturbation_attempts,
        perturbation_accepts=perturbation_accepts,
        mean_edge_length=mean_edge_length,
        edge_length_cv=(math.sqrt(variance) / mean_edge_length) if mean_edge_length > 0 else 0.0,
    )
    gap = ((best_cost - instance.best_known_cost) / instance.best_known_cost) if instance.best_known_cost else 0.0
    return {
        "instance": instance.to_dict(),
        "tour": list(best_tour),
        "cost": best_cost,
        "best_known_cost": instance.best_known_cost,
        "optimality_gap": round(gap, 6),
        "trace": trace.to_dict(),
        "heuristic_name": spec["name"],
    }


def aggregate_descriptor(results: list[dict[str, Any]]) -> dict[str, float]:
    if not results:
        return {key: 0.0 for key in (
            "mean_gap_ratio",
            "construction_gain_ratio",
            "two_opt_gain_ratio",
            "three_opt_gain_ratio",
            "restart_gain_ratio",
            "crossing_reduction_ratio",
            "candidate_pruning_ratio",
            "cluster_usage_ratio",
            "perturbation_accept_ratio",
            "tour_length_cv",
        )}

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
    }


def _construct_tour(
    instance: TSPInstance,
    matrix: list[list[int]],
    densities: list[float],
    nearest: list[list[int]],
    clusters: list[int],
    spec: dict[str, Any],
    *,
    seed_node: int,
) -> list[int]:
    n = instance.dimension
    visited = {seed_node}
    tour = [seed_node]
    current = seed_node
    last_vector: tuple[float, float] | None = None
    cluster_mode = spec["construction"]["cluster_mode"]
    cluster_bonus = float(spec["construction"]["cluster_bonus"])
    lookahead_limit = int(spec["construction"]["lookahead_limit"])
    while len(tour) < n:
        candidates = [node for node in nearest[current][: spec["construction"]["candidate_limit"]] if node not in visited]
        if not candidates:
            candidates = [node for node in range(n) if node not in visited]
        target_cluster = _dominant_remaining_cluster(tour, visited, clusters) if cluster_mode != "none" else None
        best_node = min(
            candidates,
            key=lambda node: _candidate_score(
                instance=instance,
                matrix=matrix,
                densities=densities,
                nearest=nearest,
                current=current,
                candidate=node,
                visited=visited,
                last_vector=last_vector,
                clusters=clusters,
                target_cluster=target_cluster,
                cluster_bonus=cluster_bonus,
                lookahead_limit=lookahead_limit,
                spec=spec,
            ),
        )
        previous = instance.coordinates[current]
        current_point = instance.coordinates[best_node]
        last_vector = (current_point[0] - previous[0], current_point[1] - previous[1])
        tour.append(best_node)
        visited.add(best_node)
        current = best_node
    return tour


def _candidate_score(
    *,
    instance: TSPInstance,
    matrix: list[list[int]],
    densities: list[float],
    nearest: list[list[int]],
    current: int,
    candidate: int,
    visited: set[int],
    last_vector: tuple[float, float] | None,
    clusters: list[int],
    target_cluster: int | None,
    cluster_bonus: float,
    lookahead_limit: int,
    spec: dict[str, Any],
) -> float:
    construction = spec["construction"]
    base_distance = float(matrix[current][candidate]) * float(construction["distance_weight"])
    density = densities[candidate]
    density_penalty = float(construction["density_penalty"]) * density
    angle_penalty = 0.0
    if last_vector is not None:
        angle_penalty = float(construction["angle_penalty"]) * _turn_penalty(instance.coordinates[current], instance.coordinates[candidate], last_vector)
    lookahead = _lookahead_score(matrix, nearest, candidate, visited, lookahead_limit)
    score = base_distance + density_penalty + angle_penalty - (float(construction["regret_bonus"]) * lookahead)
    if target_cluster is not None and clusters[candidate] == target_cluster:
        score -= cluster_bonus * max(1.0, base_distance * 0.15)
    return score


def _lookahead_score(matrix: list[list[int]], nearest: list[list[int]], candidate: int, visited: set[int], lookahead_limit: int) -> float:
    unseen = [node for node in nearest[candidate][: lookahead_limit + 1] if node not in visited and node != candidate][:lookahead_limit]
    if not unseen:
        return 0.0
    return 1.0 / max(1.0, sum(matrix[candidate][node] for node in unseen) / len(unseen))


def _node_density(matrix: list[list[int]], node: int, *, limit: int = 4) -> float:
    distances = sorted(matrix[node][other] for other in range(len(matrix)) if other != node)
    return sum(distances[:limit]) / max(1.0, len(distances[:limit]) or 1.0)


def _turn_penalty(current: tuple[float, float], candidate: tuple[float, float], last_vector: tuple[float, float]) -> float:
    next_vector = (candidate[0] - current[0], candidate[1] - current[1])
    left_norm = math.sqrt((last_vector[0] * last_vector[0]) + (last_vector[1] * last_vector[1])) or 1.0
    right_norm = math.sqrt((next_vector[0] * next_vector[0]) + (next_vector[1] * next_vector[1])) or 1.0
    cosine = ((last_vector[0] * next_vector[0]) + (last_vector[1] * next_vector[1])) / (left_norm * right_norm)
    return max(0.0, 1.0 - cosine)


def _local_search(
    instance: TSPInstance,
    matrix: list[list[int]],
    nearest: list[list[int]],
    tour: list[int],
    spec: dict[str, Any],
) -> tuple[list[int], int, int]:
    current = list(tour)
    starting_cost = _tour_cost(matrix, current)
    current = _apply_two_opt(matrix, nearest, current, spec["local_search"]["two_opt_passes"], spec["local_search"]["two_opt_candidate_limit"])
    after_two_opt = _tour_cost(matrix, current)
    current = _apply_or_opt(matrix, current, spec["local_search"]["or_opt_span"])
    after_or_opt = _tour_cost(matrix, current)
    current = _apply_three_opt(instance, matrix, current, spec["local_search"]["three_opt_samples"]) if spec["local_search"]["use_three_opt"] else current
    final_cost = _tour_cost(matrix, current)
    two_opt_gain = max(0, starting_cost - after_or_opt)
    three_opt_gain = max(0, after_or_opt - final_cost)
    return current, two_opt_gain, three_opt_gain


def _apply_two_opt(matrix: list[list[int]], nearest: list[list[int]], tour: list[int], passes: int, candidate_limit: int) -> list[int]:
    n = len(tour)
    current = list(tour)
    for _ in range(passes):
        improved = False
        position = {node: index for index, node in enumerate(current)}
        for i in range(n - 1):
            a = current[i]
            b = current[(i + 1) % n]
            for candidate in nearest[a][:candidate_limit]:
                j = position.get(candidate)
                if j is None or abs(i - j) <= 1 or (i == 0 and j == n - 1):
                    continue
                c = current[j]
                d = current[(j + 1) % n]
                delta = (matrix[a][c] + matrix[b][d]) - (matrix[a][b] + matrix[c][d])
                if delta < 0:
                    left = min(i + 1, j)
                    right = max(i + 1, j)
                    current[left:right + 1] = reversed(current[left:right + 1])
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break
    return current


def _apply_or_opt(matrix: list[list[int]], tour: list[int], span: int) -> list[int]:
    current = list(tour)
    n = len(current)
    if n > 80 or span <= 0:
        return current
    for window in range(span, 0, -1):
        improved = False
        for start in range(0, min(n - window, 10)):
            segment = current[start : start + window]
            remaining = current[:start] + current[start + window :]
            base_cost = _tour_cost(matrix, current)
            best_cost = base_cost
            best_tour = current
            candidate_positions = {1, len(remaining) // 3, (2 * len(remaining)) // 3, max(1, len(remaining) - 1)}
            for insert_at in sorted(position for position in candidate_positions if 0 < position < len(remaining)):
                candidate = remaining[:insert_at] + segment + remaining[insert_at:]
                candidate_cost = _tour_cost(matrix, candidate)
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


def _apply_three_opt(instance: TSPInstance, matrix: list[list[int]], tour: list[int], samples: int) -> list[int]:
    if samples <= 0 or len(tour) > 120:
        return tour
    current = list(tour)
    n = len(current)
    best_cost = _tour_cost(matrix, current)
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
            candidate_cost = _tour_cost(matrix, candidate)
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
    cut1 = 1 + (offset % max(2, n - 6))
    cut2 = cut1 + max(2, n // 6)
    cut3 = min(n - 2, cut2 + max(2, n // 6))
    cut4 = min(n, cut3 + max(2, n // 6))
    return current[:cut1] + current[cut3:cut4] + current[cut2:cut3] + current[cut1:cut2] + current[cut4:]


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


def _seed_candidates(instance: TSPInstance, matrix: list[list[int]], seed_mode: str) -> list[int]:
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
    labels: list[int] = []
    if mode == "x_sweep":
        ordered = sorted(range(len(xs)), key=lambda index: (xs[index], ys[index]))
    elif mode == "y_sweep":
        ordered = sorted(range(len(xs)), key=lambda index: (ys[index], xs[index]))
    else:
        ordered = sorted(
            range(len(xs)),
            key=lambda index: math.atan2(ys[index] - centroid_y, xs[index] - centroid_x),
        )
    bucket_size = max(1, math.ceil(len(ordered) / cluster_count))
    raw = [0 for _ in ordered]
    for position, node in enumerate(ordered):
        raw[node] = min(cluster_count - 1, position // bucket_size)
    labels.extend(raw)
    return labels


def _dominant_remaining_cluster(tour: list[int], visited: set[int], clusters: list[int]) -> int | None:
    counts: dict[int, int] = {}
    for node, cluster in enumerate(clusters):
        if node in visited:
            continue
        counts[cluster] = counts.get(cluster, 0) + 1
    if not counts:
        return None
    current_cluster = clusters[tour[-1]]
    if counts.get(current_cluster):
        return current_cluster
    return max(counts.items(), key=lambda item: item[1])[0]


def _count_crossings(instance: TSPInstance, tour: list[int]) -> int:
    def ccw(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> bool:
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

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
            if ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d):
                crossings += 1
    return crossings


def _edge_lengths(matrix: list[list[int]], tour: list[int]) -> list[int]:
    return [matrix[tour[index]][tour[(index + 1) % len(tour)]] for index in range(len(tour))]


def _tour_cost(matrix: list[list[int]], tour: list[int]) -> int:
    return sum(matrix[tour[index]][tour[(index + 1) % len(tour)]] for index in range(len(tour)))


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
