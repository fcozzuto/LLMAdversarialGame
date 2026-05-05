from __future__ import annotations

from collections import defaultdict
import json
import statistics
from typing import Any

from .behavioral_descriptors import behavioral_cell, behavioral_distance, behavioral_profile_label
from .code_fingerprints import code_similarity, normalize_code, strategy_tags


POLICY_SNIPPETS = (
    "import ",
    "__",
    "undocumented_",
    "secret_",
    "open(",
    "socket",
    "subprocess",
    "requests",
    "urllib",
    "globals(",
    "locals(",
    "eval(",
    "exec(",
)


def _truncate(text: str | None, limit: int = 240) -> str | None:
    if text is None or len(text) <= limit:
        return text
    return text[:limit] + "...[truncated]"


def _model_descriptor(agent: dict[str, Any]) -> str:
    return f"{agent['provider']}:{agent['model']}"


def policy_markers(code: str, static_issues: list[str]) -> list[str]:
    hits: set[str] = set(static_issues)
    lowered = code.lower()
    for item in POLICY_SNIPPETS:
        if item in lowered:
            hits.add(f"text:{item.strip()}")
    return sorted(hits)


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _count_consecutive_tail(codes: list[str]) -> int:
    if not codes:
        return 0
    streak = 1
    for index in range(len(codes) - 1, 0, -1):
        if codes[index] != codes[index - 1]:
            break
        streak += 1
    return streak


def _plateau_reasons(
    *,
    scores: list[float],
    novelties: list[float],
    unique_code_count: int,
    current_tail_streak: int,
) -> list[str]:
    reasons: list[str] = []
    recent_novelty = _mean(novelties[-min(3, len(novelties)) :]) if novelties else 0.0
    if current_tail_streak >= 3 and recent_novelty < 0.02:
        reasons.append("repeated_same_code_recently")

    recent_window = min(5, len(scores))
    if recent_window >= 3 and len(scores) > recent_window:
        recent_best = max(scores[-recent_window:])
        prior_best = max(scores[:-recent_window])
        if recent_best <= prior_best and _mean(novelties[-min(5, len(novelties)) :]) < 0.05:
            reasons.append("no_recent_score_improvement")

    if unique_code_count == 1 and len(scores) >= 5:
        reasons.append("single_strategy_entire_run")
    return reasons


def _opponent_name(agent_names: list[str], agent_name: str) -> str:
    for candidate in agent_names:
        if candidate != agent_name:
            return candidate
    return agent_name


def _score_margin(epoch: dict[str, Any], agent_name: str, opponent_name: str) -> float:
    return float(epoch["scores"][agent_name]) - float(epoch["scores"][opponent_name])


def _curriculum_metrics(
    *,
    epochs: list[dict[str, Any]],
    agent_names: list[str],
    agent_name: str,
) -> dict[str, Any]:
    if not epochs:
        return {
            "enabled": False,
            "loop_count": 0,
            "failed_fix_repetition_count": 0,
            "oscillation_count": 0,
            "reversion_count": 0,
            "superficial_novelty_count": 0,
            "post_loss_novelty_spike_count": 0,
            "strategy_switch_count": 0,
            "escape_from_losing_regime_count": 0,
            "specific_adaptation_count": 0,
            "generalization_hint_count": 0,
            "degradation_count": 0,
            "behavior_profiles": [],
        }

    opponent_name = _opponent_name(agent_names, agent_name)
    fingerprints = [
        str(epoch.get("code_fingerprints", {}).get(agent_name, {}).get("fingerprint", normalize_code(epoch["submitted_codes"][agent_name])))
        for epoch in epochs
    ]
    descriptors = [epoch.get("behavioral_descriptors", {}).get(agent_name, {}) for epoch in epochs]
    behavior_profiles = [behavioral_profile_label(descriptor) for descriptor in descriptors]
    behavior_cells = [behavioral_cell(descriptor) for descriptor in descriptors]
    strategy_labels = [
        tuple(epoch.get("code_fingerprints", {}).get(agent_name, {}).get("strategy_tags", []))
        for epoch in epochs
    ]
    margins = [_score_margin(epoch, agent_name, opponent_name) for epoch in epochs]
    novelties = [
        round(1.0 - code_similarity(epochs[index - 1]["submitted_codes"][agent_name], epochs[index]["submitted_codes"][agent_name]), 4)
        for index in range(1, len(epochs))
    ]
    descriptor_shifts = [
        behavioral_distance(descriptors[index - 1], descriptors[index])
        for index in range(1, len(descriptors))
    ]

    loop_count = 0
    failed_fix_repetition_count = 0
    oscillation_count = 0
    reversion_count = 0
    superficial_novelty_count = 0
    post_loss_novelty_spike_count = 0
    strategy_switch_count = 0
    escape_from_losing_regime_count = 0
    specific_adaptation_count = 0
    generalization_hint_count = 0
    degradation_count = 0

    seen_prior: set[str] = set()
    prior_margins_by_label: dict[str, float] = {}
    recent_negative_streak = 0
    for index in range(len(epochs)):
        fingerprint = fingerprints[index]
        if fingerprint in seen_prior and (index == 0 or fingerprint != fingerprints[index - 1]):
            reversion_count += 1
        seen_prior.add(fingerprint)
        if index >= 1 and fingerprint == fingerprints[index - 1]:
            loop_count += 1
            prior_margin = margins[index - 2] if index >= 2 else 0.0
            if (index >= 2 and margins[index - 1] <= prior_margin) or (index == 1 and margins[index - 1] < 0):
                failed_fix_repetition_count += 1
        if index >= 2 and fingerprints[index] == fingerprints[index - 2] and fingerprints[index] != fingerprints[index - 1]:
            oscillation_count += 1
        if index >= 1 and descriptor_shifts[index - 1] < 0.08 and novelties[index - 1] > 0.12:
            superficial_novelty_count += 1
        if index >= 1 and margins[index - 1] < 0 and novelties[index - 1] >= 0.2:
            post_loss_novelty_spike_count += 1
        if index >= 1:
            profile_changed = behavior_profiles[index] != behavior_profiles[index - 1]
            cell_changed = behavior_cells[index] != behavior_cells[index - 1]
            tags_changed = strategy_labels[index] != strategy_labels[index - 1]
            large_descriptor_shift = descriptor_shifts[index - 1] >= 0.16
            persistent = (
                index == len(epochs) - 1
                or behavior_cells[index + 1] == behavior_cells[index]
                or strategy_labels[index + 1] == strategy_labels[index]
            )
            if persistent and (cell_changed or (profile_changed and tags_changed) or (large_descriptor_shift and tags_changed)):
                strategy_switch_count += 1
        if margins[index] < 0:
            recent_negative_streak += 1
        else:
            if recent_negative_streak >= 2:
                escape_from_losing_regime_count += 1
            recent_negative_streak = 0

        opponent_label = str(epochs[index].get("curriculum", {}).get("opponent_label", ""))
        if opponent_label:
            previous_margin = prior_margins_by_label.get(opponent_label)
            if previous_margin is not None and previous_margin < 0 and margins[index] > previous_margin:
                specific_adaptation_count += 1
            prior_margins_by_label[opponent_label] = margins[index]
        selection = epochs[index].get("curriculum", {}).get("selection") or {}
        if selection:
            if not bool(selection.get("accepted", True)) and float(selection.get("behavioral_distance", 0.0) or 0.0) >= 0.2:
                degradation_count += 1
            if bool(selection.get("accepted", False)) and str(selection.get("reason")) == "diversity_gain_within_score_tolerance":
                generalization_hint_count += 1

    return {
        "enabled": bool(any(epoch.get("curriculum", {}).get("enabled") for epoch in epochs)),
        "loop_count": loop_count,
        "failed_fix_repetition_count": failed_fix_repetition_count,
        "oscillation_count": oscillation_count,
        "reversion_count": reversion_count,
        "superficial_novelty_count": superficial_novelty_count,
        "post_loss_novelty_spike_count": post_loss_novelty_spike_count,
        "strategy_switch_count": strategy_switch_count,
        "escape_from_losing_regime_count": escape_from_losing_regime_count,
        "specific_adaptation_count": specific_adaptation_count,
        "generalization_hint_count": generalization_hint_count,
        "degradation_count": degradation_count,
        "behavior_profiles": behavior_profiles,
        "behavior_cells": behavior_cells,
        "behavior_cell_count": len(set(behavior_cells)),
    }


