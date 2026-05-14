from __future__ import annotations

import math


DESCRIPTOR_KEYS = (
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
)


def behavioral_distance(left: dict[str, float] | None, right: dict[str, float] | None) -> float:
    if not left or not right:
        return 0.0
    squared = 0.0
    for key in DESCRIPTOR_KEYS:
        squared += (float(left.get(key, 0.0)) - float(right.get(key, 0.0))) ** 2
    return round(math.sqrt(squared / len(DESCRIPTOR_KEYS)), 4)


def behavioral_profile_label(descriptor: dict[str, float] | None) -> str:
    if not descriptor:
        return "unknown"
    if float(descriptor.get("cluster_usage_ratio", 0.0)) >= 0.45:
        return "clustered_constructor"
    if float(descriptor.get("restart_gain_ratio", 0.0)) >= 0.18:
        return "restart_diversifier"
    if float(descriptor.get("three_opt_gain_ratio", 0.0)) >= 0.05:
        return "deep_local_search"
    if float(descriptor.get("two_opt_gain_ratio", 0.0)) >= 0.14:
        return "local_search_heavy"
    if float(descriptor.get("perturbation_accept_ratio", 0.0)) >= 0.35:
        return "perturbative_refiner"
    if float(descriptor.get("candidate_pruning_ratio", 0.0)) >= 0.82:
        return "aggressive_pruner"
    return "balanced"


def behavioral_cell(descriptor: dict[str, float] | None) -> str:
    if not descriptor:
        return "unknown:0:0:0:0"
    return ":".join(
        [
            behavioral_profile_label(descriptor),
            str(_bin_ratio(float(descriptor.get("mean_gap_ratio", 0.0)))),
            str(_bin_ratio(float(descriptor.get("two_opt_gain_ratio", 0.0)))),
            str(_bin_ratio(float(descriptor.get("restart_gain_ratio", 0.0)))),
            str(_bin_ratio(float(descriptor.get("cluster_usage_ratio", 0.0)))),
        ]
    )


def _bin_ratio(value: float, *, bins: int = 5) -> int:
    clipped = min(0.9999, max(0.0, float(value)))
    return min(bins - 1, max(0, int(clipped * bins)))
