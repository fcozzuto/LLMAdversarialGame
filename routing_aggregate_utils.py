from __future__ import annotations

import random
import statistics
from typing import Any


def _quantile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        return 0.0
    if probability <= 0.0:
        return float(sorted_values[0])
    if probability >= 1.0:
        return float(sorted_values[-1])
    position = probability * (len(sorted_values) - 1)
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    weight = position - lower_index
    lower = float(sorted_values[lower_index])
    upper = float(sorted_values[upper_index])
    return lower + ((upper - lower) * weight)


def bootstrap_mean_interval(
    values: list[float],
    *,
    seed: int = 0,
    bootstrap_samples: int = 20_000,
) -> dict[str, float | int | str]:
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "sd": 0.0,
            "ci95_low": 0.0,
            "ci95_high": 0.0,
            "interval_method": "bootstrap_percentile",
        }
    if len(values) == 1:
        value = round(float(values[0]), 6)
        return {
            "count": 1,
            "mean": value,
            "median": value,
            "sd": 0.0,
            "ci95_low": value,
            "ci95_high": value,
            "interval_method": "bootstrap_percentile",
        }

    rng = random.Random(seed)
    sample_size = len(values)
    draws: list[float] = []
    for _ in range(bootstrap_samples):
        sample = [float(values[rng.randrange(sample_size)]) for _ in range(sample_size)]
        draws.append(statistics.fmean(sample))
    draws.sort()

    mean = statistics.fmean(float(value) for value in values)
    median = statistics.median(float(value) for value in values)
    sd = statistics.stdev(float(value) for value in values)
    return {
        "count": sample_size,
        "mean": round(mean, 6),
        "median": round(float(median), 6),
        "sd": round(float(sd), 6),
        "ci95_low": round(_quantile(draws, 0.025), 6),
        "ci95_high": round(_quantile(draws, 0.975), 6),
        "interval_method": "bootstrap_percentile",
    }


def paired_bootstrap_delta(
    candidate_values: list[float],
    reference_values: list[float],
    *,
    lower_is_better: bool,
    seed: int = 0,
    bootstrap_samples: int = 20_000,
) -> dict[str, float | int | str | bool]:
    paired = [(float(candidate), float(reference)) for candidate, reference in zip(candidate_values, reference_values)]
    if not paired:
        return {
            "count": 0,
            "candidate_mean": 0.0,
            "reference_mean": 0.0,
            "mean_delta": 0.0,
            "median_delta": 0.0,
            "sd_delta": 0.0,
            "ci95_low": 0.0,
            "ci95_high": 0.0,
            "improved_run_fraction": 0.0,
            "ties_run_fraction": 0.0,
            "interval_method": "paired_bootstrap_percentile",
            "candidate_supported": False,
        }

    deltas = [candidate - reference for candidate, reference in paired]
    mean_delta = statistics.fmean(deltas)
    median_delta = statistics.median(deltas)
    sd_delta = statistics.stdev(deltas) if len(deltas) >= 2 else 0.0
    improved = sum(1 for delta in deltas if (delta < 0.0 if lower_is_better else delta > 0.0))
    ties = sum(1 for delta in deltas if abs(delta) < 1e-12)

    if len(deltas) == 1:
        ci_low = ci_high = float(deltas[0])
    else:
        rng = random.Random(seed)
        sample_size = len(deltas)
        draws: list[float] = []
        for _ in range(bootstrap_samples):
            sampled_deltas = [deltas[rng.randrange(sample_size)] for _ in range(sample_size)]
            draws.append(statistics.fmean(sampled_deltas))
        draws.sort()
        ci_low = _quantile(draws, 0.025)
        ci_high = _quantile(draws, 0.975)

    candidate_supported = ci_high < 0.0 if lower_is_better else ci_low > 0.0
    return {
        "count": len(paired),
        "candidate_mean": round(statistics.fmean(candidate for candidate, _ in paired), 6),
        "reference_mean": round(statistics.fmean(reference for _, reference in paired), 6),
        "mean_delta": round(mean_delta, 6),
        "median_delta": round(float(median_delta), 6),
        "sd_delta": round(float(sd_delta), 6),
        "ci95_low": round(float(ci_low), 6),
        "ci95_high": round(float(ci_high), 6),
        "improved_run_fraction": round(improved / len(deltas), 6),
        "ties_run_fraction": round(ties / len(deltas), 6),
        "interval_method": "paired_bootstrap_percentile",
        "candidate_supported": bool(candidate_supported),
    }