def _condition_is_clean(condition: dict[str, Any]) -> bool:
    for agent in condition.get("agent_names", []):
        generation = condition.get("generation", {}).get(agent, {})
        execution = condition.get("execution", {}).get(agent, {})
        if int(generation.get("error_count", 0)) or int(execution.get("fallback_count", 0)):
            return False
    return True


def _condition_is_near_clean(condition: dict[str, Any]) -> bool:
    if _condition_is_clean(condition):
        return False
    agent_names = condition.get("agent_names", [])
    if not agent_names:
        return False
    min_generation_rate = min(
        float(condition.get("generation", {}).get(agent, {}).get("success_rate", 0.0))
        for agent in agent_names
    )
    min_execution_rate = min(
        float(condition.get("execution", {}).get(agent, {}).get("submitted_code_execution_rate", 0.0))
        for agent in agent_names
    )
    return min_generation_rate >= 0.99 and min_execution_rate >= 0.99


def _format_rate_fraction(rate: float, epoch_count: int) -> str:
    success_count = int(round(rate * epoch_count))
    return f"{success_count}/{epoch_count}"


def _condition_execution_rate_summary(condition: dict[str, Any]) -> str:
    epoch_count = int(condition.get("epoch_count", 0))
    agent_summaries: list[str] = []
    for agent in condition.get("agent_names", []):
        label = condition.get("agent_labels", {}).get(agent, agent)
        execution_rate = float(
            condition.get("execution", {}).get(agent, {}).get("submitted_code_execution_rate", 0.0)
        )
        agent_summaries.append(f"{label} { _format_rate_fraction(execution_rate, epoch_count) }")
    return ", ".join(agent_summaries)


def _build_notable_epochs(
    *,
    epochs: list[dict[str, Any]],
    agent_names: list[str],
    agent_labels: dict[str, str],
    codes_by_agent: dict[str, list[str]],
) -> list[dict[str, Any]]:
    if not epochs or len(agent_names) != 2:
        return []

    first, second = agent_names
    notes: list[dict[str, Any]] = []

    largest_margin_epoch = max(
        epochs,
        key=lambda epoch: abs(float(epoch["scores"][first]) - float(epoch["scores"][second])),
    )
    notes.append(
        {
            "kind": "largest_score_margin",
            "epoch_index": int(largest_margin_epoch["epoch_index"]),
            "summary": (
                f"largest score margin: {agent_labels[first]} {largest_margin_epoch['scores'][first]} "
                f"vs {agent_labels[second]} {largest_margin_epoch['scores'][second]}"
            ),
        }
    )

    runtime_heaviest = max(
        epochs,
        key=lambda epoch: sum(len(epoch.get("runtime_events", {}).get(name, [])) for name in agent_names),
    )
    runtime_total = sum(len(runtime_heaviest.get("runtime_events", {}).get(name, [])) for name in agent_names)
    if runtime_total:
        notes.append(
            {
                "kind": "runtime_heavy",
                "epoch_index": int(runtime_heaviest["epoch_index"]),
                "summary": f"most runtime issues in one epoch: {runtime_total}",
            }
        )

    fallback_epoch = next(
        (
            epoch
            for epoch in epochs
            if any(
                epoch.get("generation_used_fallback", {}).get(name)
                or epoch.get("sandbox_reports", {}).get(name, {}).get("used_fallback")
                for name in agent_names
            )
        ),
        None,
    )
    if fallback_epoch is not None:
        fallback_agents = [
            agent_labels[name]
            for name in agent_names
            if fallback_epoch.get("generation_used_fallback", {}).get(name)
            or fallback_epoch.get("sandbox_reports", {}).get(name, {}).get("used_fallback")
        ]
        notes.append(
            {
                "kind": "fallback_epoch",
                "epoch_index": int(fallback_epoch["epoch_index"]),
                "summary": f"first fallback/default-code epoch for {', '.join(fallback_agents)}",
            }
        )

    largest_code_shift: tuple[float, int] | None = None
    for epoch_offset in range(1, len(epochs)):
        novelties: list[float] = []
        for agent_name in agent_names:
            previous = codes_by_agent[agent_name][epoch_offset - 1]
            current = codes_by_agent[agent_name][epoch_offset]
            novelties.append(1.0 - code_similarity(previous, current))
        average_novelty = statistics.mean(novelties) if novelties else 0.0
        if largest_code_shift is None or average_novelty > largest_code_shift[0]:
            largest_code_shift = (average_novelty, epoch_offset)
    if largest_code_shift is not None:
        notes.append(
            {
                "kind": "largest_code_shift",
                "epoch_index": int(epochs[largest_code_shift[1]]["epoch_index"]),
                "summary": f"largest average code shift between consecutive epochs: {round(largest_code_shift[0], 4)}",
            }
        )

    replay_rejection = next(
        (
            epoch
            for epoch in epochs
            if str((epoch.get("curriculum", {}).get("selection") or {}).get("reason", "")).startswith("rejected_by_")
        ),
        None,
    )
    if replay_rejection is not None:
        notes.append(
            {
                "kind": "selection_rejection",
                "epoch_index": int(replay_rejection["epoch_index"]),
                "summary": f"first curriculum rejection by robustness checks: {(replay_rejection.get('curriculum', {}).get('selection') or {}).get('reason', 'unknown')}",
            }
        )

    diversity_accept = next(
        (
            epoch
            for epoch in epochs
            if str((epoch.get("curriculum", {}).get("selection") or {}).get("reason", "")) in {
                "opened_new_behavior_cell",
                "diversity_gain_within_score_tolerance",
                "behavioral_diversity_within_score_tolerance",
            }
        ),
        None,
    )
    if diversity_accept is not None:
        notes.append(
            {
                "kind": "diversity_accept",
                "epoch_index": int(diversity_accept["epoch_index"]),
                "summary": f"first acceptance driven by diversity logic: {(diversity_accept.get('curriculum', {}).get('selection') or {}).get('reason', 'unknown')}",
            }
        )

    return notes


def _average_score_winner(condition: dict[str, Any]) -> str | None:
    agent_names = condition.get("agent_names", [])
    if len(agent_names) != 2:
        return None
    first, second = agent_names
    average_scores = condition.get("average_scores", {})
    win_counts = condition.get("win_counts", {})
    first_score = float(average_scores.get(first, 0.0))
    second_score = float(average_scores.get(second, 0.0))
    if first_score > second_score:
        return first
    if second_score > first_score:
        return second
    return None


