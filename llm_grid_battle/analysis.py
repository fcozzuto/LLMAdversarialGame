from __future__ import annotations

from collections import defaultdict
import difflib
import json
import statistics
from typing import Any


POLICY_SNIPPETS = (
    "import ",
    "__",
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


def normalize_code(code: str) -> str:
    lines = []
    for line in code.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return " ".join(lines)


def code_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normalize_code(a), normalize_code(b)).ratio()


def strategy_tags(code: str) -> list[str]:
    lowered = code.lower()
    tags: set[str] = set()
    if "opponent_position" in lowered or "opponent_" in lowered:
        tags.add("opponent_aware")
    if "sorted(" in lowered or ".sort(" in lowered:
        tags.add("global_sort")
    if "min(" in lowered and "resources" in lowered:
        tags.add("nearest_resource")
    if "queue" in lowered or "deque" in lowered or "heapq" in lowered:
        tags.add("graph_search")
    if "self_path" in lowered or "visited" in lowered or "memory" in lowered:
        tags.add("path_memory")
    if "grid_width" in lowered and "grid_height" in lowered and "y % 2" in lowered:
        tags.add("sweep_pattern")
    if not tags:
        tags.add("uncategorized")
    return sorted(tags)


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
    lines = ["## Deterministic Conclusion"]

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

    same_model_novelty = comparison.get("same_model_avg_novelty")
    cross_model_novelty = comparison.get("cross_model_avg_novelty")
    if same_model_novelty is not None and cross_model_novelty is not None:
        lines.append(
            f"- Novelty: same-model average novelty was {same_model_novelty}, versus {cross_model_novelty} for cross-model conditions in this run."
        )

    same_model_markers = comparison.get("same_model_avg_policy_markers")
    cross_model_markers = comparison.get("cross_model_avg_policy_markers")
    if same_model_markers == 0 and cross_model_markers == 0:
        lines.append("- Policy markers: none were recorded in either same-model or cross-model conditions.")
    elif same_model_markers is not None and cross_model_markers is not None:
        lines.append(
            f"- Policy markers: same-model average {same_model_markers}, cross-model average {cross_model_markers}."
        )

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

    lines.append("")
    return lines


def summarize_condition(condition_summary: dict[str, Any]) -> dict[str, Any]:
    epochs = condition_summary["epochs"]
    agents = condition_summary["agents"]
    agent_names = [agent["name"] for agent in agents]
    agent_models = {agent["name"]: _model_descriptor(agent) for agent in agents}
    agent_labels = {name: f"{name} ({agent_models[name]})" for name in agent_names}

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

    previous_codes: dict[str, str | None] = {name: None for name in agent_names}
    for epoch in epochs:
        win_counts[epoch["winner"]] += 1
        for agent_name in agent_names:
            score_series[agent_name].append(float(epoch["scores"][agent_name]))
            current_code = epoch["codes"][agent_name]
            codes_by_agent[agent_name].append(current_code)
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

    return {
        "condition_name": condition_summary["condition_name"],
        "agent_names": agent_names,
        "agent_models": agent_models,
        "agent_labels": agent_labels,
        "epoch_count": len(epochs),
        "same_model_matchup": len({(agent["provider"], agent["model"]) for agent in agents}) == 1,
        "feedback_policy": condition_summary["feedback"],
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
        "code_change_stats": code_change_stats,
        "plateau_signals": plateau_signals,
        "plateau_reasons": plateau_reasons,
    }


def summarize_suite(condition_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    condition_summaries = [summarize_condition(item) for item in condition_payloads]

    same_model = [item for item in condition_summaries if item["same_model_matchup"]]
    cross_model = [item for item in condition_summaries if not item["same_model_matchup"]]

    def _avg_novelty(items: list[dict[str, Any]]) -> float:
        values: list[float] = []
        for item in items:
            for agent in item["agent_names"]:
                values.append(float(item["novelty"][agent]["average"]))
        return round(statistics.mean(values), 4) if values else 0.0

    def _avg_policy_markers(items: list[dict[str, Any]]) -> float:
        values: list[int] = []
        for item in items:
            for agent in item["agent_names"]:
                values.append(len(item.get("policy_markers", {}).get(agent, [])))
        return round(statistics.mean(values), 3) if values else 0.0

    models_used = sorted(
        {
            _model_descriptor(agent)
            for payload in condition_payloads
            for agent in payload["agents"]
        }
    )
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
            "same_model_avg_novelty": _avg_novelty(same_model),
            "cross_model_avg_novelty": _avg_novelty(cross_model),
            "same_model_avg_policy_markers": _avg_policy_markers(same_model),
            "cross_model_avg_policy_markers": _avg_policy_markers(cross_model),
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
            lines.append(f"- {condition['agent_labels'][name]} policy markers: {', '.join(markers)}.")
    if not any_policy:
        lines.append("- No policy markers were recorded in this condition.")
    return lines


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
    lines = ["## Models Used"]
    for condition in suite_summary.get("conditions", []):
        agent_parts = [
            f"`{agent}` = `{condition['agent_models'][agent]}`"
            for agent in condition.get("agent_names", [])
        ]
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


def render_markdown_report(
    suite_summary: dict[str, Any],
    llm_report: str | None,
    run_metadata: dict[str, Any] | None = None,
) -> str:
    lines = [
        "# LLM Adversarial Grid Report",
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
            f"- Same-model conditions had average novelty {comparison['same_model_avg_novelty']}.",
            f"- Cross-model conditions had average novelty {comparison['cross_model_avg_novelty']}.",
            f"- Same-model conditions averaged {comparison.get('same_model_avg_policy_markers', comparison.get('same_model_avg_suspicion_markers', 0.0))} policy markers per agent summary.",
            f"- Cross-model conditions averaged {comparison.get('cross_model_avg_policy_markers', comparison.get('cross_model_avg_suspicion_markers', 0.0))} policy markers per agent summary.",
            "",
            "## How To Read The Score Charts",
            "- Each `scores.svg` file plots one point per epoch for each agent.",
            "- The x-axis is epoch index. The y-axis is that agent's final score at the end of the epoch, not a cumulative running total across the whole experiment.",
            "- Higher points mean the agent collected more resources in that specific epoch.",
            "- A persistent gap between lines means one agent usually finished ahead. Frequent crossings mean the matchup stayed competitive from epoch to epoch.",
            "",
            "## Per Condition",
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
        lines.extend(_format_agent_model_list(condition))
        lines.append(f"- Overall result: {_format_overall_result(condition)}")
        lines.extend(_format_generation_execution(condition))
        lines.extend(_format_novelty(condition))
        lines.extend(_format_code_change_summary(condition))
        lines.extend(_format_plateau_summary(condition))
        lines.extend(_format_runtime_summary(condition))
        lines.extend(_format_policy_summary(condition))
        lines.append(
            f"- Score chart artifact: `{condition['condition_name']}/scores.svg`."
        )
        lines.append(f"- Score chart interpretation: {_score_chart_summary(condition)}")
        lines.append(_score_chart_markdown(condition["condition_name"], run_metadata))
        lines.append("")

    lines.extend(_render_deterministic_conclusion(suite_summary))

    if llm_report:
        lines.extend(["## Judge Model Narrative", "", llm_report.strip(), ""])
    return "\n".join(lines)
