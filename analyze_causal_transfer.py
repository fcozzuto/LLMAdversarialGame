from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
import json
import math
from pathlib import Path
import statistics
from typing import Any

from llm_grid_battle.behavioral_descriptors import behavioral_distance
from llm_grid_battle.code_fingerprints import code_similarity
from llm_grid_battle.pdf_report import write_pdf_report


RECIPE_DISPLAY_NAMES = {
    "rotating_opponents_holdout_endpoint": "Rotating opponents",
    "rotating_plus_nemesis_novelty_replay": "Rotating + nemesis + novelty + replay",
    "rotating_plus_replay_aware_selection": "Rotating + replay-aware selection",
}

CONDITION_DISPLAY_NAMES = {
    "transfer_resource_collection_denial": "resource collection / denial",
    "transfer_pursuit_evasion": "pursuit / evasion",
    "transfer_territory_control": "territory control",
}

DIVERSITY_ACCEPT_REASONS = {
    "opened_new_behavior_cell",
    "diversity_gain_within_score_tolerance",
    "behavioral_diversity_within_score_tolerance",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _stat_summary(
    values: list[float],
    *,
    lower_bound: float | None = None,
    upper_bound: float | None = None,
) -> dict[str, Any]:
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "stddev": 0.0,
            "min": 0.0,
            "max": 0.0,
            "ci95_low": 0.0,
            "ci95_high": 0.0,
        }
    mean = statistics.mean(values)
    stddev = statistics.stdev(values) if len(values) > 1 else 0.0
    margin = 1.96 * (stddev / math.sqrt(len(values))) if len(values) > 1 else 0.0
    ci95_low = mean - margin
    ci95_high = mean + margin
    if lower_bound is not None:
        ci95_low = max(lower_bound, ci95_low)
    if upper_bound is not None:
        ci95_high = min(upper_bound, ci95_high)
    return {
        "count": len(values),
        "mean": round(mean, 4),
        "stddev": round(stddev, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "ci95_low": round(ci95_low, 4),
        "ci95_high": round(ci95_high, 4),
    }


def _display_recipe(recipe_name: str) -> str:
    return RECIPE_DISPLAY_NAMES.get(recipe_name, recipe_name.replace("_", " "))


def _display_condition(condition_name: str) -> str:
    return CONDITION_DISPLAY_NAMES.get(condition_name, condition_name.replace("_", " "))


def _infer_replicate_label(run_metadata: dict[str, Any], run_name: str) -> str:
    label = str(run_metadata.get("replicate_label") or "").strip()
    if label:
        return label
    parts = run_name.rsplit("_", 1)
    if len(parts) == 2 and parts[1]:
        return parts[1]
    return run_name


def _average_ranks(values: list[float]) -> list[float]:
    indexed = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(indexed):
        end = cursor + 1
        while end < len(indexed) and indexed[end][0] == indexed[cursor][0]:
            end += 1
        average_rank = ((cursor + 1) + end) / 2.0
        for item_index in range(cursor, end):
            ranks[indexed[item_index][1]] = average_rank
        cursor = end
    return ranks


def _pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = statistics.mean(left)
    right_mean = statistics.mean(right)
    left_var = sum((value - left_mean) ** 2 for value in left)
    right_var = sum((value - right_mean) ** 2 for value in right)
    if left_var <= 0.0 or right_var <= 0.0:
        return None
    covariance = sum((left[idx] - left_mean) * (right[idx] - right_mean) for idx in range(len(left)))
    return covariance / math.sqrt(left_var * right_var)


def _spearman(left: list[float], right: list[float]) -> dict[str, Any]:
    if len(left) != len(right) or len(left) < 3:
        return {"count": len(left), "rho": None}
    rho = _pearson(_average_ranks(left), _average_ranks(right))
    return {"count": len(left), "rho": round(rho, 4) if rho is not None else None}


def _binomial_coeff(n: int, k: int) -> int:
    return math.comb(n, k)


def _sign_test_two_sided(positive: int, negative: int) -> float | None:
    trials = positive + negative
    if trials <= 0:
        return None
    tail = sum(_binomial_coeff(trials, value) for value in range(max(positive, negative), trials + 1))
    probability = min(1.0, 2.0 * tail / (2 ** trials))
    return round(probability, 4)


def _paired_difference_summary(differences: list[float]) -> dict[str, Any]:
    positive = sum(1 for value in differences if value > 0)
    negative = sum(1 for value in differences if value < 0)
    zero = sum(1 for value in differences if value == 0)
    stats = _stat_summary(differences)
    stats.update(
        {
            "positive_count": positive,
            "negative_count": negative,
            "tie_count": zero,
            "sign_test_p": _sign_test_two_sided(positive, negative),
        }
    )
    return stats


def _condition_transition_features(condition_summary: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    learner = str(condition_summary.get("curriculum", {}).get("focal_agent") or condition_summary["agents"][0]["name"])
    opponent = str(condition_summary.get("curriculum", {}).get("opponent_agent") or condition_summary["agents"][1]["name"])
    epochs = list(condition_summary.get("epochs", []))
    code_novelties: list[float] = []
    descriptor_shifts: list[float] = []
    accepted_count = 0
    diversity_accept_count = 0
    transition_rows: list[dict[str, Any]] = []

    for index in range(1, len(epochs)):
        previous = epochs[index - 1]
        current = epochs[index]
        previous_code = str(previous.get("submitted_codes", {}).get(learner, previous["codes"][learner]))
        current_code = str(current.get("submitted_codes", {}).get(learner, current["codes"][learner]))
        code_novelty = round(1.0 - code_similarity(previous_code, current_code), 4)
        previous_descriptor = previous.get("behavioral_descriptors", {}).get(learner, {})
        current_descriptor = current.get("behavioral_descriptors", {}).get(learner, {})
        descriptor_shift = behavioral_distance(previous_descriptor, current_descriptor)
        selection = (current.get("curriculum") or {}).get("selection") or {}
        accepted = bool(selection.get("accepted", False))
        reason = str(selection.get("reason", ""))
        if accepted:
            accepted_count += 1
        if reason in DIVERSITY_ACCEPT_REASONS:
            diversity_accept_count += 1
        score_delta = float(current["scores"][learner]) - float(previous["scores"][learner])
        previous_margin = float(previous["scores"][learner]) - float(previous["scores"][opponent])
        current_margin = float(current["scores"][learner]) - float(current["scores"][opponent])
        code_novelties.append(code_novelty)
        descriptor_shifts.append(descriptor_shift)
        transition_rows.append(
            {
                "epoch_index": int(current["epoch_index"]),
                "code_novelty": code_novelty,
                "descriptor_shift": descriptor_shift,
                "accepted": accepted,
                "selection_reason": reason,
                "score_delta": round(score_delta, 4),
                "margin_delta": round(current_margin - previous_margin, 4),
            }
        )

    feature_summary = {
        "transition_count": len(transition_rows),
        "mean_code_novelty": round(_mean(code_novelties), 4),
        "mean_descriptor_shift": round(_mean(descriptor_shifts), 4),
        "accepted_transition_rate": round(accepted_count / len(transition_rows), 4) if transition_rows else 0.0,
        "diversity_accept_count": diversity_accept_count,
    }
    return feature_summary, transition_rows


def _index_holdout_results(evaluation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for opponent in evaluation.get("opponents", []):
        label = str(opponent.get("label") or "unknown")
        indexed[label] = {
            "label": label,
            "mean_score_margin": float(opponent.get("mean_score_margin", 0.0)),
            "win_rate": float(opponent.get("win_rate", 0.0)),
            "games": int(opponent.get("games", evaluation.get("games_per_opponent", 0))),
        }
    return indexed


def _has_run_dirs(path: Path) -> bool:
    return any(candidate.is_dir() for candidate in path.glob("run_*"))


def _discover_recipe_roots(root: Path) -> list[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Runs root not found: {root}")
    return sorted(
        path.resolve()
        for path in root.iterdir()
        if path.is_dir() and path.name != "__pycache__" and _has_run_dirs(path)
    )


def _resolve_baseline_recipe(recipe_names: list[str], requested: str | None) -> str | None:
    if requested:
        if requested not in recipe_names:
            available = ", ".join(sorted(recipe_names)) or "none"
            raise ValueError(
                f"Requested baseline recipe `{requested}` is not present in the loaded recipe roots. "
                f"Available recipes: {available}."
            )
        return requested
    if "rotating_opponents_holdout_endpoint" in recipe_names:
        return "rotating_opponents_holdout_endpoint"
    return None


def _order_recipe_runs(recipe_runs: list[dict[str, Any]], baseline_recipe: str | None) -> list[dict[str, Any]]:
    return sorted(
        recipe_runs,
        key=lambda item: (
            0 if baseline_recipe and item["recipe_name"] == baseline_recipe else 1,
            str(item["recipe_name"]),
        ),
    )


def _load_recipe_runs(recipe_root: Path) -> dict[str, Any]:
    if not recipe_root.exists():
        raise FileNotFoundError(f"Recipe root not found: {recipe_root}")
    run_dirs = sorted(path for path in recipe_root.glob("run_*") if path.is_dir())
    if not run_dirs:
        raise FileNotFoundError(f"No run_* directories found under: {recipe_root}")

    observations: list[dict[str, Any]] = []
    transitions: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        run_metadata = _load_json(run_dir / "run_metadata.json") if (run_dir / "run_metadata.json").exists() else {}
        suite_summary = _load_json(run_dir / "suite_summary.json")
        suite_conditions = {condition["condition_name"]: condition for condition in suite_summary.get("conditions", [])}
        replicate_label = _infer_replicate_label(run_metadata, run_dir.name)
        for condition_dir in sorted(path for path in run_dir.iterdir() if path.is_dir()):
            condition_summary_path = condition_dir / "condition_summary.json"
            if not condition_summary_path.exists():
                continue
            raw_condition = _load_json(condition_summary_path)
            condition_name = str(raw_condition["condition_name"])
            suite_condition = suite_conditions.get(condition_name)
            if suite_condition is None:
                continue
            learner = str(suite_condition.get("learner_agent") or raw_condition["agents"][0]["name"])
            primary_endpoint = suite_condition.get("primary_endpoint", {})
            evaluation = suite_condition.get("evaluation", {})
            curriculum_metrics = suite_condition.get("curriculum_metrics", {}).get(learner, {})
            novelty = suite_condition.get("novelty", {}).get(learner, {})
            feature_summary, condition_transitions = _condition_transition_features(raw_condition)
            observation = {
                "recipe_name": recipe_root.name,
                "recipe_display_name": _display_recipe(recipe_root.name),
                "recipe_root": str(recipe_root.resolve()),
                "run_name": run_dir.name,
                "replicate_label": replicate_label,
                "seed_offset": int(run_metadata.get("seed_offset", 0) or 0),
                "condition_name": condition_name,
                "condition_display_name": _display_condition(condition_name),
                "environment_name": str(suite_condition.get("environment_name", "resource_collection")),
                "primary_win_rate": float(primary_endpoint.get("mean_win_rate", 0.0)),
                "primary_margin": float(primary_endpoint.get("mean_score_margin", 0.0)),
                "mean_code_novelty": float(novelty.get("average", feature_summary["mean_code_novelty"])),
                "mean_descriptor_shift": float(feature_summary["mean_descriptor_shift"]),
                "accepted_transition_rate": float(feature_summary["accepted_transition_rate"]),
                "diversity_accept_count": int(feature_summary["diversity_accept_count"]),
                "transition_count": int(feature_summary["transition_count"]),
                "loop_count": int(curriculum_metrics.get("loop_count", 0)),
                "strategy_switch_count": int(curriculum_metrics.get("strategy_switch_count", 0)),
                "behavior_cell_count": int(curriculum_metrics.get("behavior_cell_count", 0)),
                "specific_adaptation_count": int(curriculum_metrics.get("specific_adaptation_count", 0)),
                "superficial_novelty_count": int(curriculum_metrics.get("superficial_novelty_count", 0)),
                "post_loss_novelty_spike_count": int(curriculum_metrics.get("post_loss_novelty_spike_count", 0)),
                "degradation_count": int(curriculum_metrics.get("degradation_count", 0)),
                "holdout_results": _index_holdout_results(evaluation),
            }
            transition_count = max(1, int(observation["transition_count"]))
            observation["functional_adaptation_ratio"] = round(
                float(observation["mean_descriptor_shift"]) / max(0.0001, float(observation["mean_code_novelty"])),
                4,
            )
            observation["strategy_switch_rate"] = round(float(observation["strategy_switch_count"]) / transition_count, 4)
            observation["specific_adaptation_rate"] = round(float(observation["specific_adaptation_count"]) / transition_count, 4)
            observation["superficial_novelty_rate"] = round(float(observation["superficial_novelty_count"]) / transition_count, 4)
            observation["post_loss_novelty_spike_rate"] = round(
                float(observation["post_loss_novelty_spike_count"]) / transition_count,
                4,
            )
            observations.append(observation)
            for row in condition_transitions:
                transitions.append(
                    {
                        **row,
                        "recipe_name": recipe_root.name,
                        "recipe_display_name": _display_recipe(recipe_root.name),
                        "run_name": run_dir.name,
                        "replicate_label": replicate_label,
                        "condition_name": condition_name,
                        "condition_display_name": _display_condition(condition_name),
                        "environment_name": observation["environment_name"],
                    }
                )

    return {
        "recipe_name": recipe_root.name,
        "recipe_display_name": _display_recipe(recipe_root.name),
        "recipe_root": str(recipe_root.resolve()),
        "run_count": len(run_dirs),
        "observations": observations,
        "transitions": transitions,
    }


def _observation_index(observations: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    indexed: dict[tuple[str, str, str], dict[str, Any]] = {}
    for observation in observations:
        key = (
            str(observation["recipe_name"]),
            str(observation["replicate_label"]),
            str(observation["condition_name"]),
        )
        indexed[key] = observation
    return indexed


def _condition_summary_by_recipe(observations: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    buckets: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for observation in observations:
        bucket = buckets[observation["recipe_name"]][observation["condition_name"]]
        bucket["primary_win_rate"].append(float(observation["primary_win_rate"]))
        bucket["primary_margin"].append(float(observation["primary_margin"]))
    summary: dict[str, dict[str, dict[str, Any]]] = {}
    for recipe_name, by_condition in buckets.items():
        summary[recipe_name] = {}
        for condition_name, metrics in by_condition.items():
            summary[recipe_name][condition_name] = {
                "primary_win_rate": _stat_summary(metrics["primary_win_rate"], lower_bound=0.0, upper_bound=1.0),
                "primary_margin": _stat_summary(metrics["primary_margin"]),
            }
    return summary


def _overall_recipe_summary(observations: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_recipe_and_replicate: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for observation in observations:
        by_recipe_and_replicate[observation["recipe_name"]][observation["replicate_label"]].append(observation)

    summary: dict[str, dict[str, Any]] = {}
    for recipe_name, by_replicate in by_recipe_and_replicate.items():
        win_rates: list[float] = []
        margins: list[float] = []
        for items in by_replicate.values():
            win_rates.append(_mean([float(item["primary_win_rate"]) for item in items]))
            margins.append(_mean([float(item["primary_margin"]) for item in items]))
        summary[recipe_name] = {
            "primary_win_rate": _stat_summary(win_rates, lower_bound=0.0, upper_bound=1.0),
            "primary_margin": _stat_summary(margins),
        }
    return summary


def _paired_comparisons(observations: list[dict[str, Any]], recipe_names: list[str]) -> list[dict[str, Any]]:
    indexed = _observation_index(observations)
    comparisons: list[dict[str, Any]] = []
    for left_index in range(len(recipe_names)):
        for right_index in range(left_index + 1, len(recipe_names)):
            left_recipe = recipe_names[left_index]
            right_recipe = recipe_names[right_index]
            labels = sorted(
                {
                    replicate_label
                    for recipe_name, replicate_label, _ in indexed
                    if recipe_name in {left_recipe, right_recipe}
                }
            )
            condition_names = sorted(
                {
                    condition_name
                    for recipe_name, _, condition_name in indexed
                    if recipe_name in {left_recipe, right_recipe}
                }
            )
            for condition_name in condition_names:
                left_values: list[float] = []
                right_values: list[float] = []
                left_margins: list[float] = []
                right_margins: list[float] = []
                diffs: list[float] = []
                margin_diffs: list[float] = []
                paired_labels: list[str] = []
                for label in labels:
                    left_observation = indexed.get((left_recipe, label, condition_name))
                    right_observation = indexed.get((right_recipe, label, condition_name))
                    if left_observation is None or right_observation is None:
                        continue
                    left_value = float(left_observation["primary_win_rate"])
                    right_value = float(right_observation["primary_win_rate"])
                    left_margin = float(left_observation["primary_margin"])
                    right_margin = float(right_observation["primary_margin"])
                    left_values.append(left_value)
                    right_values.append(right_value)
                    left_margins.append(left_margin)
                    right_margins.append(right_margin)
                    diffs.append(round(right_value - left_value, 4))
                    margin_diffs.append(round(right_margin - left_margin, 4))
                    paired_labels.append(label)
                if not diffs:
                    continue
                comparisons.append(
                    {
                        "left_recipe": left_recipe,
                        "right_recipe": right_recipe,
                        "condition_name": condition_name,
                        "condition_display_name": _display_condition(condition_name),
                        "replicate_labels": paired_labels,
                        "left_primary_win_rate": _stat_summary(left_values, lower_bound=0.0, upper_bound=1.0),
                        "right_primary_win_rate": _stat_summary(right_values, lower_bound=0.0, upper_bound=1.0),
                        "left_primary_margin": _stat_summary(left_margins),
                        "right_primary_margin": _stat_summary(right_margins),
                        "win_rate_difference": _paired_difference_summary(diffs),
                        "margin_difference": _paired_difference_summary(margin_diffs),
                    }
                )

            left_overall: list[float] = []
            right_overall: list[float] = []
            left_overall_margins: list[float] = []
            right_overall_margins: list[float] = []
            overall_diffs: list[float] = []
            overall_margin_diffs: list[float] = []
            paired_labels = []
            for label in labels:
                left_items = [
                    indexed[key]
                    for key in indexed
                    if key[0] == left_recipe and key[1] == label
                ]
                right_items = [
                    indexed[key]
                    for key in indexed
                    if key[0] == right_recipe and key[1] == label
                ]
                if not left_items or not right_items:
                    continue
                left_by_condition = {item["condition_name"]: item for item in left_items}
                right_by_condition = {item["condition_name"]: item for item in right_items}
                shared_conditions = sorted(set(left_by_condition) & set(right_by_condition))
                if not shared_conditions:
                    continue
                left_avg = _mean([float(left_by_condition[name]["primary_win_rate"]) for name in shared_conditions])
                right_avg = _mean([float(right_by_condition[name]["primary_win_rate"]) for name in shared_conditions])
                left_margin_avg = _mean([float(left_by_condition[name]["primary_margin"]) for name in shared_conditions])
                right_margin_avg = _mean([float(right_by_condition[name]["primary_margin"]) for name in shared_conditions])
                left_overall.append(left_avg)
                right_overall.append(right_avg)
                left_overall_margins.append(left_margin_avg)
                right_overall_margins.append(right_margin_avg)
                overall_diffs.append(round(right_avg - left_avg, 4))
                overall_margin_diffs.append(round(right_margin_avg - left_margin_avg, 4))
                paired_labels.append(label)
            if overall_diffs:
                comparisons.append(
                    {
                        "left_recipe": left_recipe,
                        "right_recipe": right_recipe,
                        "condition_name": "overall_transfer_average",
                        "condition_display_name": "overall transfer average",
                        "replicate_labels": paired_labels,
                        "left_primary_win_rate": _stat_summary(left_overall, lower_bound=0.0, upper_bound=1.0),
                        "right_primary_win_rate": _stat_summary(right_overall, lower_bound=0.0, upper_bound=1.0),
                        "left_primary_margin": _stat_summary(left_overall_margins),
                        "right_primary_margin": _stat_summary(right_overall_margins),
                        "win_rate_difference": _paired_difference_summary(overall_diffs),
                        "margin_difference": _paired_difference_summary(overall_margin_diffs),
                    }
                )
    return comparisons


def _failure_mode_summary(observations: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, dict[str, Any]]]]:
    buckets: dict[str, dict[str, dict[str, dict[str, list[float]]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    )
    for observation in observations:
        condition_name = str(observation["condition_name"])
        recipe_name = str(observation["recipe_name"])
        for label, holdout in observation["holdout_results"].items():
            bucket = buckets[condition_name][label][recipe_name]
            bucket["win_rate"].append(float(holdout["win_rate"]))
            bucket["mean_score_margin"].append(float(holdout["mean_score_margin"]))
    summary: dict[str, dict[str, dict[str, dict[str, Any]]]] = {}
    for condition_name, by_label in buckets.items():
        summary[condition_name] = {}
        for label, by_recipe in by_label.items():
            summary[condition_name][label] = {}
            for recipe_name, metrics in by_recipe.items():
                summary[condition_name][label][recipe_name] = {
                    "win_rate": _stat_summary(metrics["win_rate"], lower_bound=0.0, upper_bound=1.0),
                    "mean_score_margin": _stat_summary(metrics["mean_score_margin"]),
                }
    return summary


def _failure_mode_findings(
    failure_modes: dict[str, dict[str, dict[str, dict[str, Any]]]],
    baseline_recipe: str | None,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for condition_name, by_label in failure_modes.items():
        for label, by_recipe in by_label.items():
            weakness_recipes = sorted(
                recipe_name
                for recipe_name, stats in by_recipe.items()
                if float(stats["win_rate"]["mean"]) < 0.5
            )
            improvement_vs_baseline = None
            if baseline_recipe and baseline_recipe in by_recipe:
                baseline_win = float(by_recipe[baseline_recipe]["win_rate"]["mean"])
                deltas = []
                for recipe_name, stats in by_recipe.items():
                    if recipe_name == baseline_recipe:
                        continue
                    deltas.append(
                        {
                            "recipe_name": recipe_name,
                            "delta_win_rate": round(float(stats["win_rate"]["mean"]) - baseline_win, 4),
                        }
                    )
                if deltas:
                    improvement_vs_baseline = sorted(deltas, key=lambda item: item["delta_win_rate"], reverse=True)
            findings.append(
                {
                    "condition_name": condition_name,
                    "condition_display_name": _display_condition(condition_name),
                    "holdout_label": label,
                    "weakness_recipes": weakness_recipes,
                    "improvement_vs_baseline": improvement_vs_baseline,
                }
            )
    return findings


def _attach_baseline_deltas(observations: list[dict[str, Any]], baseline_recipe: str | None) -> None:
    if not baseline_recipe:
        return
    indexed = _observation_index(observations)
    for observation in observations:
        if observation["recipe_name"] == baseline_recipe:
            observation["delta_vs_baseline_win_rate"] = None
            observation["delta_vs_baseline_margin"] = None
            continue
        baseline = indexed.get((baseline_recipe, observation["replicate_label"], observation["condition_name"]))
        if baseline is None:
            observation["delta_vs_baseline_win_rate"] = None
            observation["delta_vs_baseline_margin"] = None
            continue
        observation["delta_vs_baseline_win_rate"] = round(
            float(observation["primary_win_rate"]) - float(baseline["primary_win_rate"]),
            4,
        )
        observation["delta_vs_baseline_margin"] = round(
            float(observation["primary_margin"]) - float(baseline["primary_margin"]),
            4,
        )


def _correlation_row(observations: list[dict[str, Any]], feature_name: str, outcome_name: str) -> dict[str, Any]:
    left: list[float] = []
    right: list[float] = []
    for observation in observations:
        feature_value = observation.get(feature_name)
        outcome_value = observation.get(outcome_name)
        if feature_value is None or outcome_value is None:
            continue
        left.append(float(feature_value))
        right.append(float(outcome_value))
    return {
        "feature_name": feature_name,
        "outcome_name": outcome_name,
        **_spearman(left, right),
    }


def _behavioral_correlations(
    observations: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
    baseline_recipe: str | None,
) -> dict[str, Any]:
    transition_novelty = [float(item["code_novelty"]) for item in transitions]
    transition_shift = [float(item["descriptor_shift"]) for item in transitions]
    accepted_transitions = [item for item in transitions if bool(item.get("accepted", False))]
    accepted_novelty = [float(item["code_novelty"]) for item in accepted_transitions]
    accepted_shift = [float(item["descriptor_shift"]) for item in accepted_transitions]

    feature_names = [
        "mean_code_novelty",
        "mean_descriptor_shift",
        "functional_adaptation_ratio",
        "strategy_switch_rate",
        "behavior_cell_count",
        "specific_adaptation_rate",
        "superficial_novelty_rate",
        "post_loss_novelty_spike_rate",
    ]
    outcome_names = ["primary_win_rate", "primary_margin"]
    if baseline_recipe:
        outcome_names.extend(["delta_vs_baseline_win_rate", "delta_vs_baseline_margin"])

    run_level_rows: list[dict[str, Any]] = []
    for feature_name in feature_names:
        for outcome_name in outcome_names:
            run_level_rows.append(_correlation_row(observations, feature_name, outcome_name))

    return {
        "transition_all": {
            "metric_pair": "code_novelty_vs_descriptor_shift",
            **_spearman(transition_novelty, transition_shift),
        },
        "transition_accepted_only": {
            "metric_pair": "accepted_code_novelty_vs_descriptor_shift",
            **_spearman(accepted_novelty, accepted_shift),
        },
        "run_level": run_level_rows,
    }


def _top_correlation_rows(
    rows: list[dict[str, Any]],
    *,
    outcome_name: str,
    positive: bool,
    limit: int = 2,
) -> list[dict[str, Any]]:
    filtered = [
        row
        for row in rows
        if row.get("outcome_name") == outcome_name and row.get("rho") is not None
    ]
    if positive:
        filtered = [row for row in filtered if float(row["rho"]) > 0]
        filtered.sort(key=lambda item: float(item["rho"]), reverse=True)
    else:
        filtered = [row for row in filtered if float(row["rho"]) < 0]
        filtered.sort(key=lambda item: float(item["rho"]))
    return filtered[:limit]


def _format_stat(stats: dict[str, Any]) -> str:
    return (
        f"mean {stats['mean']} "
        f"(95% CI {stats['ci95_low']} to {stats['ci95_high']}; n={stats['count']})"
    )


def _render_comparison_table(comparisons: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Comparison | Scope | Left win | Right win | Win diff | Sign p | Left margin | Right margin | Margin diff |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in comparisons:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{_display_recipe(item['left_recipe'])} vs {_display_recipe(item['right_recipe'])}",
                    item["condition_display_name"],
                    str(item["left_primary_win_rate"]["mean"]),
                    str(item["right_primary_win_rate"]["mean"]),
                    str(item["win_rate_difference"]["mean"]),
                    str(item["win_rate_difference"]["sign_test_p"]),
                    str(item["left_primary_margin"]["mean"]),
                    str(item["right_primary_margin"]["mean"]),
                    str(item["margin_difference"]["mean"]),
                ]
            )
            + " |"
        )
    return lines


def _render_failure_mode_lines(
    failure_modes: dict[str, dict[str, dict[str, dict[str, Any]]]],
    recipe_names: list[str],
) -> list[str]:
    lines: list[str] = []
    for condition_name in sorted(failure_modes):
        lines.append(f"### {_display_condition(condition_name)}")
        lines.append(
            "| Holdout archetype | "
            + " | ".join(f"{_display_recipe(recipe_name)} win/margin" for recipe_name in recipe_names)
            + " |"
        )
        lines.append(
            "| --- | " + " | ".join("---" for _ in recipe_names) + " |"
        )
        for holdout_label in sorted(failure_modes[condition_name]):
            row = [holdout_label]
            for recipe_name in recipe_names:
                stats = failure_modes[condition_name][holdout_label].get(recipe_name)
                if not stats:
                    row.append("N/A")
                    continue
                row.append(
                    f"{stats['win_rate']['mean']} / {stats['mean_score_margin']['mean']}"
                )
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
    return lines


def _render_failure_findings(summary: dict[str, Any]) -> list[str]:
    recipe_names = summary["recipe_names"]
    findings = summary["failure_mode_findings"]
    persistent = [
        item
        for item in findings
        if len(item.get("weakness_recipes", [])) == len(recipe_names)
    ]
    improvements: list[dict[str, Any]] = []
    for item in findings:
        ranked = item.get("improvement_vs_baseline") or []
        if not ranked:
            continue
        best = ranked[0]
        if float(best["delta_win_rate"]) > 0.0:
            improvements.append(
                {
                    "condition_display_name": item["condition_display_name"],
                    "holdout_label": item["holdout_label"],
                    "recipe_name": best["recipe_name"],
                    "delta_win_rate": float(best["delta_win_rate"]),
                }
            )
    improvements.sort(key=lambda entry: entry["delta_win_rate"], reverse=True)

    lines: list[str] = []
    if persistent:
        labels = ", ".join(
            f"`{item['condition_display_name']} / {item['holdout_label']}`"
            for item in sorted(persistent, key=lambda row: (row["condition_display_name"], row["holdout_label"]))
        )
        lines.append(f"- Persistent weak archetypes across all compared recipes: {labels}.")
    if improvements:
        rendered = ", ".join(
            f"`{item['condition_display_name']} / {item['holdout_label']}` for {_display_recipe(item['recipe_name'])} ({item['delta_win_rate']:+.3f} win rate)"
            for item in improvements[:5]
        )
        lines.append(f"- Largest win-rate improvements relative to the baseline appeared in {rendered}.")
    if not lines:
        lines.append("- No cross-recipe failure-mode finding cleared the current automatic thresholds.")
    return lines


def _render_correlation_lines(correlations: dict[str, Any]) -> list[str]:
    top_positive = _top_correlation_rows(correlations["run_level"], outcome_name="primary_win_rate", positive=True)
    top_negative = _top_correlation_rows(correlations["run_level"], outcome_name="primary_win_rate", positive=False)
    lines = [
        f"- All transitions: novelty vs descriptor shift -> rho {correlations['transition_all']['rho']} (n={correlations['transition_all']['count']}).",
        f"- Accepted transitions only: novelty vs descriptor shift -> rho {correlations['transition_accepted_only']['rho']} (n={correlations['transition_accepted_only']['count']}).",
    ]
    if top_positive:
        positives = ", ".join(f"{row['feature_name']} ({row['rho']})" for row in top_positive)
        lines.append(f"- Strongest positive transfer correlates in this dataset: {positives}.")
    if top_negative:
        negatives = ", ".join(f"{row['feature_name']} ({row['rho']})" for row in top_negative)
        lines.append(f"- Strongest negative transfer correlates in this dataset: {negatives}.")
    lines.extend(
        [
        "",
        "| Feature proxy | Outcome | Spearman rho | N |",
        "| --- | --- | --- | --- |",
        ]
    )
    for row in correlations["run_level"]:
        lines.append(
            f"| {row['feature_name']} | {row['outcome_name']} | {row['rho']} | {row['count']} |"
        )
    return lines


def _render_markdown(summary: dict[str, Any]) -> str:
    recipe_names = summary["recipe_names"]
    lines = [
        "# Phase 4 Causal Transfer Analysis",
        "",
        "## Scope",
        f"- Recipe roots analyzed: {', '.join(f'`{item}`' for item in summary['recipe_roots'])}.",
        f"- Recipes compared: {', '.join(_display_recipe(item) for item in recipe_names)}.",
        (
            f"- Baseline recipe for delta metrics: `{summary['baseline_recipe']}`."
            if summary.get("baseline_recipe")
            else "- Baseline recipe for delta metrics: none resolved; baseline-relative rows are omitted."
        ),
        f"- Condition observations: {len(summary['observations'])}.",
        f"- Epoch-to-epoch transition rows: {len(summary['transitions'])}.",
        "",
        "## Reliability And Replication",
    ]
    for recipe_name in recipe_names:
        overall = summary["overall_recipe_summary"].get(recipe_name, {})
        if not overall:
            continue
        lines.append(
            f"- {_display_recipe(recipe_name)} overall transfer win rate: {_format_stat(overall['primary_win_rate'])}; overall transfer margin: {_format_stat(overall['primary_margin'])}."
        )
        by_condition = summary["condition_summary_by_recipe"].get(recipe_name, {})
        for condition_name in sorted(by_condition):
            lines.append(
                f"- {_display_recipe(recipe_name)} on {_display_condition(condition_name)}: win rate {_format_stat(by_condition[condition_name]['primary_win_rate'])}; margin {_format_stat(by_condition[condition_name]['primary_margin'])}."
            )
    lines.extend(["", *(_render_comparison_table(summary["paired_comparisons"]) or [])])
    lines.extend(
        [
            "",
            "## Failure Modes",
            "- Holdout rows are reported as `mean win rate / mean score margin` across replicates.",
            *_render_failure_findings(summary),
            "",
            *_render_failure_mode_lines(summary["failure_modes"], recipe_names),
            "## Behavioral Interpretation",
            "- `mean_code_novelty` is the average lexical code-change magnitude across consecutive epochs.",
            "- `mean_descriptor_shift` is the average behavioral-descriptor distance across consecutive epochs.",
            "- `strategy_switch_count`, `behavior_cell_count`, and `specific_adaptation_count` are the main proxies for stable adaptive motifs in this report.",
            "",
            *_render_correlation_lines(summary["behavioral_correlations"]),
            "",
            "## Interpretation Guardrails",
            "- These correlations are exploratory and should not be treated as causal proof on their own.",
            "- The behavioral descriptors remain heuristic proxies, but they are closer to functional adaptation than lexical code novelty alone.",
            "- Paired-seed transfer comparisons should be weighted more heavily than unpaired aggregate differences.",
            "- Persistent weak archetypes are scientifically useful evidence of uneven robustness, not a nuisance to be hidden.",
        ]
    )
    return "\n".join(lines)


def build_summary(recipe_roots: list[Path], *, baseline_recipe_name: str | None = None) -> dict[str, Any]:
    recipe_runs = [_load_recipe_runs(path.resolve()) for path in recipe_roots]
    discovered_recipe_names = [item["recipe_name"] for item in recipe_runs]
    baseline_recipe = _resolve_baseline_recipe(discovered_recipe_names, baseline_recipe_name)
    recipe_runs = _order_recipe_runs(recipe_runs, baseline_recipe)
    recipe_names = [item["recipe_name"] for item in recipe_runs]
    observations = [row for item in recipe_runs for row in item["observations"]]
    transitions = [row for item in recipe_runs for row in item["transitions"]]
    _attach_baseline_deltas(observations, baseline_recipe)
    return {
        "generated_at_local": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recipe_roots": [item["recipe_root"] for item in recipe_runs],
        "recipe_names": recipe_names,
        "baseline_recipe": baseline_recipe,
        "observations": observations,
        "transitions": transitions,
        "overall_recipe_summary": _overall_recipe_summary(observations),
        "condition_summary_by_recipe": _condition_summary_by_recipe(observations),
        "paired_comparisons": _paired_comparisons(observations, recipe_names),
        "failure_modes": _failure_mode_summary(observations),
        "failure_mode_findings": _failure_mode_findings(_failure_mode_summary(observations), baseline_recipe),
        "behavioral_correlations": _behavioral_correlations(observations, transitions, baseline_recipe),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a phase-4 causal-transfer report from completed transfer-suite runs."
    )
    parser.add_argument(
        "--recipe-root",
        action="append",
        default=None,
        help="Recipe run root such as runs/transfer_suite/rotating_opponents_holdout_endpoint. Repeat for multiple recipes.",
    )
    parser.add_argument(
        "--runs-root",
        default="runs/transfer_suite",
        help="Fallback directory used when --recipe-root is omitted. Only subdirectories that contain run_* children are treated as recipe roots.",
    )
    parser.add_argument(
        "--baseline-recipe",
        default=None,
        help="Optional recipe name to treat as the baseline for delta metrics and baseline-relative findings. Defaults to rotating_opponents_holdout_endpoint when present.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to write the phase-4 report into. Defaults to <runs-root>/causal_analysis_<timestamp>.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    if args.recipe_root:
        recipe_roots = [(project_root / item).resolve() if not Path(item).is_absolute() else Path(item).resolve() for item in args.recipe_root]
    else:
        root = ((project_root / args.runs_root).resolve() if not Path(args.runs_root).is_absolute() else Path(args.runs_root).resolve())
        recipe_roots = _discover_recipe_roots(root)
    if len(recipe_roots) < 2:
        raise ValueError("At least two recipe roots are required for causal transfer comparison.")

    summary = build_summary(recipe_roots, baseline_recipe_name=str(args.baseline_recipe) if args.baseline_recipe else None)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_output = Path(args.output_dir).resolve() if args.output_dir else (recipe_roots[0].parent / f"causal_analysis_{timestamp}")
    base_output.mkdir(parents=True, exist_ok=True)

    (base_output / "causal_transfer_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    report = _render_markdown(summary)
    (base_output / "causal_transfer_report.md").write_text(report, encoding="utf-8")
    write_pdf_report(
        path=base_output / "causal_transfer_report.pdf",
        run_name=base_output.name,
        markdown_report=report,
        suite_summary={},
        condition_payloads=[],
    )
    print(f"Wrote causal transfer artifacts to: {base_output}")


if __name__ == "__main__":
    main()