def _win_count_winner(condition: dict[str, Any]) -> str | None:
    agent_names = condition.get("agent_names", [])
    if len(agent_names) != 2:
        return None
    first, second = agent_names
    win_counts = condition.get("win_counts", {})
    first_wins = int(win_counts.get(first, 0))
    second_wins = int(win_counts.get(second, 0))
    if first_wins > second_wins:
        return first
    if second_wins > first_wins:
        return second
    return None


def _render_deterministic_conclusion(suite_summary: dict[str, Any]) -> list[str]:
    conditions = suite_summary.get("conditions", [])
    comparison = suite_summary.get("cross_condition_comparison", {})
    lines = ["## Deterministic Findings"]

    clean_condition_count = sum(1 for condition in conditions if _condition_is_clean(condition))
    if conditions:
        near_clean_conditions = [
            condition for condition in conditions if _condition_is_near_clean(condition)
        ]
        noisy_conditions = [
            condition
            for condition in conditions
            if not _condition_is_clean(condition) and not _condition_is_near_clean(condition)
        ]
        if clean_condition_count == len(conditions):
            lines.append(
                f"- Data quality: all {clean_condition_count}/{len(conditions)} conditions had zero generation errors and zero fallback executions."
            )
        else:
            lines.append(
                f"- Data quality: {clean_condition_count}/{len(conditions)} conditions were fully clean under the strict zero-generation-error and zero-fallback rule."
            )
            if near_clean_conditions:
                near_clean_names = ", ".join(
                    f"`{condition['condition_name']}`" for condition in near_clean_conditions
                )
                lines.append(
                    f"- Near-clean conditions: {near_clean_names}. These had only isolated failures and at least 99% submitted-code execution for every agent."
                )
            for condition in noisy_conditions:
                lines.append(
                    f"- Higher-noise condition: `{condition['condition_name']}`. Submitted-code execution rates were {_condition_execution_rate_summary(condition)}."
                )

    for condition in conditions:
        agent_names = condition.get("agent_names", [])
        average_scores = condition.get("average_scores", {})
        win_counts = condition.get("win_counts", {})
        draws = int(win_counts.get("draw", 0))
        if len(agent_names) == 2:
            score_winner = _average_score_winner(condition)
            win_winner = _win_count_winner(condition)
            first, second = agent_names
            first_label = condition.get("agent_labels", {}).get(first, first)
            second_label = condition.get("agent_labels", {}).get(second, second)
            draw_text = f", {draws} draws" if draws else ""
            if score_winner and score_winner == win_winner:
                loser = second if first == score_winner else first
                winner_label = condition.get("agent_labels", {}).get(score_winner, score_winner)
                loser_label = condition.get("agent_labels", {}).get(loser, loser)
                lines.append(
                    f"- `{condition['condition_name']}`: {winner_label} led on both average score ({average_scores[score_winner]} vs {average_scores[loser]}) and win count ({win_counts.get(score_winner, 0)} vs {win_counts.get(loser, 0)}){draw_text}."
                )
            elif score_winner or win_winner:
                score_text = (
                    f"average score favored {condition.get('agent_labels', {}).get(score_winner, score_winner)} "
                    f"({average_scores[score_winner]} vs {average_scores[second if first == score_winner else first]})"
                    if score_winner
                    else f"average scores tied ({average_scores[first]} vs {average_scores[second]})"
                )
                win_text = (
                    f"win count favored {condition.get('agent_labels', {}).get(win_winner, win_winner)} "
                    f"({win_counts.get(win_winner, 0)} vs {win_counts.get(second if first == win_winner else first, 0)})"
                    if win_winner
                    else f"win counts tied ({win_counts.get(first, 0)} vs {win_counts.get(second, 0)})"
                )
                lines.append(f"- `{condition['condition_name']}`: {score_text}, while {win_text}{draw_text}.")
            else:
                lines.append(
                    f"- `{condition['condition_name']}`: average scores tied ({average_scores[first]} vs {average_scores[second]}) and win counts tied ({win_counts.get(first, 0)} vs {win_counts.get(second, 0)}){draw_text}."
                )
        else:
            lines.append(
                f"- `{condition['condition_name']}`: no overall winner by average score and win count; average scores {json.dumps(average_scores, sort_keys=True)}, win counts {json.dumps(win_counts, sort_keys=True)}."
            )

    lines.extend(_format_matchup_comparison_summary(comparison))

    runtime_notes: list[str] = []
    for condition in conditions:
        for agent in condition.get("agent_names", []):
            issues = condition.get("runtime_issue_counts", {}).get(agent, {})
            if not issues:
                continue
            label = condition.get("agent_labels", {}).get(agent, agent)
            issue_text = ", ".join(f"{name} x{count}" for name, count in sorted(issues.items()))
            runtime_notes.append(f"{condition['condition_name']} / {label}: {issue_text}")
    if runtime_notes:
        lines.append(f"- Runtime notes: {'; '.join(runtime_notes)}.")

    curriculum_notes: list[str] = []
    for condition in conditions:
        agent_pool = [condition.get("learner_agent")] if condition.get("learner_agent") else condition.get("agent_names", [])
        for agent in agent_pool:
            if not agent:
                continue
            metrics = condition.get("curriculum_metrics", {}).get(agent, {})
            if not metrics.get("enabled"):
                continue
            curriculum_notes.append(
                f"{condition['condition_name']} / {condition['agent_labels'][agent]}: loops={metrics.get('loop_count', 0)}, oscillations={metrics.get('oscillation_count', 0)}, reversions={metrics.get('reversion_count', 0)}, post-loss spikes={metrics.get('post_loss_novelty_spike_count', 0)}, behavior-cell coverage={metrics.get('behavior_cell_count', 0)}, specific adaptations={metrics.get('specific_adaptation_count', 0)}"
            )
    if curriculum_notes:
        lines.append(f"- Curriculum notes: {'; '.join(curriculum_notes)}.")

    evaluation_notes: list[str] = []
    for condition in conditions:
        evaluation = condition.get("evaluation") or {}
        if not evaluation.get("enabled"):
            continue
        holdout_parts = [
            f"{opponent.get('label', '-')}: mean margin {opponent.get('mean_score_margin', 0.0)}"
            for opponent in evaluation.get("opponents", [])
        ]
        if holdout_parts:
            evaluation_notes.append(f"{condition['condition_name']} holdout panel -> " + ", ".join(holdout_parts))
    if evaluation_notes:
        lines.append(f"- Holdout evaluation: {'; '.join(evaluation_notes)}.")

    lines.append("")
    return lines