def find_condition_by_suffix(condition_names: set[str], suffix: str) -> str | None:
    matches = sorted(name for name in condition_names if name.endswith(suffix))
    if len(matches) == 1:
        return matches[0]
    return None


def build_default_paired_specs(condition_names: set[str]) -> list[dict[str, str]]:
    no_replay = find_condition_by_suffix(condition_names, "no_replay")
    random_replay = find_condition_by_suffix(condition_names, "random_replay")
    failure_replay = find_condition_by_suffix(condition_names, "failure_replay")
    failure_compression = find_condition_by_suffix(condition_names, "failure_replay_compression")

    specs: list[dict[str, str]] = []
    if random_replay and no_replay:
        specs.append(
            {
                "name": "random_vs_no_replay",
                "candidate": random_replay,
                "reference": no_replay,
            }
        )
    if failure_replay and no_replay:
        specs.append(
            {
                "name": "failure_vs_no_replay",
                "candidate": failure_replay,
                "reference": no_replay,
            }
        )
    if failure_replay and random_replay:
        specs.append(
            {
                "name": "failure_vs_random_replay",
                "candidate": failure_replay,
                "reference": random_replay,
            }
        )
    if failure_compression and failure_replay:
        specs.append(
            {
                "name": "compression_vs_failure_replay",
                "candidate": failure_compression,
                "reference": failure_replay,
            }
        )
    if failure_compression and no_replay:
        specs.append(
            {
                "name": "compression_vs_no_replay",
                "candidate": failure_compression,
                "reference": no_replay,
            }
        )
    return specs


def summarize_paired_comparisons(
    *,
    run_condition_tables: list[dict[str, dict[str, Any]]],
    primary_metric_key: str,
    comparison_specs: list[dict[str, str]],
    benchmark_label: str,
) -> list[dict[str, Any]]:
    metric_specs = [
        ("final_transfer_gap", True, "transfer_gap"),
        (primary_metric_key, True, benchmark_label),
        ("final_synthetic_gap", True, "synthetic_gap"),
        ("mean_code_novelty", True, "accepted_novelty"),
        ("mean_complexity", True, "complexity"),
        ("adaptation_efficiency", False, "adaptation_efficiency"),
    ]

    comparisons: list[dict[str, Any]] = []
    for spec_index, spec in enumerate(comparison_specs):
        candidate_name = spec["candidate"]
        reference_name = spec["reference"]
        metric_payload: dict[str, Any] = {}
        paired_count = 0
        for metric_key, lower_is_better, label in metric_specs:
            candidate_values: list[float] = []
            reference_values: list[float] = []
            for run_index, table in enumerate(run_condition_tables):
                candidate = table.get(candidate_name)
                reference = table.get(reference_name)
                if candidate is None or reference is None:
                    continue
                candidate_values.append(float(candidate.get(metric_key, 0.0)))
                reference_values.append(float(reference.get(metric_key, 0.0)))
            paired_count = max(paired_count, len(candidate_values))
            metric_payload[label] = paired_bootstrap_delta(
                candidate_values,
                reference_values,
                lower_is_better=lower_is_better,
                seed=(spec_index * 1000) + len(metric_key) + 17,
            )
        comparisons.append(
            {
                "comparison_name": spec["name"],
                "candidate_condition": candidate_name,
                "reference_condition": reference_name,
                "paired_run_count": paired_count,
                "metrics": metric_payload,
            }
        )
    return comparisons
