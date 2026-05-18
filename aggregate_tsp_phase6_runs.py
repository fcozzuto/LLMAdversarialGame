from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
from typing import Any

from llm_grid_battle.pdf_report import write_pdf_report
from llm_tsp.visualization import write_scatter_plot_png, write_scatter_plot_svg
from routing_aggregate_utils import bootstrap_mean_interval, paired_bootstrap_delta


AGGREGATE_METRICS = [
    ("final_transfer_gap", 11),
    ("final_tsplib_gap", 13),
    ("final_synthetic_gap", 17),
    ("mean_code_novelty", 19),
    ("mean_complexity", 23),
    ("adaptation_efficiency", 29),
    ("mean_archive_descriptor_diversity", 31),
    ("mean_archive_hardness", 37),
    ("mean_archive_size_bias", 41),
    ("mean_replay_failure_concentration", 43),
    ("mean_replay_selection_diversity", 47),
    ("mean_selected_expected_gap", 53),
    ("mean_selected_residual_gap", 59),
]


def _json_dump(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def summarize_aggregate(run_dirs: list[Path]) -> dict[str, Any]:
    condition_metrics: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    run_condition_tables: list[dict[str, dict[str, Any]]] = []
    scatter_points: list[dict[str, Any]] = []
    used_run_count = 0
    for run_dir in run_dirs:
        summary_path = run_dir / "suite_summary.json"
        if not summary_path.exists():
            continue
        used_run_count += 1
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        condition_table: dict[str, dict[str, Any]] = {}
        for condition in summary.get("conditions", []):
            name = str(condition["condition_name"])
            condition_table[name] = condition
            for metric_key, _seed in AGGREGATE_METRICS:
                condition_metrics[name][metric_key].append(float(condition.get(metric_key, 0.0)))
            scatter_points.append(
                {
                    "condition_name": name,
                    "run_name": run_dir.name,
                    "archive_diversity": float(condition.get("mean_archive_descriptor_diversity", 0.0)),
                    "archive_hardness": float(condition.get("mean_archive_hardness", 0.0)),
                    "tsplib_gap": float(condition.get("final_tsplib_gap", 0.0)),
                    "transfer_gap": float(condition.get("final_transfer_gap", 0.0)),
                }
            )
        run_condition_tables.append(condition_table)

    conditions = []
    for name, metrics in sorted(condition_metrics.items()):
        payload = {"condition_name": name}
        for metric_key, seed in AGGREGATE_METRICS:
            payload[metric_key] = bootstrap_mean_interval(metrics[metric_key], seed=seed)
        conditions.append(payload)

    condition_names = set(condition_metrics.keys())
    paired_comparisons = summarize_phase6_paired_comparisons(run_condition_tables, condition_names)
    diversity_vs_gap = summarize_scatter_relation(scatter_points, x_key="archive_diversity", y_key="tsplib_gap")
    hardness_vs_gap = summarize_scatter_relation(scatter_points, x_key="archive_hardness", y_key="tsplib_gap")
    best_condition = min(
        conditions,
        key=lambda item: float(item["final_transfer_gap"]["mean"]),
    )["condition_name"] if conditions else None

    return {
        "run_count": used_run_count,
        "condition_count": len(conditions),
        "best_transfer_condition": best_condition,
        "conditions": conditions,
        "paired_comparisons": paired_comparisons,
        "scatter_points": scatter_points,
        "diversity_vs_gap": diversity_vs_gap,
        "hardness_vs_gap": hardness_vs_gap,
        "mechanism_answers": build_mechanism_answers(paired_comparisons, diversity_vs_gap, hardness_vs_gap),
    }


def summarize_phase6_paired_comparisons(
    run_condition_tables: list[dict[str, dict[str, Any]]],
    condition_names: set[str],
) -> list[dict[str, Any]]:
    specs: list[dict[str, str]] = []
    no_replay = _find_unique_condition(condition_names, "no_replay")
    random_replay = _find_unique_condition(condition_names, "random_replay")
    failure_replay = _find_unique_condition(condition_names, "failure_replay")
    random_replay_compression = _find_unique_condition(condition_names, "random_replay_compression")
    stratified_random = _find_unique_condition(condition_names, "stratified_random_replay")
    diversity_weighted = _find_unique_condition(condition_names, "diversity_weighted_replay")
    residual_failure = _find_unique_condition(condition_names, "residual_failure_replay")
    diversity_failure = _find_unique_condition(condition_names, "diversity_failure_replay")
    diversity_failure_compression = _find_unique_condition(condition_names, "diversity_failure_replay_compression")

    if random_replay and no_replay:
        specs.append({"name": "random_vs_no_replay", "candidate": random_replay, "reference": no_replay})
    if failure_replay and random_replay:
        specs.append({"name": "failure_vs_random", "candidate": failure_replay, "reference": random_replay})
    if random_replay_compression and random_replay:
        specs.append({"name": "random_compression_vs_random", "candidate": random_replay_compression, "reference": random_replay})
    if stratified_random and random_replay:
        specs.append({"name": "stratified_vs_random", "candidate": stratified_random, "reference": random_replay})
    if diversity_weighted and random_replay:
        specs.append({"name": "diversity_weighted_vs_random", "candidate": diversity_weighted, "reference": random_replay})
    if residual_failure and failure_replay:
        specs.append({"name": "residual_vs_failure", "candidate": residual_failure, "reference": failure_replay})
    if diversity_failure and failure_replay:
        specs.append({"name": "diversity_failure_vs_failure", "candidate": diversity_failure, "reference": failure_replay})
    if diversity_failure_compression and diversity_failure:
        specs.append({"name": "diversity_failure_compression_vs_diversity_failure", "candidate": diversity_failure_compression, "reference": diversity_failure})

    metrics = [
        ("final_transfer_gap", True, "transfer_gap"),
        ("final_tsplib_gap", True, "tsplib_gap"),
        ("final_synthetic_gap", True, "synthetic_gap"),
        ("mean_archive_descriptor_diversity", False, "archive_diversity"),
        ("mean_archive_hardness", True, "archive_hardness"),
        ("mean_replay_failure_concentration", True, "failure_concentration"),
        ("mean_code_novelty", True, "accepted_novelty"),
        ("mean_complexity", True, "complexity"),
        ("adaptation_efficiency", False, "adaptation_efficiency"),
    ]

    comparisons: list[dict[str, Any]] = []
    for spec_index, spec in enumerate(specs):
        metric_payload: dict[str, Any] = {}
        paired_run_count = 0
        for metric_index, (metric_key, lower_is_better, label) in enumerate(metrics):
            candidate_values: list[float] = []
            reference_values: list[float] = []
            for table in run_condition_tables:
                candidate = table.get(spec["candidate"])
                reference = table.get(spec["reference"])
                if candidate is None or reference is None:
                    continue
                candidate_values.append(float(candidate.get(metric_key, 0.0)))
                reference_values.append(float(reference.get(metric_key, 0.0)))
            paired_run_count = max(paired_run_count, len(candidate_values))
            metric_payload[label] = paired_bootstrap_delta(
                candidate_values,
                reference_values,
                lower_is_better=lower_is_better,
                seed=(spec_index * 1_000) + (metric_index * 71) + 7,
            )
        comparisons.append(
            {
                "comparison_name": spec["name"],
                "candidate_condition": spec["candidate"],
                "reference_condition": spec["reference"],
                "paired_run_count": paired_run_count,
                "metrics": metric_payload,
            }
        )
    return comparisons


def _find_unique_condition(condition_names: set[str], family: str) -> str | None:
    exact_matches: list[str] = []
    for name in sorted(condition_names):
        if family == "no_replay" and name.endswith("_no_replay"):
            exact_matches.append(name)
        elif family == "random_replay" and name.endswith("_random_replay"):
            exact_matches.append(name)
        elif family == "failure_replay" and name.endswith("_failure_replay"):
            if name.endswith("_residual_failure_replay") or name.endswith("_diversity_failure_replay"):
                continue
            exact_matches.append(name)
        elif family == "random_replay_compression" and name.endswith("_random_replay_compression"):
            exact_matches.append(name)
        elif family == "stratified_random_replay" and name.endswith("_stratified_random_replay"):
            exact_matches.append(name)
        elif family == "diversity_weighted_replay" and name.endswith("_diversity_weighted_replay"):
            exact_matches.append(name)
        elif family == "residual_failure_replay" and name.endswith("_residual_failure_replay"):
            exact_matches.append(name)
        elif family == "diversity_failure_replay" and name.endswith("_diversity_failure_replay"):
            if name.endswith("_diversity_failure_replay_compression"):
                continue
            exact_matches.append(name)
        elif family == "diversity_failure_replay_compression" and name.endswith("_diversity_failure_replay_compression"):
            exact_matches.append(name)
    return exact_matches[0] if len(exact_matches) == 1 else None


def summarize_scatter_relation(points: list[dict[str, Any]], *, x_key: str, y_key: str) -> dict[str, Any]:
    x_values = [float(point.get(x_key, 0.0)) for point in points]
    y_values = [float(point.get(y_key, 0.0)) for point in points]
    return {
        "point_count": len(points),
        "pearson_r": round(pearson_r(x_values, y_values), 6),
        "spearman_rho": round(spearman_rho(x_values, y_values), 6),
    }


def pearson_r(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        return 0.0
    mean_left = sum(left) / len(left)
    mean_right = sum(right) / len(right)
    numerator = sum((lval - mean_left) * (rval - mean_right) for lval, rval in zip(left, right))
    left_sd = math.sqrt(sum((value - mean_left) ** 2 for value in left))
    right_sd = math.sqrt(sum((value - mean_right) ** 2 for value in right))
    if left_sd <= 1e-12 or right_sd <= 1e-12:
        return 0.0
    return numerator / (left_sd * right_sd)


def spearman_rho(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        return 0.0
    return pearson_r(_rank(left), _rank(right))


def _rank(values: list[float]) -> list[float]:
    indexed = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0 for _ in values]
    cursor = 0
    while cursor < len(indexed):
        end = cursor
        while end + 1 < len(indexed) and indexed[end + 1][0] == indexed[cursor][0]:
            end += 1
        average_rank = (cursor + end) / 2.0
        for position in range(cursor, end + 1):
            ranks[indexed[position][1]] = average_rank
        cursor = end + 1
    return ranks


def build_mechanism_answers(
    paired_comparisons: list[dict[str, Any]],
    diversity_vs_gap: dict[str, Any],
    hardness_vs_gap: dict[str, Any],
) -> dict[str, str]:
    comparison_lookup = {item["comparison_name"]: item for item in paired_comparisons}
    random_vs_no = comparison_lookup.get("random_vs_no_replay")
    failure_vs_random = comparison_lookup.get("failure_vs_random")
    random_compression = comparison_lookup.get("random_compression_vs_random")

    why_random = "Insufficient paired data."
    if random_vs_no and failure_vs_random:
        random_transfer = random_vs_no["metrics"]["transfer_gap"]["mean_delta"]
        failure_transfer = failure_vs_random["metrics"]["transfer_gap"]["mean_delta"]
        random_diversity = random_vs_no["metrics"]["archive_diversity"]["mean_delta"]
        failure_hardness = failure_vs_random["metrics"]["archive_hardness"]["mean_delta"]
        why_random = (
            "Random replay outperformed raw failure replay when it kept broader archive coverage. "
            f"Its transfer delta vs no replay was {random_transfer}, while failure replay vs random was {failure_transfer}; "
            f"the diversity shift was {random_diversity} and the hardness shift was {failure_hardness}."
        )

    diversity_explanation = (
        "Archive diversity explains transfer better than hardness."
        if abs(float(diversity_vs_gap.get("spearman_rho", 0.0))) >= abs(float(hardness_vs_gap.get("spearman_rho", 0.0)))
        else "Archive hardness explains transfer at least as strongly as diversity."
    )

    compression_answer = "Insufficient paired data."
    if random_compression:
        compression_answer = (
            f"Random-replay compression changed transfer by {random_compression['metrics']['transfer_gap']['mean_delta']} "
            f"and complexity by {random_compression['metrics']['complexity']['mean_delta']} relative to plain random replay."
        )

    operator_difference = (
        "Final heuristics should be treated as genuinely different only when transfer, novelty, and complexity move together; "
        "the paired novelty and complexity deltas in this aggregate are the main evidence for that distinction."
    )
    return {
        "why_random_replay_beat_failure_replay": why_random,
        "diversity_vs_hardness": diversity_explanation,
        "compression_on_best_replay": compression_answer,
        "final_heuristic_difference": operator_difference,
    }


def render_markdown_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Phase 6 TSP Replay Mechanism Report",
        "",
        "## Overview",
        f"- Run count: {summary.get('run_count', 0)}.",
        f"- Condition count: {summary.get('condition_count', 0)}.",
        f"- Best mean transfer gap: `{summary.get('best_transfer_condition')}`.",
        "",
        "## Mechanism Answers",
        f"1. Why did random replay beat failure replay? {summary.get('mechanism_answers', {}).get('why_random_replay_beat_failure_replay', 'n/a')}",
        f"2. Does replay archive diversity explain transfer better than replay hardness? {summary.get('mechanism_answers', {}).get('diversity_vs_hardness', 'n/a')}",
        f"3. Does compression help once applied to the best replay mechanism? {summary.get('mechanism_answers', {}).get('compression_on_best_replay', 'n/a')}",
        f"4. Are the final heuristics genuinely different, or just differently tuned? {summary.get('mechanism_answers', {}).get('final_heuristic_difference', 'n/a')}",
        "",
        "## Condition Comparison",
        "| Condition | Mean Transfer Gap | Mean TSPLIB Gap | Mean Synthetic Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in summary.get("conditions", []):
        lines.append(
            f"| {condition['condition_name']} | {condition['final_transfer_gap']['mean']} | {condition['final_tsplib_gap']['mean']} | "
            f"{condition['final_synthetic_gap']['mean']} | {condition['mean_archive_descriptor_diversity']['mean']} | "
            f"{condition['mean_archive_hardness']['mean']} | {condition['mean_replay_failure_concentration']['mean']} | "
            f"{condition['mean_code_novelty']['mean']} | {condition['mean_complexity']['mean']} | {condition['adaptation_efficiency']['mean']} |"
        )

    lines.extend(
        [
            "",
            "## Archive-Diversity Diagnostics",
            f"- Diversity vs TSPLIB gap Pearson r: `{summary.get('diversity_vs_gap', {}).get('pearson_r', 0.0)}`.",
            f"- Diversity vs TSPLIB gap Spearman rho: `{summary.get('diversity_vs_gap', {}).get('spearman_rho', 0.0)}`.",
            f"- Hardness vs TSPLIB gap Pearson r: `{summary.get('hardness_vs_gap', {}).get('pearson_r', 0.0)}`.",
            f"- Hardness vs TSPLIB gap Spearman rho: `{summary.get('hardness_vs_gap', {}).get('spearman_rho', 0.0)}`.",
        ]
    )

    paired = summary.get("paired_comparisons", [])
    if paired:
        lines.extend(
            [
                "",
                "## Paired Comparisons",
                "Negative deltas favor the candidate for transfer gap, benchmark gap, synthetic gap, hardness, concentration, novelty, and complexity. Positive deltas favor the candidate for archive diversity and adaptation efficiency.",
                "",
                "| Comparison | Paired Runs | Transfer Delta | TSPLIB Delta | Archive Diversity Delta | Archive Hardness Delta | Novelty Delta | Complexity Delta | Adaptation Delta |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for item in paired:
            lines.append(
                f"| {item['candidate_condition']} vs {item['reference_condition']} | {item['paired_run_count']} | "
                f"{item['metrics']['transfer_gap']['mean_delta']} | {item['metrics']['tsplib_gap']['mean_delta']} | "
                f"{item['metrics']['archive_diversity']['mean_delta']} | {item['metrics']['archive_hardness']['mean_delta']} | "
                f"{item['metrics']['accepted_novelty']['mean_delta']} | {item['metrics']['complexity']['mean_delta']} | "
                f"{item['metrics']['adaptation_efficiency']['mean_delta']} |"
            )
        lines.extend(["", "### Paired Notes"])
        for item in paired:
            transfer = item["metrics"]["transfer_gap"]
            benchmark = item["metrics"]["tsplib_gap"]
            diversity = item["metrics"]["archive_diversity"]
            lines.extend(
                [
                    f"- `{item['candidate_condition']}` vs `{item['reference_condition']}` used {item['paired_run_count']} paired runs.",
                    f"- Transfer delta `{transfer['mean_delta']}` with 95% CI `{transfer['ci95_low']}` to `{transfer['ci95_high']}`.",
                    f"- TSPLIB delta `{benchmark['mean_delta']}` with 95% CI `{benchmark['ci95_low']}` to `{benchmark['ci95_high']}`.",
                    f"- Archive-diversity delta `{diversity['mean_delta']}` with 95% CI `{diversity['ci95_low']}` to `{diversity['ci95_high']}`.",
                ]
            )
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate phase-6 TSP replay mechanism runs.")
    parser.add_argument("--runs-root", default="runs/tsp_phase6_suite/replay_mechanism", help="Root directory containing run_* folders.")
    args = parser.parse_args()

    runs_root = Path(args.runs_root)
    run_dirs = sorted(path for path in runs_root.iterdir() if path.is_dir() and path.name.startswith("run_"))
    if not run_dirs:
        raise SystemExit(f"No run directories found under {runs_root}")
    valid_run_dirs = [path for path in run_dirs if (path / "suite_summary.json").exists()]
    if not valid_run_dirs:
        raise SystemExit(f"No completed run directories with suite_summary.json were found under {runs_root}")

    summary = summarize_aggregate(valid_run_dirs)
    timestamp = valid_run_dirs[-1].name.replace("run_", "aggregate_")
    output_dir = runs_root / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    scatter_points = summary.get("scatter_points", [])
    diversity_plot_points = [
        {
            "x": float(point["archive_diversity"]),
            "y": float(point["tsplib_gap"]),
            "series": str(point["condition_name"]),
        }
        for point in scatter_points
    ]
    hardness_plot_points = [
        {
            "x": float(point["archive_hardness"]),
            "y": float(point["tsplib_gap"]),
            "series": str(point["condition_name"]),
        }
        for point in scatter_points
    ]
    write_scatter_plot_svg(
        path=output_dir / "archive_diversity_vs_tsplib_gap.svg",
        title="TSPLIB Gap vs Replay Archive Descriptor Diversity",
        x_label="Mean replay archive descriptor diversity",
        y_label="Final held-out TSPLIB gap",
        points=diversity_plot_points,
    )
    write_scatter_plot_png(
        path=output_dir / "archive_diversity_vs_tsplib_gap.png",
        title="TSPLIB Gap vs Replay Archive Descriptor Diversity",
        x_label="Mean replay archive descriptor diversity",
        y_label="Final held-out TSPLIB gap",
        points=diversity_plot_points,
    )
    write_scatter_plot_svg(
        path=output_dir / "archive_hardness_vs_tsplib_gap.svg",
        title="TSPLIB Gap vs Replay Archive Hardness",
        x_label="Mean replay archive hardness",
        y_label="Final held-out TSPLIB gap",
        points=hardness_plot_points,
    )
    write_scatter_plot_png(
        path=output_dir / "archive_hardness_vs_tsplib_gap.png",
        title="TSPLIB Gap vs Replay Archive Hardness",
        x_label="Mean replay archive hardness",
        y_label="Final held-out TSPLIB gap",
        points=hardness_plot_points,
    )

    _json_dump(output_dir / "aggregate_summary.json", summary)
    report = render_markdown_report(summary)
    (output_dir / "aggregate_report.md").write_text(report, encoding="utf-8")
    write_pdf_report(
        path=output_dir / "aggregate_report.pdf",
        run_name=output_dir.name,
        markdown_report=report,
        suite_summary=summary,
        condition_payloads=[],
    )
    print(f"Wrote phase-6 aggregate report to {output_dir}")


if __name__ == "__main__":
    main()