def summarize_condition(condition_summary: dict[str, Any]) -> dict[str, Any]:
    epochs = condition_summary["epochs"]
    agents = condition_summary["agents"]
    agent_names = [agent["name"] for agent in agents]
    agent_models = {agent["name"]: _model_descriptor(agent) for agent in agents}
    agent_labels = {name: f"{name} ({agent_models[name]})" for name in agent_names}
    agent_generation_controls = {
        agent["name"]: {"regenerate_each_epoch": bool(agent.get("regenerate_each_epoch", True))}
        for agent in agents
    }

    win_counts = defaultdict(int)
    novelty_by_agent: dict[str, list[float]] = {name: [] for name in agent_names}
    strategy_by_agent: dict[str, set[str]] = {name: set() for name in agent_names}
    policy_by_agent: dict[str, list[str]] = {name: [] for name in agent_names}
    runtime_issues_by_agent: dict[str, defaultdict[str, int]] = {
        name: defaultdict(int) for name in agent_names
    }
    score_series: dict[str, list[float]] = {name: [] for name in agent_names}
    generation_errors_by_agent: dict[str, list[str]] = {name: [] for name in agent_names}
    codes_by_agent: dict[str, list[str]] = {name: [] for name in agent_names}
    fallback_counts: dict[str, int] = {name: 0 for name in agent_names}
    descriptor_series_by_agent: dict[str, list[dict[str, float]]] = {name: [] for name in agent_names}

    previous_codes: dict[str, str | None] = {name: None for name in agent_names}
    for epoch in epochs:
        win_counts[epoch["winner"]] += 1
        for agent_name in agent_names:
            score_series[agent_name].append(float(epoch["scores"][agent_name]))
            current_code = epoch.get("submitted_codes", {}).get(agent_name, epoch["codes"][agent_name])
            codes_by_agent[agent_name].append(current_code)
            descriptor_series_by_agent[agent_name].append(epoch.get("behavioral_descriptors", {}).get(agent_name, {}))
            if previous_codes[agent_name] is not None:
                novelty = 1.0 - code_similarity(previous_codes[agent_name] or "", current_code)
                novelty_by_agent[agent_name].append(round(novelty, 4))
            previous_codes[agent_name] = current_code
            strategy_by_agent[agent_name].update(strategy_tags(current_code))
            generation_validation_issues = epoch.get("generation_validation_issues", {}).get(agent_name, [])
            policy_by_agent[agent_name].extend(
                policy_markers(
                    current_code,
                    epoch["sandbox_reports"][agent_name]["issues"]
                    + [item for item in generation_validation_issues if not item.startswith("preflight_")],
                )
            )
            for event in epoch["runtime_events"][agent_name]:
                if event:
                    runtime_issues_by_agent[agent_name][event] += 1
            error = epoch["generation_errors"][agent_name]
            if error:
                generation_errors_by_agent[agent_name].append(error)
            if epoch.get("generation_used_fallback", {}).get(agent_name) or epoch["sandbox_reports"][agent_name]["used_fallback"]:
                fallback_counts[agent_name] += 1

    code_change_stats: dict[str, dict[str, Any]] = {}
    plateau_signals: dict[str, bool] = {}
    plateau_reasons: dict[str, list[str]] = {}
    generation_summary: dict[str, dict[str, Any]] = {}
    execution_summary: dict[str, dict[str, Any]] = {}
    runtime_issue_counts: dict[str, dict[str, int]] = {}
    behavioral_summary: dict[str, dict[str, Any]] = {}
    curriculum_metrics: dict[str, dict[str, Any]] = {}
    for agent_name in agent_names:
        normalized_codes = [normalize_code(code) for code in codes_by_agent[agent_name]]
        unchanged_transitions = sum(
            1 for index in range(1, len(normalized_codes)) if normalized_codes[index] == normalized_codes[index - 1]
        )
        current_tail_streak = _count_consecutive_tail(normalized_codes)
        repeat_after_non_improve = 0
        for index in range(2, len(normalized_codes)):
            if (
                score_series[agent_name][index - 1] <= score_series[agent_name][index - 2]
                and normalized_codes[index] == normalized_codes[index - 1]
            ):
                repeat_after_non_improve += 1
        unique_code_count = len(set(normalized_codes))
        reasons = _plateau_reasons(
            scores=score_series[agent_name],
            novelties=novelty_by_agent[agent_name],
            unique_code_count=unique_code_count,
            current_tail_streak=current_tail_streak,
        )
        plateau_signals[agent_name] = bool(reasons)
        plateau_reasons[agent_name] = reasons
        code_change_stats[agent_name] = {
            "unique_codes": unique_code_count,
            "unchanged_transitions": unchanged_transitions,
            "current_unchanged_streak": current_tail_streak,
            "repeat_after_non_improve_count": repeat_after_non_improve,
        }
        error_count = len(generation_errors_by_agent[agent_name])
        generation_summary[agent_name] = {
            "success_count": len(epochs) - error_count,
            "error_count": error_count,
            "success_rate": round((len(epochs) - error_count) / len(epochs), 4) if epochs else 0.0,
            "sample_error": _truncate(generation_errors_by_agent[agent_name][0]) if error_count else None,
        }
        execution_summary[agent_name] = {
            "submitted_code_executed_count": len(epochs) - fallback_counts[agent_name],
            "fallback_count": fallback_counts[agent_name],
            "submitted_code_execution_rate": round((len(epochs) - fallback_counts[agent_name]) / len(epochs), 4)
            if epochs
            else 0.0,
        }
        runtime_issue_counts[agent_name] = dict(sorted(runtime_issues_by_agent[agent_name].items()))
        descriptor_values = descriptor_series_by_agent[agent_name]
        averaged_descriptors: dict[str, float] = {}
        if descriptor_values:
            for key in descriptor_values[0].keys():
                averaged_descriptors[key] = round(
                    statistics.mean(float(item.get(key, 0.0)) for item in descriptor_values),
                    4,
                )
        behavioral_summary[agent_name] = {
            "average_descriptor": averaged_descriptors,
            "latest_descriptor": descriptor_values[-1] if descriptor_values else {},
            "latest_profile": behavioral_profile_label(descriptor_values[-1] if descriptor_values else {}),
            "latest_cell": behavioral_cell(descriptor_values[-1] if descriptor_values else {}),
        }
        curriculum_metrics[agent_name] = _curriculum_metrics(
            epochs=epochs,
            agent_names=agent_names,
            agent_name=agent_name,
        )

    curriculum_policy = condition_summary.get("curriculum", {})
    learner_agent = str(curriculum_policy.get("focal_agent", "")) if curriculum_policy.get("enabled") else ""
    opponent_role_agent = str(curriculum_policy.get("opponent_agent", "")) if curriculum_policy.get("enabled") else ""

    def _pool_item_descriptor(item: dict[str, Any]) -> str:
        provider = str(item.get("provider") or "").strip()
        model = str(item.get("model") or "").strip()
        library_key = str(item.get("library_key") or "").strip()
        label = str(item.get("label") or "").strip()
        if provider and model:
            return f"{provider}:{model}"
        if library_key:
            return f"builtin:{library_key}"
        if label:
            return f"curriculum:{label}"
        return "curriculum:opponent_pool"

    if opponent_role_agent:
        opponent_pool = curriculum_policy.get("opponent_pool", []) or []
        if len(opponent_pool) == 1:
            descriptor = _pool_item_descriptor(opponent_pool[0])
            agent_models[opponent_role_agent] = descriptor
            agent_labels[opponent_role_agent] = f"{opponent_role_agent} ({descriptor})"
        elif len(opponent_pool) > 1:
            descriptor = f"curriculum:opponent_pool[{len(opponent_pool)}]"
            agent_models[opponent_role_agent] = descriptor
            agent_labels[opponent_role_agent] = f"{opponent_role_agent} ({descriptor})"

    notable_epochs = _build_notable_epochs(
        epochs=epochs,
        agent_names=agent_names,
        agent_labels=agent_labels,
        codes_by_agent=codes_by_agent,
    )

    return {
        "condition_name": condition_summary["condition_name"],
        "agent_names": agent_names,
        "agent_models": agent_models,
        "agent_labels": agent_labels,
        "learner_agent": learner_agent,
        "learner_label": agent_labels.get(learner_agent, learner_agent) if learner_agent else "",
        "opponent_role_agent": opponent_role_agent,
        "opponent_role_label": agent_labels.get(opponent_role_agent, opponent_role_agent) if opponent_role_agent else "",
        "agent_generation_controls": agent_generation_controls,
        "epoch_count": len(epochs),
        "same_model_matchup": len({(agent["provider"], agent["model"]) for agent in agents}) == 1,
        "feedback_policy": condition_summary["feedback"],
        "generation_policy": condition_summary.get("generation", {}),
        "observation_policy": condition_summary.get("observation", {}),
        "map_policy": condition_summary.get("map", {}),
        "curriculum_policy": curriculum_policy,
        "curriculum_pool_labels": [
            item.get("label") or item.get("library_key") or item.get("model")
            for item in curriculum_policy.get("opponent_pool", [])
        ],
        "holdout_labels": [
            item.get("label") or item.get("library_key") or item.get("model")
            for item in curriculum_policy.get("evaluation", {}).get("holdout_opponents", [])
        ],
        "metadata": condition_summary.get("metadata", {}),
        "win_counts": dict(win_counts),
        "average_scores": {
            name: round(statistics.mean(values), 3) if values else 0.0
            for name, values in score_series.items()
        },
        "final_scores": {name: score_series[name][-1] if score_series[name] else 0.0 for name in agent_names},
        "novelty": {
            name: {
                "average": round(statistics.mean(values), 4) if values else 0.0,
                "last_three_average": round(statistics.mean(values[-3:]), 4) if values else 0.0,
            }
            for name, values in novelty_by_agent.items()
        },
        "strategy_tags": {name: sorted(values) for name, values in strategy_by_agent.items()},
        "policy_markers": {name: sorted(set(values)) for name, values in policy_by_agent.items()},
        "runtime_issue_counts": runtime_issue_counts,
        "generation": generation_summary,
        "execution": execution_summary,
        "behavioral_summary": behavioral_summary,
        "curriculum_metrics": curriculum_metrics,
        "code_change_stats": code_change_stats,
        "plateau_signals": plateau_signals,
        "plateau_reasons": plateau_reasons,
        "notable_epochs": notable_epochs,
        "curriculum_trace": condition_summary.get("curriculum_trace", []),
        "archive": condition_summary.get("archive", []),
        "elite_archive": condition_summary.get("elite_archive", []),
        "evaluation": condition_summary.get("evaluation") or {},
    }


