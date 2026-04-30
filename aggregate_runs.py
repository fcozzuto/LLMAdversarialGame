from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import statistics
from typing import Any

from llm_grid_battle.pdf_report import write_pdf_report
from llm_grid_battle.visualization import write_grouped_bar_chart_png


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _condition_is_clean(condition: dict[str, Any]) -> bool:
    for agent in condition.get("agent_names", []):
        generation = condition.get("generation", {}).get(agent, {})
        execution = condition.get("execution", {}).get(agent, {})
        if int(generation.get("error_count", 0)) or int(execution.get("fallback_count", 0)):
            return False
    return True


def _format_stat(label: str, stats: dict[str, Any]) -> str:
    return (
        f"{label} mean {stats['mean']} "
        f"(std {stats['stddev']}, 95% CI {stats['ci95_low']} to {stats['ci95_high']})"
    )


def _has_samples(stats: dict[str, Any]) -> bool:
    return int(stats.get("count", 0)) > 0


def _ci_overlaps(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return not (
        float(left["ci95_high"]) < float(right["ci95_low"])
        or float(right["ci95_high"]) < float(left["ci95_low"])
    )


def _display_condition_name(condition_name: str) -> str:
    mapping = {
        "same_model_full_feedback": "Same-model full feedback",
        "cross_model_full_feedback": "Cross-model full feedback",
        "same_model_limited_feedback": "Same-model limited feedback",
    }
    return mapping.get(condition_name, condition_name.replace("_", " "))


def _discover_run_dirs(runs_root: Path, explicit: list[str] | None, pattern: str) -> list[Path]:
    if explicit:
        return [Path(item).resolve() for item in explicit]
    return sorted(path.resolve() for path in runs_root.glob(pattern) if path.is_dir())


def aggregate_run_dirs(run_dirs: list[Path]) -> dict[str, Any]:
    bundles: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        suite_summary_path = run_dir / "suite_summary.json"
        if not suite_summary_path.exists():
            continue
        bundle = {
            "run_name": run_dir.name,
            "run_dir": str(run_dir),
            "run_metadata": _load_json(run_dir / "run_metadata.json") if (run_dir / "run_metadata.json").exists() else {},
            "suite_summary": _load_json(suite_summary_path),
        }
        bundles.append(bundle)

    by_condition: dict[str, list[dict[str, Any]]] = {}
    same_model_novelty_values: list[float] = []
    cross_model_novelty_values: list[float] = []
    same_model_policy_values: list[float] = []
    cross_model_policy_values: list[float] = []
    suite_families: set[str] = set()
    suite_types: set[str] = set()
    for bundle in bundles:
        conditions = bundle["suite_summary"].get("conditions", [])
        has_same_model = any(bool(condition.get("same_model_matchup", False)) for condition in conditions)
        has_cross_model = any(not bool(condition.get("same_model_matchup", False)) for condition in conditions)
        comparison = bundle["suite_summary"].get("cross_condition_comparison", {})
        if has_same_model and "same_model_avg_novelty" in comparison:
            same_model_novelty_values.append(float(comparison["same_model_avg_novelty"]))
        if has_cross_model and "cross_model_avg_novelty" in comparison:
            cross_model_novelty_values.append(float(comparison["cross_model_avg_novelty"]))
        if has_same_model and "same_model_avg_policy_markers" in comparison:
            same_model_policy_values.append(float(comparison["same_model_avg_policy_markers"]))
        if has_cross_model and "cross_model_avg_policy_markers" in comparison:
            cross_model_policy_values.append(float(comparison["cross_model_avg_policy_markers"]))
        for condition in conditions:
            metadata = condition.get("metadata", {})
            suite_family = metadata.get("suite_family")
            suite_type = metadata.get("suite_type")
            if isinstance(suite_family, str) and suite_family:
                suite_families.add(suite_family)
            if isinstance(suite_type, str) and suite_type:
                suite_types.add(suite_type)
            by_condition.setdefault(str(condition["condition_name"]), []).append(
                {"run_name": bundle["run_name"], "condition": condition}
            )

    condition_summaries: list[dict[str, Any]] = []
    for condition_name, entries in sorted(by_condition.items()):
        sample = entries[0]["condition"]
        agent_names = list(sample.get("agent_names", []))
        condition_summary: dict[str, Any] = {
            "condition_name": condition_name,
            "run_count": len(entries),
            "agent_names": agent_names,
            "agent_labels": sample.get("agent_labels", {}),
            "agent_models": sample.get("agent_models", {}),
            "same_model_matchup": bool(sample.get("same_model_matchup", False)),
            "metadata_examples": [],
            "clean_run_count": sum(1 for entry in entries if _condition_is_clean(entry["condition"])),
            "average_scores": {},
            "win_shares": {},
            "generation_success_rate": {},
            "execution_rate": {},
            "novelty": {},
            "policy_marker_count": {},
        }
        metadata_values = {
            json.dumps(entry["condition"].get("metadata", {}), sort_keys=True)
            for entry in entries
            if entry["condition"].get("metadata")
        }
        if metadata_values:
            condition_summary["metadata_examples"] = [json.loads(item) for item in sorted(metadata_values)]

        for agent_name in agent_names:
            condition_summary["average_scores"][agent_name] = _stat_summary(
                [float(entry["condition"]["average_scores"][agent_name]) for entry in entries]
            )
            condition_summary["generation_success_rate"][agent_name] = _stat_summary(
                [float(entry["condition"]["generation"][agent_name]["success_rate"]) for entry in entries],
                lower_bound=0.0,
                upper_bound=1.0,
            )
            condition_summary["execution_rate"][agent_name] = _stat_summary(
                [float(entry["condition"]["execution"][agent_name]["submitted_code_execution_rate"]) for entry in entries],
                lower_bound=0.0,
                upper_bound=1.0,
            )
            condition_summary["novelty"][agent_name] = _stat_summary(
                [float(entry["condition"]["novelty"][agent_name]["average"]) for entry in entries]
            )
            condition_summary["policy_marker_count"][agent_name] = _stat_summary(
                [float(len(entry["condition"].get("policy_markers", {}).get(agent_name, []))) for entry in entries],
                lower_bound=0.0,
            )

        for outcome_name in [*agent_names, "draw"]:
            win_share_values: list[float] = []
            for entry in entries:
                epoch_count = max(1, int(entry["condition"].get("epoch_count", 0)))
                wins = int(entry["condition"].get("win_counts", {}).get(outcome_name, 0))
                win_share_values.append(wins / epoch_count)
            condition_summary["win_shares"][outcome_name] = _stat_summary(
                win_share_values,
                lower_bound=0.0,
                upper_bound=1.0,
            )

        condition_summaries.append(condition_summary)

    return {
        "run_count": len(bundles),
        "run_names": [bundle["run_name"] for bundle in bundles],
        "run_directories": [bundle["run_dir"] for bundle in bundles],
        "condition_count": len(condition_summaries),
        "suite_families": sorted(suite_families),
        "suite_types": sorted(suite_types),
        "has_same_model_conditions": any(bool(condition.get("same_model_matchup", False)) for condition in condition_summaries),
        "has_cross_model_conditions": any(not bool(condition.get("same_model_matchup", False)) for condition in condition_summaries),
        "cross_run_summary": {
            "same_model_avg_novelty": _stat_summary(same_model_novelty_values),
            "cross_model_avg_novelty": _stat_summary(cross_model_novelty_values),
            "same_model_avg_policy_markers": _stat_summary(same_model_policy_values, lower_bound=0.0),
            "cross_model_avg_policy_markers": _stat_summary(cross_model_policy_values, lower_bound=0.0),
        },
        "conditions": condition_summaries,
    }


def _condition_by_name(aggregate_summary: dict[str, Any], name: str) -> dict[str, Any] | None:
    for condition in aggregate_summary.get("conditions", []):
        if condition.get("condition_name") == name:
            return condition
    return None


def _min_rate(condition: dict[str, Any], metric_name: str) -> float:
    agent_names = condition.get("agent_names", [])
    if not agent_names:
        return 0.0
    return min(float(condition[metric_name][agent_name]["mean"]) for agent_name in agent_names)


def _condition_quality_label(condition: dict[str, Any]) -> str:
    run_count = int(condition.get("run_count", 0))
    clean_run_count = int(condition.get("clean_run_count", 0))
    if run_count and clean_run_count == run_count:
        return "fully clean"
    if _min_rate(condition, "generation_success_rate") >= 0.99 and _min_rate(condition, "execution_rate") >= 0.99:
        return "near-clean"
    return "higher-noise"


def _agent_display(condition: dict[str, Any], agent_name: str) -> str:
    return str(condition.get("agent_labels", {}).get(agent_name, agent_name))


def _cross_model_winner_line(condition: dict[str, Any]) -> str | None:
    agent_names = condition.get("agent_names", [])
    if len(agent_names) != 2:
        return None
    left, right = agent_names
    left_score = condition["average_scores"][left]
    right_score = condition["average_scores"][right]
    left_wins = condition["win_shares"][left]
    right_wins = condition["win_shares"][right]
    if float(left_score["mean"]) == float(right_score["mean"]):
        return None
    winner = left if float(left_score["mean"]) > float(right_score["mean"]) else right
    loser = right if winner == left else left
    winner_score = condition["average_scores"][winner]
    loser_score = condition["average_scores"][loser]
    winner_wins = condition["win_shares"][winner]
    loser_wins = condition["win_shares"][loser]
    overlap = _ci_overlaps(winner_score, loser_score) or _ci_overlaps(winner_wins, loser_wins)
    strong_evidence = int(condition.get("run_count", 0)) >= 3 and not overlap
    evidence_phrase = "consistently outperformed" if strong_evidence else "directionally outperformed"
    return (
        f"- In {_display_condition_name(str(condition['condition_name']))}, {_agent_display(condition, winner)} "
        f"{evidence_phrase} {_agent_display(condition, loser)} on both mean score "
        f"({winner_score['mean']} vs {loser_score['mean']}) and win share "
        f"({winner_wins['mean']:.3f} vs {loser_wins['mean']:.3f})."
    )


def _aggregate_conclusions(aggregate_summary: dict[str, Any]) -> list[str]:
    lines = ["## Aggregate Conclusions"]
    conditions = aggregate_summary.get("conditions", [])
    if not conditions:
        lines.extend(
            [
                "- No condition summaries were available, so no aggregate conclusion can be drawn.",
                "",
            ]
        )
        return lines

    quality_counts = {"fully clean": 0, "near-clean": 0, "higher-noise": 0}
    for condition in conditions:
        quality_counts[_condition_quality_label(condition)] += 1
    lines.append(
        f"- Data quality summary: {quality_counts['fully clean']}/{len(conditions)} conditions were fully clean, "
        f"{quality_counts['near-clean']}/{len(conditions)} were near-clean, and "
        f"{quality_counts['higher-noise']}/{len(conditions)} remained higher-noise."
    )
    mixed_suite_families = len(aggregate_summary.get("suite_families", [])) > 1
    mixed_suite_types = len(aggregate_summary.get("suite_types", [])) > 1
    mixed_campaign = mixed_suite_families or mixed_suite_types
    if mixed_campaign:
        lines.append(
            "- This aggregate mixes multiple suite families or suite types, so treat it as a campaign-level inventory and sanity check rather than a causal comparison report."
        )
    if int(aggregate_summary.get("run_count", 0)) < 3:
        run_word = "run" if int(aggregate_summary.get("run_count", 0)) == 1 else "runs"
        lines.append(
            f"- The aggregate currently includes only {aggregate_summary.get('run_count', 0)} {run_word}, so all findings should be treated as preliminary until the full replicate target is met."
        )

    lines.append("")
    lines.append("### Best-Supported Findings")

    same_novelty = aggregate_summary["cross_run_summary"]["same_model_avg_novelty"]
    cross_novelty = aggregate_summary["cross_run_summary"]["cross_model_avg_novelty"]
    if mixed_campaign:
        lines.append(
            "- Family-level novelty comparisons are not the main interpretation target here because the aggregate mixes core, ablation, control, or opportunity suites."
        )
    elif _has_samples(same_novelty) and _has_samples(cross_novelty):
        if float(same_novelty["mean"]) > float(cross_novelty["mean"]):
            strong_novelty = int(aggregate_summary.get("run_count", 0)) >= 3 and not _ci_overlaps(same_novelty, cross_novelty)
            novelty_phrase = "consistently" if strong_novelty else "directionally"
            lines.append(
                f"- Same-model conditions showed {novelty_phrase} higher code novelty than cross-model conditions "
                f"({same_novelty['mean']} vs {cross_novelty['mean']})."
            )
        elif float(cross_novelty["mean"]) > float(same_novelty["mean"]):
            strong_novelty = int(aggregate_summary.get("run_count", 0)) >= 3 and not _ci_overlaps(same_novelty, cross_novelty)
            novelty_phrase = "consistently" if strong_novelty else "directionally"
            lines.append(
                f"- Cross-model conditions showed {novelty_phrase} higher code novelty than same-model conditions "
                f"({cross_novelty['mean']} vs {same_novelty['mean']})."
            )
        else:
            lines.append("- Same-model and cross-model novelty were effectively tied in the current aggregate.")
    elif _has_samples(same_novelty):
        lines.append(
            f"- This aggregate only supports same-model novelty summary ({same_novelty['mean']}); no cross-model comparison is available here."
        )
    elif _has_samples(cross_novelty):
        lines.append(
            f"- This aggregate only supports cross-model novelty summary ({cross_novelty['mean']}); no same-model comparison is available here."
        )
    else:
        lines.append("- No same-model versus cross-model novelty comparison is available in this aggregate.")

    same_markers = aggregate_summary["cross_run_summary"]["same_model_avg_policy_markers"]
    cross_markers = aggregate_summary["cross_run_summary"]["cross_model_avg_policy_markers"]
    if mixed_campaign:
        lines.append(
            "- Policy-marker totals should also be interpreted at the family level rather than as one combined same-model versus cross-model comparison."
        )
    elif _has_samples(same_markers) and _has_samples(cross_markers) and float(same_markers["mean"]) <= 0.5 and float(cross_markers["mean"]) <= 0.5:
        lines.append(
            f"- Policy-marker rates remained low across the aggregate "
            f"(same-model {same_markers['mean']}, cross-model {cross_markers['mean']}), "
            "so the current evidence does not show repeated or dominant rule-violation behavior."
        )
    elif _has_samples(same_markers) and _has_samples(cross_markers):
        lines.append(
            f"- Policy-marker rates were non-trivial in at least one comparison family "
            f"(same-model {same_markers['mean']}, cross-model {cross_markers['mean']}), "
            "so rule-boundary behavior should be inspected qualitatively before making strong claims."
        )
    elif _has_samples(same_markers):
        lines.append(
            f"- Policy-marker rates for the available same-model conditions were {same_markers['mean']}; no cross-model comparison is available here."
        )
    elif _has_samples(cross_markers):
        lines.append(
            f"- Policy-marker rates for the available cross-model conditions were {cross_markers['mean']}; no same-model comparison is available here."
        )

    limited = _condition_by_name(aggregate_summary, "same_model_limited_feedback")
    same_full = _condition_by_name(aggregate_summary, "same_model_full_feedback")
    if limited and same_full and not mixed_campaign:
        limited_exec = _min_rate(limited, "execution_rate")
        full_exec = _min_rate(same_full, "execution_rate")
        if limited_exec + 0.005 < full_exec:
            lines.append(
                f"- In the same-model comparison, limited feedback reduced execution reliability relative to full feedback "
                f"(minimum agent execution rate {limited_exec:.3f} vs {full_exec:.3f})."
            )

    cross_full = _condition_by_name(aggregate_summary, "cross_model_full_feedback")
    cross_winner_line = _cross_model_winner_line(cross_full) if cross_full else None
    if cross_winner_line and not mixed_campaign:
        lines.append(cross_winner_line)

    lines.append("")
    lines.append("### Directional Or Uncertain Findings")
    directional_lines: list[str] = []
    if same_full and limited:
        full_novelty = statistics.mean(
            float(same_full["novelty"][agent_name]["mean"]) for agent_name in same_full.get("agent_names", [])
        )
        limited_novelty = statistics.mean(
            float(limited["novelty"][agent_name]["mean"]) for agent_name in limited.get("agent_names", [])
        )
        directional_lines.append(
            f"- Full feedback and limited feedback differed on novelty ({full_novelty:.4f} vs {limited_novelty:.4f}), "
            "but this should be interpreted together with the reliability difference rather than treated as a standalone causal result."
        )
    if quality_counts["higher-noise"]:
        directional_lines.append(
            "- Conditions classified as higher-noise should be treated as exploratory unless the same direction reappears in cleaner replicate runs."
        )
    if not directional_lines:
        directional_lines.append(
            "- No major directional-only findings stood out beyond the supported points above."
        )
    lines.extend(directional_lines)

    lines.append("")
    lines.append("### Claims Not Supported Yet")
    lines.append(
        "- The aggregate does not by itself establish causality; the strongest causal interpretations should come from replicated ablation conditions rather than from mixed-condition summaries alone."
    )
    lines.append(
        "- Code novelty should not be treated as equivalent to strategic innovation without qualitative review of notable epochs and behavior traces."
    )
    if int(aggregate_summary.get("run_count", 0)) < 3:
        lines.append(
            "- Claims about stable long-run behavior are not yet well-supported because the current aggregate has fewer than three repeated runs."
        )
    lines.append("")
    return lines


def _build_aggregate_charts(output_dir: Path, aggregate_summary: dict[str, Any]) -> dict[str, str]:
    conditions = aggregate_summary.get("conditions", [])
    if not conditions:
        return {}

    categories = [_display_condition_name(condition["condition_name"]) for condition in conditions]
    agent_names = sorted({agent for condition in conditions for agent in condition.get("agent_names", [])})
    series_labels = {agent_name: agent_name.replace("_", " ").title() for agent_name in agent_names}

    def collect_stats(metric_name: str) -> tuple[dict[str, list[float]], dict[str, list[tuple[float, float]]]]:
        series: dict[str, list[float]] = {agent_name: [] for agent_name in agent_names}
        error_ranges: dict[str, list[tuple[float, float]]] = {agent_name: [] for agent_name in agent_names}
        for condition in conditions:
            metric = condition.get(metric_name, {})
            for agent_name in agent_names:
                stats = metric.get(agent_name)
                if not stats:
                    series[agent_name].append(0.0)
                    error_ranges[agent_name].append((0.0, 0.0))
                    continue
                series[agent_name].append(float(stats.get("mean", 0.0)))
                error_ranges[agent_name].append(
                    (
                        float(stats.get("ci95_low", stats.get("mean", 0.0))),
                        float(stats.get("ci95_high", stats.get("mean", 0.0))),
                    )
                )
        return series, error_ranges

    chart_specs = [
        {
            "name": "aggregate_average_scores.png",
            "title": "Aggregate Mean Score by Condition",
            "metric_name": "average_scores",
            "x_label": "Condition",
            "y_label": "Mean final score per epoch",
            "percent_scale": False,
        },
        {
            "name": "aggregate_execution_rates.png",
            "title": "Submitted-Code Execution Rate by Condition",
            "metric_name": "execution_rate",
            "x_label": "Condition",
            "y_label": "Execution rate",
            "percent_scale": True,
        },
        {
            "name": "aggregate_novelty.png",
            "title": "Aggregate Mean Code Novelty by Condition",
            "metric_name": "novelty",
            "x_label": "Condition",
            "y_label": "Average normalized novelty",
            "percent_scale": False,
        },
    ]

    chart_paths: dict[str, str] = {}
    for spec in chart_specs:
        series, error_ranges = collect_stats(spec["metric_name"])
        chart_path = output_dir / spec["name"]
        write_grouped_bar_chart_png(
            path=chart_path,
            title=spec["title"],
            categories=categories,
            series=series,
            x_label=spec["x_label"],
            y_label=spec["y_label"],
            series_labels=series_labels,
            error_ranges=error_ranges,
            percent_scale=bool(spec["percent_scale"]),
        )
        chart_paths[spec["metric_name"]] = chart_path.name
    return chart_paths


def render_aggregate_report(aggregate_summary: dict[str, Any], chart_paths: dict[str, str] | None = None) -> str:
    chart_paths = chart_paths or {}
    lines = [
        "# Aggregate Research Report",
        "",
        "## Included Runs",
        f"- Run count: {aggregate_summary.get('run_count', 0)}.",
        f"- Conditions aggregated: {aggregate_summary.get('condition_count', 0)}.",
    ]
    run_names = aggregate_summary.get("run_names", [])
    if run_names:
        lines.append(f"- Runs: {', '.join(f'`{item}`' for item in run_names)}.")
    lines.extend(
        [
            "",
            "## Cross-Run Summary",
        ]
    )
    same_novelty = aggregate_summary["cross_run_summary"]["same_model_avg_novelty"]
    cross_novelty = aggregate_summary["cross_run_summary"]["cross_model_avg_novelty"]
    same_markers = aggregate_summary["cross_run_summary"]["same_model_avg_policy_markers"]
    cross_markers = aggregate_summary["cross_run_summary"]["cross_model_avg_policy_markers"]
    if _has_samples(same_novelty):
        lines.append(f"- {_format_stat('Same-model novelty', same_novelty)}.")
    else:
        lines.append("- No same-model conditions were included in this aggregate.")
    if _has_samples(cross_novelty):
        lines.append(f"- {_format_stat('Cross-model novelty', cross_novelty)}.")
    else:
        lines.append("- No cross-model conditions were included in this aggregate.")
    if _has_samples(same_markers):
        lines.append(f"- {_format_stat('Same-model policy markers', same_markers)}.")
    else:
        lines.append("- No same-model policy-marker summary is available for this aggregate.")
    if _has_samples(cross_markers):
        lines.append(f"- {_format_stat('Cross-model policy markers', cross_markers)}.")
    else:
        lines.append("- No cross-model policy-marker summary is available for this aggregate.")
    if len(aggregate_summary.get("suite_families", [])) > 1 or len(aggregate_summary.get("suite_types", [])) > 1:
        lines.append(
            "- This aggregate mixes multiple suite families or suite types, so use the family-specific aggregates for interpretation and treat this summary as descriptive only."
        )
    lines.extend(
        [
            "",
            "## Aggregate Charts",
        ]
    )
    if chart_paths.get("average_scores"):
        lines.extend(
            [
                "### Mean Score by Condition",
                f"![Mean average score by condition and agent]({chart_paths['average_scores']})",
                "- Each bar shows the mean final score per epoch for one agent role in that condition.",
                "- Error bars show the 95% confidence interval across the included runs.",
                "",
            ]
        )
    if chart_paths.get("execution_rate"):
        lines.extend(
            [
                "### Submitted-Code Execution Rate by Condition",
                f"![Submitted-code execution rate by condition and agent]({chart_paths['execution_rate']})",
                "- The y-axis is the percentage of epochs where submitted code executed instead of a fallback policy.",
                "- Values near 100% indicate the infrastructure stayed reliable across the included runs.",
                "",
            ]
        )
    if chart_paths.get("novelty"):
        lines.extend(
            [
                "### Mean Code Novelty by Condition",
                f"![Mean code novelty by condition and agent]({chart_paths['novelty']})",
                "- Novelty is the average normalized code-change score across epochs for that agent role and condition.",
                "- Higher bars indicate more code variation across repeated runs, not necessarily better performance.",
                "",
            ]
        )
    lines.extend(
        [
            "## Per Condition",
        ]
    )

    for condition in aggregate_summary.get("conditions", []):
        lines.append(f"### {condition['condition_name']}")
        lines.append(
            f"- Matchup type: {'same-model' if condition.get('same_model_matchup') else 'cross-model'}."
        )
        lines.append(
            f"- Fully clean run count: {condition['clean_run_count']}/{condition['run_count']}."
        )
        if condition.get("metadata_examples"):
            metadata_rendered = "; ".join(
                ", ".join(f"{key}={value}" for key, value in sorted(item.items()))
                for item in condition["metadata_examples"]
            )
            lines.append(f"- Research tags: {metadata_rendered}.")
        for agent_name in condition.get("agent_names", []):
            lines.append(
                f"- {agent_name} average score: {_format_stat(agent_name, condition['average_scores'][agent_name])}."
            )
            lines.append(
                f"- {agent_name} generation success rate: {_format_stat(agent_name, condition['generation_success_rate'][agent_name])}."
            )
            lines.append(
                f"- {agent_name} submitted-code execution rate: {_format_stat(agent_name, condition['execution_rate'][agent_name])}."
            )
            lines.append(
                f"- {agent_name} novelty: {_format_stat(agent_name, condition['novelty'][agent_name])}."
            )
            lines.append(
                f"- {agent_name} policy-marker count: {_format_stat(agent_name, condition['policy_marker_count'][agent_name])}."
            )
        for outcome_name, stats in condition.get("win_shares", {}).items():
            lines.append(f"- {outcome_name} win share: {_format_stat(outcome_name, stats)}.")
        lines.append("")

    lines.extend(
        [
            "## Interpretation Caveats",
            "- Aggregate results are only as strong as the included run set. If the input runs mix different prompts, environments, or suite definitions, treat the summary as descriptive rather than causal.",
            "- Confidence intervals here summarize variation across run-level condition summaries; they are not substitutes for careful experimental design.",
            "- Use this aggregate report together with per-run reports and the research checklist before making strong claims.",
            "",
        ]
    )
    lines.extend(_aggregate_conclusions(aggregate_summary))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate multiple run directories into one research report.")
    parser.add_argument("--runs-root", default="runs", help="Root directory containing run_* folders.")
    parser.add_argument("--run-dir", action="append", default=None, help="Specific run directory to include. May be repeated.")
    parser.add_argument("--pattern", default="run_*", help="Glob used under --runs-root when --run-dir is omitted.")
    parser.add_argument("--output-dir", default=None, help="Directory to write aggregate artifacts into.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    runs_root = (project_root / args.runs_root).resolve()
    run_dirs = _discover_run_dirs(runs_root, args.run_dir, args.pattern)
    if not run_dirs:
        raise FileNotFoundError("No matching run directories were found.")

    aggregate_summary = aggregate_run_dirs(run_dirs)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output_dir).resolve() if args.output_dir else (runs_root / f"aggregate_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = output_dir / "aggregate_summary.json"
    summary_path.write_text(json.dumps(aggregate_summary, indent=2, sort_keys=True), encoding="utf-8")

    chart_paths = _build_aggregate_charts(output_dir, aggregate_summary)
    report = render_aggregate_report(aggregate_summary, chart_paths)
    report_path = output_dir / "aggregate_report.md"
    report_path.write_text(report, encoding="utf-8")

    write_pdf_report(
        path=output_dir / "aggregate_report.pdf",
        run_name=output_dir.name,
        markdown_report=report,
        suite_summary={},
        condition_payloads=[],
    )
    print(f"Wrote aggregate artifacts to: {output_dir}")


if __name__ == "__main__":
    main()
