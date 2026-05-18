from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .heuristic_engine import canonicalize_heuristic_spec, solve_instance
from .instance_features import descriptor_distance, descriptor_vector, ensure_instance_descriptors


BASELINE_PORTFOLIO: dict[str, dict[str, Any]] = {
    "baseline_default": {
        "name": "baseline_default",
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
    },
    "baseline_clustered": {
        "name": "baseline_clustered",
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
    },
    "baseline_compact": {
        "name": "baseline_compact",
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
    },
    "baseline_sparse_three_opt": {
        "name": "baseline_sparse_three_opt",
        "construction": {
            "seed_mode": "lowest_x",
            "candidate_limit": 9,
            "lookahead_limit": 2,
            "distance_weight": 1.05,
            "density_penalty": 0.06,
            "angle_penalty": 0.12,
            "regret_bonus": 0.02,
            "cluster_mode": "none",
            "cluster_count": 1,
            "cluster_bonus": 0.0,
        },
        "local_search": {
            "two_opt_passes": 2,
            "two_opt_candidate_limit": 12,
            "use_three_opt": True,
            "three_opt_samples": 4,
            "or_opt_span": 1,
        },
        "perturbation": {
            "enabled": False,
            "mode": "double_bridge",
            "strength": 1,
            "attempts": 1,
        },
        "restart": {
            "restart_count": 2,
            "seed_pool_size": 2,
            "use_perturbation_restarts": False,
        },
        "acceptance": {
            "mode": "improving_only",
            "worse_acceptance_threshold": 0.0,
            "annealing_temperature": 0.0,
        },
    },
    "baseline_restart_threshold": {
        "name": "baseline_restart_threshold",
        "construction": {
            "seed_mode": "highest_y",
            "candidate_limit": 16,
            "lookahead_limit": 3,
            "distance_weight": 0.95,
            "density_penalty": 0.22,
            "angle_penalty": 0.04,
            "regret_bonus": 0.07,
            "cluster_mode": "y_sweep",
            "cluster_count": 3,
            "cluster_bonus": 0.2,
        },
        "local_search": {
            "two_opt_passes": 3,
            "two_opt_candidate_limit": 16,
            "use_three_opt": False,
            "three_opt_samples": 0,
            "or_opt_span": 3,
        },
        "perturbation": {
            "enabled": True,
            "mode": "shuffle_window",
            "strength": 2,
            "attempts": 2,
        },
        "restart": {
            "restart_count": 6,
            "seed_pool_size": 4,
            "use_perturbation_restarts": True,
        },
        "acceptance": {
            "mode": "threshold",
            "worse_acceptance_threshold": 0.006,
            "annealing_temperature": 0.0,
        },
    },
}


@dataclass(frozen=True)
class DifficultyReference:
    instance_name: str
    family: str
    descriptor_vector: dict[str, float]
    baseline_results: dict[str, dict[str, Any]]
    baseline_mean_gap: float
    baseline_best_gap: float
    baseline_gap_std: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "instance_name": self.instance_name,
            "family": self.family,
            "descriptor_vector": dict(self.descriptor_vector),
            "baseline_results": dict(self.baseline_results),
            "baseline_mean_gap": round(self.baseline_mean_gap, 6),
            "baseline_best_gap": round(self.baseline_best_gap, 6),
            "baseline_gap_std": round(self.baseline_gap_std, 6),
        }


@dataclass
class DifficultyModel:
    references: list[DifficultyReference]
    neighbor_count: int = 3

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_count": len(self.references),
            "neighbor_count": int(self.neighbor_count),
            "references": [reference.to_dict() for reference in self.references],
        }


def build_difficulty_model(instances: list[Any], *, seed_base: int = 0) -> DifficultyModel:
    references: list[DifficultyReference] = []
    for index, instance in enumerate(instances):
        ensure_instance_descriptors(instance)
        baseline_results = evaluate_baseline_portfolio(instance, seed_base=seed_base + (index * 10_000))
        gap_values = [float(item["optimality_gap"]) for item in baseline_results.values()]
        references.append(
            DifficultyReference(
                instance_name=str(instance.name),
                family=str(instance.family),
                descriptor_vector=descriptor_vector(instance),
                baseline_results=baseline_results,
                baseline_mean_gap=sum(gap_values) / len(gap_values) if gap_values else 0.0,
                baseline_best_gap=min(gap_values) if gap_values else 0.0,
                baseline_gap_std=_population_std(gap_values),
            )
        )
    neighbor_count = min(3, max(1, len(references)))
    return DifficultyModel(references=references, neighbor_count=neighbor_count)


def evaluate_baseline_portfolio(instance: Any, *, seed_base: int = 0) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for index, (name, spec) in enumerate(BASELINE_PORTFOLIO.items()):
        solved = solve_instance(instance, canonicalize_heuristic_spec(spec), seed=seed_base + (index * 101))
        results[name] = {
            "heuristic_name": name,
            "cost": int(solved["cost"]),
            "best_known_cost": int(solved["best_known_cost"]),
            "optimality_gap": round(float(solved["optimality_gap"]), 6),
        }
    return results


def expected_gap(model: DifficultyModel, instance: Any) -> float:
    ensure_instance_descriptors(instance)
    if not model.references:
        return 0.0
    matches = [reference for reference in model.references if reference.instance_name == str(getattr(instance, "name", ""))]
    if matches:
        return round(matches[0].baseline_mean_gap, 6)
    neighbors = sorted(
        model.references,
        key=lambda reference: descriptor_distance({"descriptors": reference.descriptor_vector}, instance),
    )[: max(1, model.neighbor_count)]
    weighted_sum = 0.0
    total_weight = 0.0
    for rank, reference in enumerate(neighbors):
        distance = max(1e-6, descriptor_distance({"descriptors": reference.descriptor_vector}, instance))
        weight = 1.0 / (distance + (0.15 * rank))
        weighted_sum += weight * reference.baseline_mean_gap
        total_weight += weight
    return round(weighted_sum / total_weight if total_weight > 0 else 0.0, 6)


def residual_failure_gap(model: DifficultyModel, instance: Any, observed_gap: float) -> float:
    return round(float(observed_gap) - float(expected_gap(model, instance)), 6)


def baseline_reference_summary(model: DifficultyModel) -> dict[str, Any]:
    if not model.references:
        return {
            "reference_count": 0,
            "mean_baseline_gap": 0.0,
            "mean_best_baseline_gap": 0.0,
            "mean_baseline_gap_std": 0.0,
        }
    return {
        "reference_count": len(model.references),
        "mean_baseline_gap": round(sum(reference.baseline_mean_gap for reference in model.references) / len(model.references), 6),
        "mean_best_baseline_gap": round(sum(reference.baseline_best_gap for reference in model.references) / len(model.references), 6),
        "mean_baseline_gap_std": round(sum(reference.baseline_gap_std for reference in model.references) / len(model.references), 6),
    }


def _population_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return variance ** 0.5