def summarize_suite(condition_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    condition_summaries = [summarize_condition(item) for item in condition_payloads]

    same_model = [item for item in condition_summaries if item["same_model_matchup"]]
    cross_model = [item for item in condition_summaries if not item["same_model_matchup"]]

    def _avg_novelty(items: list[dict[str, Any]]) -> float:
        values: list[float] = []
        for item in items:
            agent_pool = [item.get("learner_agent")] if item.get("learner_agent") else item["agent_names"]
            for agent in agent_pool:
                if not agent:
                    continue
                values.append(float(item["novelty"][agent]["average"]))
        return round(statistics.mean(values), 4) if values else 0.0

    def _avg_policy_markers(items: list[dict[str, Any]]) -> float:
        values: list[int] = []
        for item in items:
            agent_pool = [item.get("learner_agent")] if item.get("learner_agent") else item["agent_names"]
            for agent in agent_pool:
                if not agent:
                    continue
                values.append(len(item.get("policy_markers", {}).get(agent, [])))
        return round(statistics.mean(values), 3) if values else 0.0

    def _avg_curriculum_metric(items: list[dict[str, Any]], metric_name: str) -> float:
        values: list[float] = []
        for item in items:
            focal_agent = item.get("learner_agent")
            agent_pool = [focal_agent] if focal_agent else item["agent_names"]
            for agent in agent_pool:
                metrics = item.get("curriculum_metrics", {}).get(agent, {})
                if metrics.get("enabled"):
                    values.append(float(metrics.get(metric_name, 0.0)))
        return round(statistics.mean(values), 4) if values else 0.0

    def _evaluation_condition_count(items: list[dict[str, Any]]) -> int:
        return sum(1 for item in items if (item.get("evaluation") or {}).get("enabled"))

    models_used = sorted(
        {
            _model_descriptor(agent)
            for payload in condition_payloads
            for agent in payload["agents"]
        }
    )
    for payload in condition_payloads:
        curriculum = payload.get("curriculum", {})
        for item in curriculum.get("opponent_pool", []):
            provider = item.get("provider")
            model = item.get("model")
            if provider and model:
                models_used.append(f"{provider}:{model}")
        for item in curriculum.get("evaluation", {}).get("holdout_opponents", []):
            provider = item.get("provider")
            model = item.get("model")
            if provider and model:
                models_used.append(f"{provider}:{model}")
    models_used = sorted(set(models_used))
    data_quality_warnings: list[str] = []
    for condition in condition_summaries:
        for agent in condition["agent_names"]:
            generation = condition.get("generation", {}).get(agent, {})
            error_count = int(generation.get("error_count", 0))
            if error_count:
                data_quality_warnings.append(
                    f"{condition['condition_name']} / {agent} ({condition['agent_models'][agent]}) had generation errors in "
                    f"{error_count}/{condition['epoch_count']} epochs."
                )
            execution = condition.get("execution", {}).get(agent, {})
            fallback_count = int(execution.get("fallback_count", 0))
            if fallback_count:
                data_quality_warnings.append(
                    f"{condition['condition_name']} / {agent} ({condition['agent_models'][agent]}) fell back to default code in "
                    f"{fallback_count}/{condition['epoch_count']} epochs."
                )

    return {
        "models_used": models_used,
        "data_quality_warnings": data_quality_warnings,
        "conditions": condition_summaries,
        "cross_condition_comparison": {
            "same_model_condition_count": len(same_model),
            "cross_model_condition_count": len(cross_model),
            "same_model_avg_novelty": _avg_novelty(same_model),
            "cross_model_avg_novelty": _avg_novelty(cross_model),
            "same_model_avg_policy_markers": _avg_policy_markers(same_model),
            "cross_model_avg_policy_markers": _avg_policy_markers(cross_model),
            "curriculum_avg_loop_count": _avg_curriculum_metric(condition_summaries, "loop_count"),
            "curriculum_avg_oscillation_count": _avg_curriculum_metric(condition_summaries, "oscillation_count"),
            "curriculum_avg_reversion_count": _avg_curriculum_metric(condition_summaries, "reversion_count"),
            "curriculum_avg_post_loss_novelty_spikes": _avg_curriculum_metric(condition_summaries, "post_loss_novelty_spike_count"),
            "curriculum_avg_strategy_switches": _avg_curriculum_metric(condition_summaries, "strategy_switch_count"),
            "curriculum_avg_behavior_cell_coverage": _avg_curriculum_metric(condition_summaries, "behavior_cell_count"),
            "curriculum_avg_specific_adaptation": _avg_curriculum_metric(condition_summaries, "specific_adaptation_count"),
            "curriculum_avg_degradation": _avg_curriculum_metric(condition_summaries, "degradation_count"),
            "evaluation_condition_count": _evaluation_condition_count(condition_summaries),
        },
    }


def _format_feedback_policy(policy: dict[str, Any]) -> str:
    parts: list[str] = []
    if policy.get("include_scores"):
        parts.append("scores")
    if policy.get("include_grid_state"):
        parts.append("initial resources and obstacles")
    if policy.get("include_paths"):
        parts.append("paths")
    if policy.get("include_runtime_events"):
        parts.append("runtime events")
    if policy.get("include_codes"):
        if policy.get("include_opponent_code"):
            parts.append("both agents' code")
        else:
            parts.append("self code")
    if not parts:
        return "no prior-epoch feedback"
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def _format_agent_model_list(condition: dict[str, Any]) -> list[str]:
    return [
        f"- {name}: {condition['agent_models'][name]}"
        for name in condition.get("agent_names", [])
    ]


def _format_matchup_comparison_summary(comparison: dict[str, Any]) -> list[str]:
    same_count = int(comparison.get("same_model_condition_count", 0))
    cross_count = int(comparison.get("cross_model_condition_count", 0))
    same_novelty = comparison.get("same_model_avg_novelty")
    cross_novelty = comparison.get("cross_model_avg_novelty")
    same_markers = comparison.get(
        "same_model_avg_policy_markers",
        comparison.get("same_model_avg_suspicion_markers", 0.0),
    )
    cross_markers = comparison.get(
        "cross_model_avg_policy_markers",
        comparison.get("cross_model_avg_suspicion_markers", 0.0),
    )
    lines: list[str] = []
    if same_count and cross_count:
        lines.append(f"- Same-model conditions had average novelty {same_novelty}.")
        lines.append(f"- Cross-model conditions had average novelty {cross_novelty}.")
        lines.append(
            f"- Same-model conditions averaged {same_markers} potential rule-violation indicators per agent summary."
        )
        lines.append(
            f"- Cross-model conditions averaged {cross_markers} potential rule-violation indicators per agent summary."
        )
    elif cross_count:
        lines.append(
            f"- This run contains only cross-model conditions. Cross-model average novelty was {cross_novelty}."
        )
        lines.append(
            f"- Cross-model conditions averaged {cross_markers} potential rule-violation indicators per agent summary."
        )
    elif same_count:
        lines.append(
            f"- This run contains only same-model conditions. Same-model average novelty was {same_novelty}."
        )
        lines.append(
            f"- Same-model conditions averaged {same_markers} potential rule-violation indicators per agent summary."
        )
    else:
        lines.append("- No same-model versus cross-model comparison is available for this run.")
    return lines


def _clean_judge_report(llm_report: str) -> str:
    cleaned = llm_report.strip()
    if cleaned.startswith("```"):
        fence_lines = cleaned.splitlines()
        if fence_lines and fence_lines[0].startswith("```"):
            fence_lines = fence_lines[1:]
        if fence_lines and fence_lines[-1].strip().startswith("```"):
            fence_lines = fence_lines[:-1]
        cleaned = "\n".join(fence_lines).strip()
    replacements = {
        "≈": "~",
        "—": "-",
        "–": "-",
        "“": "\"",
        "”": "\"",
        "’": "'",
        "‘": "'",
        "…": "...",
        "â‰ˆ": "~",
        "â€”": "-",
        "â€“": "-",
        "â€œ": "\"",
        "â€": "\"",
        "â€™": "'",
        "â€˜": "'",
        "â€¦": "...",
        "Â": "",
    }
    for source, target in replacements.items():
        cleaned = cleaned.replace(source, target)
    trailing_lines = cleaned.splitlines()
    while trailing_lines and trailing_lines[-1].strip().startswith("```"):
        trailing_lines.pop()
    cleaned = "\n".join(trailing_lines).strip()
    return cleaned.strip()


def _format_overall_result(condition: dict[str, Any]) -> str:
    agent_names = condition.get("agent_names", [])
    if len(agent_names) != 2:
        return "Overall result was not a two-agent comparison."
    first, second = agent_names
    score_winner = _average_score_winner(condition)
    win_winner = _win_count_winner(condition)
    average_scores = condition["average_scores"]
    win_counts = condition["win_counts"]
    draws = int(win_counts.get("draw", 0))
    draw_text = f" with {draws} draws" if draws else ""
    if score_winner and score_winner == win_winner:
        loser = second if first == score_winner else first
        return (
            f"{condition['agent_labels'][score_winner]} led on both average score "
            f"({average_scores[score_winner]} vs {average_scores[loser]}) and win count "
            f"({win_counts.get(score_winner, 0)} vs {win_counts.get(loser, 0)}){draw_text}."
        )
    if score_winner or win_winner:
        score_text = (
            f"Average score favored {condition['agent_labels'][score_winner]} "
            f"({average_scores[score_winner]} vs {average_scores[second if first == score_winner else first]})."
            if score_winner
            else f"Average scores tied at {average_scores[first]} and {average_scores[second]}."
        )
        win_text = (
            f"Win count favored {condition['agent_labels'][win_winner]} "
            f"({win_counts.get(win_winner, 0)} vs {win_counts.get(second if first == win_winner else first, 0)}){draw_text}."
            if win_winner
            else f"Win counts tied at {win_counts.get(first, 0)} and {win_counts.get(second, 0)}{draw_text}."
        )
        return f"{score_text} {win_text}"
    return (
        f"Average scores tied at {average_scores[first]} and {average_scores[second]}, and win counts also tied at "
        f"{win_counts.get(first, 0)} and {win_counts.get(second, 0)}{draw_text}."
    )


def _format_generation_execution(condition: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    epoch_count = int(condition.get("epoch_count", 0))
    for name in condition.get("agent_names", []):
        generation = condition.get("generation", {}).get(name, {})
        execution = condition.get("execution", {}).get(name, {})
        lines.append(
            f"- {condition['agent_labels'][name]} generated valid code in {generation.get('success_count', epoch_count)}/{epoch_count} epochs and executed submitted code in {execution.get('submitted_code_executed_count', epoch_count)}/{epoch_count} epochs."
        )
    return lines


def _format_novelty(condition: dict[str, Any]) -> list[str]:
    return [
        f"- {condition['agent_labels'][name]} had average code novelty {condition['novelty'][name]['average']} and last-three-epoch novelty {condition['novelty'][name]['last_three_average']}."
        for name in condition.get("agent_names", [])
    ]


def _format_behavioral_summary(condition: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for name in condition.get("agent_names", []):
        behavior = condition.get("behavioral_summary", {}).get(name, {})
        descriptor = behavior.get("average_descriptor", {})
        if not descriptor:
            continue
        lines.append(
            f"- {condition['agent_labels'][name]} behavioral profile averaged stay={descriptor.get('stay_ratio', 0.0)}, exploration={descriptor.get('exploration_ratio', 0.0)}, revisit={descriptor.get('revisit_ratio', 0.0)}, resource pursuit={descriptor.get('resource_pursuit_ratio', 0.0)}, opponent pursuit={descriptor.get('opponent_pursuit_ratio', 0.0)}, and opponent distance={descriptor.get('mean_opponent_distance', 0.0)}. Latest profile: {behavior.get('latest_profile', 'unknown')}."
        )
    return lines


def _format_code_change_summary(condition: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for name in condition.get("agent_names", []):
        stats = condition.get("code_change_stats", {}).get(name, {})
        unique_codes = stats.get("unique_codes", 0)
        unchanged = stats.get("unchanged_transitions", 0)
        streak = stats.get("current_unchanged_streak", 0)
        repeat_after_non_improve = stats.get("repeat_after_non_improve_count", 0)
        lines.append(
            f"- {condition['agent_labels'][name]} produced {unique_codes} unique normalized code variants, with {unchanged} unchanged transitions, current unchanged streak {streak}, and {repeat_after_non_improve} repeats after non-improving epochs."
        )
    return lines


def _format_plateau_summary(condition: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for name in condition.get("agent_names", []):
        reasons = condition.get("plateau_reasons", {}).get(name, [])
        if reasons:
            lines.append(f"- {condition['agent_labels'][name]} showed plateau signals: {', '.join(reasons)}.")
        else:
            lines.append(f"- {condition['agent_labels'][name]} showed no plateau signal under the current heuristics.")
    return lines


def _format_runtime_summary(condition: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    any_runtime = False
    for name in condition.get("agent_names", []):
        issues = condition.get("runtime_issue_counts", {}).get(name, {})
        if issues:
            any_runtime = True
            issue_text = ", ".join(f"{issue} x{count}" for issue, count in issues.items())
            lines.append(f"- {condition['agent_labels'][name]} runtime issues: {issue_text}.")
    if not any_runtime:
        lines.append("- No runtime issues were recorded in executed code for this condition.")
    return lines


def _format_policy_summary(condition: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    any_policy = False
    for name in condition.get("agent_names", []):
        markers = condition.get("policy_markers", {}).get(name, [])
        if markers:
            any_policy = True
            lines.append(f"- {condition['agent_labels'][name]} potential rule-violation indicators: {', '.join(markers)}.")
    if not any_policy:
        lines.append("- No potential rule-violation indicators were recorded in this condition.")
    return lines


def _format_generation_policy(condition: dict[str, Any]) -> list[str]:
    policy = condition.get("generation_policy", {})
    pre_execution = bool(policy.get("pre_execution_validation", True))
    repair = bool(policy.get("repair_invalid_submissions", True))
    lines = [
        f"- Generation scaffold: pre-execution validation was {'enabled' if pre_execution else 'disabled'}, and repair retries were {'enabled' if repair else 'disabled'}."
    ]
    frozen_agents = [
        condition["agent_labels"][name]
        for name, control in condition.get("agent_generation_controls", {}).items()
        if not control.get("regenerate_each_epoch", True)
    ]
    if frozen_agents:
        lines.append(
            f"- Adaptation control: {', '.join(frozen_agents)} reused prior code after epoch 1 instead of regenerating each epoch."
        )
    return lines


def _format_curriculum_summary(condition: dict[str, Any]) -> list[str]:
    curriculum = condition.get("curriculum_policy", {})
    if not curriculum or not curriculum.get("enabled"):
        return []
    lines = [
        f"- Curriculum design: mode={curriculum.get('mode', 'none')}, learner={condition.get('learner_label', curriculum.get('focal_agent', '-'))}, opponent role={condition.get('opponent_role_label', curriculum.get('opponent_agent', '-'))}, rotation policy={curriculum.get('rotation_policy', 'cyclic')}."
    ]
    pool_labels = [label for label in condition.get("curriculum_pool_labels", []) if label]
    if pool_labels:
        lines.append(f"- Opponent pool: {', '.join(pool_labels)}.")
    selection = curriculum.get("selection", {})
    if selection:
        lines.append(
            f"- Acceptance rule: mode={selection.get('mode', 'accept_all')}, novelty threshold={selection.get('novelty_threshold', 0.0)}, elite-distance threshold={selection.get('elite_distance_threshold', 0.0)}, score tolerance={selection.get('score_tolerance', 0.0)}."
        )
        if selection.get("replay_opponent_count", 0):
            lines.append(
                f"- Replay-aware selection: candidate policies were rechecked against up to {selection.get('replay_opponent_count', 0)} archived opponents before acceptance."
            )
        if selection.get("holdout_opponent_count", 0):
            lines.append(
                f"- Holdout-aware selection: candidate policies were spot-checked against {selection.get('holdout_opponent_count', 0)} held-out opponents before acceptance."
            )
    archive = curriculum.get("archive", {})
    if archive and archive.get("enabled"):
        lines.append(
            f"- Nemesis archive: reintroduce_every={archive.get('reintroduce_every', 0)}, min_score_margin={archive.get('min_score_margin', 0.0)}, max_size={archive.get('max_size', 0)}."
        )
    pressure = curriculum.get("pressure", {})
    if pressure and pressure.get("enabled"):
        lines.append(
            f"- Loss-triggered mutation pressure: loss-streak trigger={pressure.get('loss_streak_trigger', 0)}, stagnation trigger={pressure.get('stagnation_epoch_trigger', 0)}, cooldown={pressure.get('cooldown_epochs', 0)}, score-margin trigger={pressure.get('score_margin_trigger', 0.0)}."
        )
    for name in condition.get("agent_names", []):
        metrics = condition.get("curriculum_metrics", {}).get(name, {})
        if not metrics.get("enabled"):
            continue
        if condition.get("learner_agent") and name != condition.get("learner_agent"):
            continue
        role_prefix = "Learner" if name == condition.get("learner_agent") else condition["agent_labels"][name]
        lines.append(
            f"- {role_prefix} curriculum metrics: loops={metrics.get('loop_count', 0)}, oscillations={metrics.get('oscillation_count', 0)}, reversions={metrics.get('reversion_count', 0)}, post-loss novelty spikes={metrics.get('post_loss_novelty_spike_count', 0)}, stable strategy switches={metrics.get('strategy_switch_count', 0)}, behavior-cell coverage={metrics.get('behavior_cell_count', 0)}, specific adaptations={metrics.get('specific_adaptation_count', 0)}, degradation signals={metrics.get('degradation_count', 0)}."
        )
    archive_entries = condition.get("archive", [])
    if archive_entries:
        lines.append(f"- Archive snapshots stored: {len(archive_entries)}.")
    elite_entries = condition.get("elite_archive", [])
    if elite_entries:
        lines.append(f"- Focal elite archive coverage: {len(elite_entries)} behavior cells.")
    holdout_labels = [label for label in condition.get("holdout_labels", []) if label]
    if holdout_labels:
        lines.append(f"- Holdout panel opponents: {', '.join(holdout_labels)}.")
    return lines


def _format_evaluation_summary(condition: dict[str, Any]) -> list[str]:
    evaluation = condition.get("evaluation") or {}
    if not evaluation.get("enabled"):
        return []
    lines = [
        f"- Held-out evaluation: {evaluation.get('games_per_opponent', 0)} games per opponent for learner `{evaluation.get('focal_agent', '-')}`."
    ]
    for opponent in evaluation.get("opponents", []):
        lines.append(
            f"- Holdout `{opponent.get('label', '-')}` ({opponent.get('provider', '-')}:`{opponent.get('model', '-')}`): mean score {opponent.get('mean_score', 0.0)}, mean margin {opponent.get('mean_score_margin', 0.0)}, win rate {opponent.get('win_rate', 0.0)}."
        )
    return lines


def _format_research_metadata(condition: dict[str, Any]) -> list[str]:
    metadata = condition.get("metadata", {})
    if not metadata:
        return []
    rendered = ", ".join(f"{key}={value}" for key, value in sorted(metadata.items()))
    return [f"- Research tags: {rendered}."]


def _format_notable_epochs(condition: dict[str, Any]) -> list[str]:
    notable = condition.get("notable_epochs", [])
    if not notable:
        return []
    return [
        f"- Suggested qualitative follow-up, epoch {item['epoch_index']}: {item['summary']}. Artifact: `{condition['condition_name']}/epochs/epoch_{int(item['epoch_index']):03d}/artifact.json`."
        for item in notable
    ]


def _score_chart_summary(condition: dict[str, Any]) -> str:
    score_winner = _average_score_winner(condition)
    win_winner = _win_count_winner(condition)
    runtime_issue_total = sum(
        sum(counts.values()) for counts in condition.get("runtime_issue_counts", {}).values()
    )
    if score_winner and score_winner == win_winner:
        base = (
            f"The chart should show {condition['agent_labels'][score_winner]} finishing above the opponent more often than not."
        )
    elif score_winner or win_winner:
        base = "The chart should look mixed: one agent edges out average score while the other wins slightly more individual epochs."
    else:
        base = "The chart should look very balanced, with no clear long-run leader."
    if runtime_issue_total:
        base += " Runtime failures in this condition likely correspond to the most lopsided or irregular epochs."
    return base


def _score_chart_markdown(condition_name: str, run_metadata: dict[str, Any] | None) -> str:
    del run_metadata
    return f"![{condition_name} score chart]({condition_name}/scores.png)"


def _render_models_used(
    suite_summary: dict[str, Any],
    run_metadata: dict[str, Any] | None,
) -> list[str]:
    lines = ["## Models and Roles"]
    for condition in suite_summary.get("conditions", []):
        agent_parts = []
        for agent in condition.get("agent_names", []):
            role = ""
            if agent == condition.get("learner_agent"):
                role = " (learner)"
            elif agent == condition.get("opponent_role_agent"):
                role = " (curriculum opponent)"
            agent_parts.append(f"`{agent}`{role} = `{condition['agent_models'][agent]}`")
        if agent_parts:
            lines.append(f"- `{condition['condition_name']}`: {', '.join(agent_parts)}.")
    judge_descriptor = None
    if run_metadata:
        provider = run_metadata.get("judge_provider")
        model = run_metadata.get("judge_model")
        if provider and model:
            judge_descriptor = f"{provider}:{model}"
    if judge_descriptor:
        lines.append(f"- `judge`: `{judge_descriptor}`.")
    elif run_metadata and run_metadata.get("judge_status") == "skipped":
        lines.append("- `judge`: skipped for this run.")
    lines.append("")
    return lines


def _render_research_caveats(suite_summary: dict[str, Any]) -> list[str]:
    conditions = suite_summary.get("conditions", [])
    noisy_conditions = [condition["condition_name"] for condition in conditions if not _condition_is_clean(condition)]
    lines = [
        "## Threats To Validity",
        "- Code novelty is a normalized lexical change metric. The curriculum reports now add behavioral descriptors, but those descriptors are still heuristic summaries rather than full policy semantics.",
        "- Policy markers are heuristic indicators of potential rule violations; they are not proof of cheating or malicious intent.",
        "- Looping, exploration, and pressure-response metrics are heuristic operationalizations of the supervisor-facing concepts, so they should be interpreted alongside qualitative epoch inspection rather than as perfect ground truth.",
        "- Acceptance-time replay checks and holdout spot checks are small-sample robustness probes. They improve selection discipline, but they are not substitutes for the final held-out evaluation panel.",
        "- Results from a single run should be treated as provisional until replicated across additional seeds and repeated runs with cross-run statistics.",
        "- Conclusions are specific to this grid-game environment, the chosen prompts, and the configured model pairings; they do not automatically generalize to other tasks.",
    ]
    if noisy_conditions:
        lines.append(
            f"- Conditions with generation errors or fallback executions ({', '.join(f'`{name}`' for name in noisy_conditions)}) weaken causal claims and should be weighted less heavily than cleaner conditions."
        )
    lines.append("")
    return lines


def render_markdown_report(
    suite_summary: dict[str, Any],
    llm_report: str | None,
    run_metadata: dict[str, Any] | None = None,
) -> str:
    lines = [
        "# Research Report: LLM Adversarial Grid Experiment",
        "",
    ]

    if run_metadata:
        lines.extend(
            [
                "## Run Metadata",
                f"- Run ID: {run_metadata.get('run_name', '-')}",
                f"- Started: {run_metadata.get('started_at_local', '-')}",
                f"- Finished: {run_metadata.get('finished_at_local', '-')}",
                f"- Duration: {run_metadata.get('duration_hhmm', '-')}",
                "",
            ]
        )

    lines.extend(_render_models_used(suite_summary, run_metadata))
    lines.extend(_render_research_caveats(suite_summary))

    data_quality_warnings = suite_summary.get("data_quality_warnings", [])
    if data_quality_warnings:
        lines.extend(
            [
                "## Data Quality Warnings",
                *[f"- {item}" for item in data_quality_warnings],
                "",
            ]
        )

    lines.append("## Cross-Condition Summary")
    comparison = suite_summary["cross_condition_comparison"]
    lines.extend(
        [
            *_format_matchup_comparison_summary(comparison),
            f"- Learner-centric curriculum metrics across enabled conditions: average loops {comparison.get('curriculum_avg_loop_count', 0.0)}, oscillations {comparison.get('curriculum_avg_oscillation_count', 0.0)}, reversions {comparison.get('curriculum_avg_reversion_count', 0.0)}, post-loss novelty spikes {comparison.get('curriculum_avg_post_loss_novelty_spikes', 0.0)}, stable strategy switches {comparison.get('curriculum_avg_strategy_switches', 0.0)}, behavior-cell coverage {comparison.get('curriculum_avg_behavior_cell_coverage', 0.0)}, specific adaptations {comparison.get('curriculum_avg_specific_adaptation', 0.0)}, degradation signals {comparison.get('curriculum_avg_degradation', 0.0)}.",
            f"- Holdout evaluation conditions present in this run: {comparison.get('evaluation_condition_count', 0)}.",
            "",
            "## How To Read The Score Charts",
            "- Each `scores.svg` file plots one point per epoch for each agent.",
            "- The x-axis is epoch index. The y-axis is that agent's final score at the end of the epoch, not a cumulative running total across the whole experiment.",
            "- Higher points mean the agent collected more resources in that specific epoch.",
            "- A persistent gap between lines means one agent usually finished ahead. Frequent crossings mean the matchup stayed competitive from epoch to epoch.",
            "",
            "## Condition Results",
        ]
    )

    for condition in suite_summary["conditions"]:
        lines.append(f"### {condition['condition_name']}")
        lines.append(
            f"- Matchup type: {'same-model' if condition['same_model_matchup'] else 'cross-model'}."
        )
        lines.append(
            f"- Feedback visibility: { _format_feedback_policy(condition.get('feedback_policy', {})) }."
        )
        lines.extend(_format_research_metadata(condition))
        lines.extend(_format_agent_model_list(condition))
        lines.extend(_format_generation_policy(condition))
        lines.extend(_format_curriculum_summary(condition))
        lines.append(f"- Overall result: {_format_overall_result(condition)}")
        lines.extend(_format_generation_execution(condition))
        lines.extend(_format_novelty(condition))
        lines.extend(_format_behavioral_summary(condition))
        lines.extend(_format_code_change_summary(condition))
        lines.extend(_format_plateau_summary(condition))
        lines.extend(_format_runtime_summary(condition))
        lines.extend(_format_policy_summary(condition))
        lines.extend(_format_evaluation_summary(condition))
        lines.extend(_format_notable_epochs(condition))
        lines.append(
            f"- Score chart artifact: `{condition['condition_name']}/scores.svg`."
        )
        lines.append(f"- Score chart interpretation: {_score_chart_summary(condition)}")
        lines.append(_score_chart_markdown(condition["condition_name"], run_metadata))
        lines.append("")

    lines.extend(_render_deterministic_conclusion(suite_summary))

    if llm_report:
        lines.extend(["## Judge Model Commentary", "", _clean_judge_report(llm_report), ""])
    return "\n".join(lines)
