from __future__ import annotations

from dataclasses import dataclass
import copy
import math
from typing import Any

from .benchmark import ATSPInstance


DEFAULT_HEURISTIC_SPEC: dict[str, Any] = {
    "name": "atsp_greedy_restarts",
    "construction": {
        "seed_mode": "highest_in_minus_out",
        "candidate_limit": 14,
        "lookahead_limit": 3,
        "distance_weight": 1.0,
        "outbound_density_penalty": 0.12,
        "inbound_density_penalty": 0.1,
        "asymmetry_bonus": 0.18,
        "regret_bonus": 0.08,
        "cluster_mode": "none",
        "cluster_count": 1,
        "cluster_bonus": 0.15,
    },
    "local_search": {
        "two_opt_passes": 3,
        "two_opt_candidate_limit": 18,
        "use_three_opt": False,
        "three_opt_samples": 0,
        "relocate_span": 2,
    },
    "perturbation": {
        "enabled": True,
        "mode": "segment_reversal",
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
        "name": "atsp_greedy_restarts",
        "construction": {
            "seed_mode": "highest_in_minus_out",
            "candidate_limit": 14,
            "lookahead_limit": 3,
            "distance_weight": 1.0,
            "outbound_density_penalty": 0.12,
            "inbound_density_penalty": 0.1,
            "asymmetry_bonus": 0.18,
            "regret_bonus": 0.08,
            "cluster_mode": "none",
            "cluster_count": 1,
            "cluster_bonus": 0.15,
        },
        "local_search": {
            "two_opt_passes": 3,
            "two_opt_candidate_limit": 18,
            "use_three_opt": False,
            "three_opt_samples": 0,
            "relocate_span": 2,
        },
        "perturbation": {
            "enabled": True,
            "mode": "segment_reversal",
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
    if normalized in {"atsp_default", "atsp_greedy_restarts"}:
        return default_heuristic_code()
    if normalized == "asymmetry_hunter":
        return """
def build_heuristic():
    return {
        "name": "asymmetry_hunter",
        "construction": {
            "seed_mode": "highest_asymmetry",
            "candidate_limit": 12,
            "lookahead_limit": 4,
            "distance_weight": 1.0,
            "outbound_density_penalty": 0.08,
            "inbound_density_penalty": 0.14,
            "asymmetry_bonus": 0.26,
            "regret_bonus": 0.12,
            "cluster_mode": "row_bands",
            "cluster_count": 4,
            "cluster_bonus": 0.22,
        },
        "local_search": {
            "two_opt_passes": 4,
            "two_opt_candidate_limit": 18,
            "use_three_opt": True,
            "three_opt_samples": 7,
            "relocate_span": 2,
        },
        "perturbation": {
            "enabled": True,
            "mode": "double_bridge",
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
            "seed_mode": "lowest_row_mean",
            "candidate_limit": 10,
            "lookahead_limit": 2,
            "distance_weight": 1.0,
            "outbound_density_penalty": 0.1,
            "inbound_density_penalty": 0.08,
            "asymmetry_bonus": 0.14,
            "regret_bonus": 0.05,
            "cluster_mode": "hub_groups",
            "cluster_count": 3,
            "cluster_bonus": 0.16,
        },
        "local_search": {
            "two_opt_passes": 3,
            "two_opt_candidate_limit": 14,
            "use_three_opt": False,
            "three_opt_samples": 0,
            "relocate_span": 1,
        },
        "perturbation": {
            "enabled": True,
            "mode": "segment_reversal",
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
        {"highest_in_minus_out", "lowest_row_mean", "lowest_column_mean", "highest_asymmetry"},
        "highest_in_minus_out",
    )
    construction["candidate_limit"] = _bounded_int(construction.get("candidate_limit", 14), 4, 40)
    construction["lookahead_limit"] = _bounded_int(construction.get("lookahead_limit", 3), 1, 8)
    construction["distance_weight"] = _bounded_float(construction.get("distance_weight", 1.0), 0.4, 2.5)
    construction["outbound_density_penalty"] = _bounded_float(construction.get("outbound_density_penalty", 0.12), 0.0, 1.2)
    construction["inbound_density_penalty"] = _bounded_float(construction.get("inbound_density_penalty", 0.1), 0.0, 1.2)
    construction["asymmetry_bonus"] = _bounded_float(construction.get("asymmetry_bonus", 0.18), 0.0, 1.2)
    construction["regret_bonus"] = _bounded_float(construction.get("regret_bonus", 0.08), 0.0, 1.0)
    construction["cluster_mode"] = _enum(
        str(construction.get("cluster_mode", "")),
        {"none", "row_bands", "column_bands", "hub_groups"},
        "none",
    )
    construction["cluster_count"] = _bounded_int(construction.get("cluster_count", 1), 1, 6)
    construction["cluster_bonus"] = _bounded_float(construction.get("cluster_bonus", 0.15), 0.0, 1.0)
    if construction["cluster_mode"] == "none":
        construction["cluster_count"] = 1

    local_search = merged["local_search"]
    local_search["two_opt_passes"] = _bounded_int(local_search.get("two_opt_passes", 3), 1, 8)
    local_search["two_opt_candidate_limit"] = _bounded_int(local_search.get("two_opt_candidate_limit", 18), 6, 40)
    local_search["use_three_opt"] = bool(local_search.get("use_three_opt", False))
    local_search["three_opt_samples"] = _bounded_int(local_search.get("three_opt_samples", 0), 0, 20)
    local_search["relocate_span"] = _bounded_int(local_search.get("relocate_span", 2), 1, 3)
    if not local_search["use_three_opt"]:
        local_search["three_opt_samples"] = 0

    perturbation = merged["perturbation"]
    perturbation["enabled"] = bool(perturbation.get("enabled", True))
    perturbation["mode"] = _enum(
        str(perturbation.get("mode", "")),
        {"double_bridge", "segment_reversal", "shuffle_window"},
        "segment_reversal",
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
    relocate_gain: int
    three_opt_gain: int
    restart_gain: int
    candidate_limit: int
    cluster_count: int
    perturbation_attempts: int
    perturbation_accepts: int
    mean_arc_cost: float
    arc_cost_cv: float
    asymmetry_capture: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "construction_cost": self.construction_cost,
            "final_cost": self.final_cost,
            "two_opt_gain": self.two_opt_gain,
            "relocate_gain": self.relocate_gain,
            "three_opt_gain": self.three_opt_gain,
            "restart_gain": self.restart_gain,
            "candidate_limit": self.candidate_limit,
            "cluster_count": self.cluster_count,
            "perturbation_attempts": self.perturbation_attempts,
            "perturbation_accepts": self.perturbation_accepts,
            "mean_arc_cost": round(self.mean_arc_cost, 4),
            "arc_cost_cv": round(self.arc_cost_cv, 4),
            "asymmetry_capture": round(self.asymmetry_capture, 4),
        }


def solve_instance(instance: ATSPInstance, spec: dict[str, Any], *, seed: int = 0) -> dict[str, Any]:
    spec = canonicalize_heuristic_spec(spec)
    matrix = instance.distance_matrix
    outgoing_means = [_node_outgoing_mean(matrix, node) for node in range(instance.dimension)]
    incoming_means = [_node_incoming_mean(matrix, node) for node in range(instance.dimension)]
    asymmetry_scores = [_node_asymmetry(matrix, node) for node in range(instance.dimension)]
    nearest = _nearest_candidates(matrix, max(spec["construction"]["candidate_limit"], spec["local_search"]["two_opt_candidate_limit"]))
    clusters = _cluster_labels(instance, spec["construction"]["cluster_mode"], spec["construction"]["cluster_count"], outgoing_means, incoming_means, asymmetry_scores)
    seed_nodes = _seed_candidates(instance, spec["construction"]["seed_mode"], outgoing_means, incoming_means, asymmetry_scores)

    best_tour: list[int] | None = None
    best_cost: int | None = None
    best_construction_cost = 0
    best_two_opt_gain = 0
    best_relocate_gain = 0
    best_three_opt_gain = 0
    perturbation_attempts = 0
    perturbation_accepts = 0
    current_tour: list[int] | None = None
    current_cost: int | None = None

    for restart_index in range(spec["restart"]["restart_count"]):
        if restart_index == 0 or not spec["restart"]["use_perturbation_restarts"] or current_tour is None:
            seed_node = seed_nodes[restart_index % min(len(seed_nodes), spec["restart"]["seed_pool_size"])]
            candidate_tour = _construct_tour(
                instance,
                matrix,
                nearest,
                outgoing_means,
                incoming_means,
                asymmetry_scores,
                clusters,
                spec,
                seed_node=seed_node,
            )
        else:
            candidate_tour = _perturb_tour(list(current_tour), spec["perturbation"]["mode"], spec["perturbation"]["strength"], seed + restart_index)
            perturbation_attempts += spec["perturbation"]["attempts"]
        construction_cost = _tour_cost(matrix, candidate_tour)
        improved_tour, two_opt_gain, relocate_gain, three_opt_gain = _local_search(matrix, nearest, candidate_tour, spec)
        improved_cost = _tour_cost(matrix, improved_tour)
        accepted = _should_accept_restart(
            candidate_cost=improved_cost,
            incumbent_cost=best_cost,
            spec=spec,
            restart_index=restart_index,
        )
        if accepted:
            if best_cost is not None and improved_cost > best_cost:
                perturbation_accepts += 1
            best_tour = improved_tour
            best_cost = improved_cost
            best_construction_cost = construction_cost
            best_two_opt_gain = two_opt_gain
            best_relocate_gain = relocate_gain
            best_three_opt_gain = three_opt_gain
            current_tour = improved_tour
            current_cost = improved_cost
        elif current_tour is None:
            current_tour = improved_tour
            current_cost = improved_cost

    if best_tour is None or best_cost is None:
        raise RuntimeError("Heuristic engine failed to produce a tour.")

    arc_costs = _edge_costs(matrix, best_tour)
    mean_arc_cost = sum(arc_costs) / max(1, len(arc_costs))
    variance = sum((item - mean_arc_cost) ** 2 for item in arc_costs) / max(1, len(arc_costs))
    trace = SolveTrace(
        construction_cost=best_construction_cost,
        final_cost=best_cost,
        two_opt_gain=best_two_opt_gain,
        relocate_gain=best_relocate_gain,
        three_opt_gain=best_three_opt_gain,
        restart_gain=max(0, best_construction_cost - best_cost),
        candidate_limit=spec["construction"]["candidate_limit"],
        cluster_count=spec["construction"]["cluster_count"] if spec["construction"]["cluster_mode"] != "none" else 1,
        perturbation_attempts=perturbation_attempts,
        perturbation_accepts=perturbation_accepts,
        mean_arc_cost=mean_arc_cost,
        arc_cost_cv=(math.sqrt(variance) / mean_arc_cost) if mean_arc_cost > 0 else 0.0,
        asymmetry_capture=_tour_asymmetry_capture(matrix, best_tour),
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
        return {
            "mean_gap_ratio": 0.0,
            "construction_gain_ratio": 0.0,
            "two_opt_gain_ratio": 0.0,
            "relocate_gain_ratio": 0.0,
            "three_opt_gain_ratio": 0.0,
            "restart_gain_ratio": 0.0,
            "candidate_pruning_ratio": 0.0,
            "cluster_usage_ratio": 0.0,
            "perturbation_accept_ratio": 0.0,
            "arc_cost_cv": 0.0,
            "asymmetry_capture_ratio": 0.0,
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
    relocate_gain = sum(
        max(0.0, float(item["trace"]["relocate_gain"]) / max(1.0, float(item["trace"]["construction_cost"])))
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
    tour_cv = sum(float(item["trace"]["arc_cost_cv"]) for item in results) / len(results)
    asymmetry_capture = sum(float(item["trace"]["asymmetry_capture"]) for item in results) / len(results)
    return {
        "mean_gap_ratio": round(mean_gap, 6),
        "construction_gain_ratio": round(construction_gain, 6),
        "two_opt_gain_ratio": round(two_opt_gain, 6),
        "relocate_gain_ratio": round(relocate_gain, 6),
        "three_opt_gain_ratio": round(three_opt_gain, 6),
        "restart_gain_ratio": round(restart_gain, 6),
        "candidate_pruning_ratio": round(candidate_pruning, 6),
        "cluster_usage_ratio": round(cluster_usage, 6),
        "perturbation_accept_ratio": round(perturbation_accept, 6),
        "arc_cost_cv": round(tour_cv, 6),
        "asymmetry_capture_ratio": round(asymmetry_capture, 6),
    }


def _construct_tour(
    instance: ATSPInstance,
    matrix: list[list[int]],
    nearest: list[list[int]],
    outgoing_means: list[float],
    incoming_means: list[float],
    asymmetry_scores: list[float],
    clusters: list[int],
    spec: dict[str, Any],
    *,
    seed_node: int,
) -> list[int]:
    n = instance.dimension
    visited = {seed_node}
    tour = [seed_node]
    current = seed_node
    cluster_mode = spec["construction"]["cluster_mode"]
    cluster_bonus = float(spec["construction"]["cluster_bonus"])
    lookahead_limit = int(spec["construction"]["lookahead_limit"])
    while len(tour) < n:
        candidates = [node for node in nearest[current][: spec["construction"]["candidate_limit"]] if node not in visited]
        if not candidates:
            candidates = [node for node in range(n) if node not in visited]
        target_cluster = _dominant_remaining_cluster(visited, clusters) if cluster_mode != "none" else None
        best_node = min(
            candidates,
            key=lambda node: _candidate_score(
                matrix=matrix,
                nearest=nearest,
                current=current,
                candidate=node,
                visited=visited,
                outgoing_means=outgoing_means,
                incoming_means=incoming_means,
                asymmetry_scores=asymmetry_scores,
                clusters=clusters,
                target_cluster=target_cluster,
                cluster_bonus=cluster_bonus,
                lookahead_limit=lookahead_limit,
                spec=spec,
            ),
        )
        tour.append(best_node)
        visited.add(best_node)
        current = best_node
    return tour


def _candidate_score(
    *,
    matrix: list[list[int]],
    nearest: list[list[int]],
    current: int,
    candidate: int,
    visited: set[int],
    outgoing_means: list[float],
    incoming_means: list[float],
    asymmetry_scores: list[float],
    clusters: list[int],
    target_cluster: int | None,
    cluster_bonus: float,
    lookahead_limit: int,
    spec: dict[str, Any],
) -> float:
    construction = spec["construction"]
    forward = float(matrix[current][candidate])
    reverse = float(matrix[candidate][current])
    base_distance = forward * float(construction["distance_weight"])
    outbound_penalty = float(construction["outbound_density_penalty"]) * outgoing_means[candidate]
    inbound_penalty = float(construction["inbound_density_penalty"]) * incoming_means[candidate]
    asymmetry_bonus = float(construction["asymmetry_bonus"]) * max(0.0, reverse - forward) / max(1.0, forward)
    lookahead = _lookahead_score(matrix, nearest, candidate, visited, lookahead_limit)
    score = base_distance + outbound_penalty + inbound_penalty - asymmetry_bonus - (float(construction["regret_bonus"]) * lookahead)
    score -= 0.1 * asymmetry_scores[candidate]
    if target_cluster is not None and clusters[candidate] == target_cluster:
        score -= cluster_bonus * max(1.0, base_distance * 0.12)
    return score


def _lookahead_score(matrix: list[list[int]], nearest: list[list[int]], candidate: int, visited: set[int], lookahead_limit: int) -> float:
    unseen = [node for node in nearest[candidate][: lookahead_limit + 1] if node not in visited and node != candidate][:lookahead_limit]
    if not unseen:
        return 0.0
    mean_cost = sum(matrix[candidate][node] for node in unseen) / len(unseen)
    return 1.0 / max(1.0, mean_cost)


def _local_search(
    matrix: list[list[int]],
    nearest: list[list[int]],
    tour: list[int],
    spec: dict[str, Any],
) -> tuple[list[int], int, int, int]:
    current = list(tour)
    starting_cost = _tour_cost(matrix, current)
    current = _apply_two_opt(matrix, nearest, current, spec["local_search"]["two_opt_passes"], spec["local_search"]["two_opt_candidate_limit"])
    after_two_opt = _tour_cost(matrix, current)
    current = _apply_relocate(matrix, current, spec["local_search"]["relocate_span"])
    after_relocate = _tour_cost(matrix, current)
    current = _apply_three_opt(matrix, current, spec["local_search"]["three_opt_samples"]) if spec["local_search"]["use_three_opt"] else current
    final_cost = _tour_cost(matrix, current)
    return (
        current,
        max(0, starting_cost - after_two_opt),
        max(0, after_two_opt - after_relocate),
        max(0, after_relocate - final_cost),
    )


def _apply_two_opt(matrix: list[list[int]], nearest: list[list[int]], tour: list[int], passes: int, candidate_limit: int) -> list[int]:
    n = len(tour)
    current = list(tour)
    for _ in range(passes):
        improved = False
        position = {node: index for index, node in enumerate(current)}
        for i in range(n - 1):
            a = current[i]
            for candidate in nearest[a][:candidate_limit]:
                j = position.get(candidate)
                if j is None or abs(i - j) <= 1 or (i == 0 and j == n - 1):
                    continue
                left = min(i + 1, j)
                right = max(i + 1, j)
                candidate_tour = current[:left] + list(reversed(current[left : right + 1])) + current[right + 1 :]
                if _tour_cost(matrix, candidate_tour) < _tour_cost(matrix, current):
                    current = candidate_tour
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break
    return current


def _apply_relocate(matrix: list[list[int]], tour: list[int], span: int) -> list[int]:
    current = list(tour)
    n = len(current)
    if n > 90 or span <= 0:
        return current
    for window in range(span, 0, -1):
        improved = False
        for start in range(0, min(n - window + 1, 12)):
            segment = current[start : start + window]
            remaining = current[:start] + current[start + window :]
            best_cost = _tour_cost(matrix, current)
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


def _apply_three_opt(matrix: list[list[int]], tour: list[int], samples: int) -> list[int]:
    if samples <= 0 or len(tour) > 110:
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
    if mode == "shuffle_window":
        start = 1 + (offset % max(2, n - 5))
        window = current[start : start + 4]
        current[start : start + 4] = window[2:] + window[:2]
        return current
    if mode == "double_bridge":
        cut1 = 1 + (offset % max(2, n - 6))
        cut2 = cut1 + max(2, n // 6)
        cut3 = min(n - 2, cut2 + max(2, n // 6))
        cut4 = min(n, cut3 + max(2, n // 6))
        return current[:cut1] + current[cut3:cut4] + current[cut2:cut3] + current[cut1:cut2] + current[cut4:]
    for attempt in range(strength):
        start = 1 + ((offset + (attempt * 3)) % max(2, n - 4))
        end = min(n - 1, start + 2 + attempt)
        current[start:end] = reversed(current[start:end])
    return current


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


def _seed_candidates(
    instance: ATSPInstance,
    seed_mode: str,
    outgoing_means: list[float],
    incoming_means: list[float],
    asymmetry_scores: list[float],
) -> list[int]:
    nodes = list(range(instance.dimension))
    if seed_mode == "lowest_row_mean":
        return sorted(nodes, key=lambda node: (outgoing_means[node], -asymmetry_scores[node]))
    if seed_mode == "lowest_column_mean":
        return sorted(nodes, key=lambda node: (incoming_means[node], -asymmetry_scores[node]))
    if seed_mode == "highest_asymmetry":
        return sorted(nodes, key=lambda node: (-asymmetry_scores[node], outgoing_means[node]))
    return sorted(nodes, key=lambda node: (-(incoming_means[node] - outgoing_means[node]), -asymmetry_scores[node]))


def _nearest_candidates(matrix: list[list[int]], limit: int) -> list[list[int]]:
    candidates: list[list[int]] = []
    for row_index, row in enumerate(matrix):
        ordering = sorted((distance, column_index) for column_index, distance in enumerate(row) if column_index != row_index)
        candidates.append([column_index for _, column_index in ordering[:limit]])
    return candidates


def _cluster_labels(
    instance: ATSPInstance,
    mode: str,
    cluster_count: int,
    outgoing_means: list[float],
    incoming_means: list[float],
    asymmetry_scores: list[float],
) -> list[int]:
    if mode == "none" or cluster_count <= 1:
        return [0 for _ in range(instance.dimension)]
    nodes = list(range(instance.dimension))
    if mode == "row_bands":
        ordered = sorted(nodes, key=lambda node: (outgoing_means[node], incoming_means[node]))
    elif mode == "column_bands":
        ordered = sorted(nodes, key=lambda node: (incoming_means[node], outgoing_means[node]))
    else:
        ordered = sorted(nodes, key=lambda node: (outgoing_means[node] + incoming_means[node], -asymmetry_scores[node]))
    bucket_size = max(1, math.ceil(len(ordered) / cluster_count))
    labels = [0 for _ in ordered]
    for position, node in enumerate(ordered):
        labels[node] = min(cluster_count - 1, position // bucket_size)
    return labels


def _dominant_remaining_cluster(visited: set[int], clusters: list[int]) -> int | None:
    counts: dict[int, int] = {}
    for node, cluster in enumerate(clusters):
        if node in visited:
            continue
        counts[cluster] = counts.get(cluster, 0) + 1
    if not counts:
        return None
    return max(counts.items(), key=lambda item: item[1])[0]


def _tour_asymmetry_capture(matrix: list[list[int]], tour: list[int]) -> float:
    capture = 0.0
    for index, node in enumerate(tour):
        nxt = tour[(index + 1) % len(tour)]
        forward = float(matrix[node][nxt])
        reverse = float(matrix[nxt][node])
        capture += max(0.0, reverse - forward) / max(1.0, max(forward, reverse))
    return capture / max(1, len(tour))


def _edge_costs(matrix: list[list[int]], tour: list[int]) -> list[int]:
    return [matrix[tour[index]][tour[(index + 1) % len(tour)]] for index in range(len(tour))]


def _tour_cost(matrix: list[list[int]], tour: list[int]) -> int:
    return sum(matrix[tour[index]][tour[(index + 1) % len(tour)]] for index in range(len(tour)))


def _node_outgoing_mean(matrix: list[list[int]], node: int) -> float:
    values = [distance for index, distance in enumerate(matrix[node]) if index != node]
    return sum(values) / max(1, len(values))


def _node_incoming_mean(matrix: list[list[int]], node: int) -> float:
    values = [row[node] for row_index, row in enumerate(matrix) if row_index != node]
    return sum(values) / max(1, len(values))


def _node_asymmetry(matrix: list[list[int]], node: int) -> float:
    values = [
        abs(float(matrix[node][other]) - float(matrix[other][node])) / max(1.0, (float(matrix[node][other]) + float(matrix[other][node])) * 0.5)
        for other in range(len(matrix))
        if other != node
    ]
    return sum(values) / max(1, len(values))


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
