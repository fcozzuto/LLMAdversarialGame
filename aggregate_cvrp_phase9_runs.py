from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any

from llm_grid_battle.pdf_report import write_pdf_report
from routing_aggregate_utils import bootstrap_mean_interval, find_condition_by_suffix, paired_bootstrap_delta


AGGREGATE_METRICS = [
    ("heldout_feasibility_rate", False, "heldout_feasibility_rate", 11),
    ("heldout_penalized_gap", True, "heldout_penalized_gap", 13),
    ("heldout_feasible_gap", True, "heldout_feasible_gap", 17),
    ("heldout_runtime_ms", True, "heldout_runtime_ms", 19),
    ("accepted_epoch_count", False, "accepted_epoch_count", 21),
    ("fallback_epoch_count", True, "fallback_epoch_count", 22),
    ("generation_error_epoch_count", True, "generation_error_epoch_count", 23),
    ("mean_code_novelty", False, "mean_code_novelty", 27),
    ("mean_complexity", True, "mean_complexity", 29),
    ("robustness_dispersion", True, "robustness_dispersion", 31),
]


def _json_dump(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def summarize_aggregate(run_dirs: list[Path]) -> dict[str, Any]:
    condition_metrics: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    run_condition_tables: list[dict[str, dict[str, Any]]] = []
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
            for metric_key, _lower, _label, _seed in AGGREGATE_METRICS:
                condition_metrics[name][metric_key].append(float(condition.get(metric_key, 0.0)))
        run_condition_tables.append(condition_table)

    conditions = []
    for name, metrics in sorted(condition_metrics.items()):
        payload = {"condition_name": name}
        for metric_key, _lower, _label, seed in AGGREGATE_METRICS:
            payload[metric_key] = bootstrap_mean_interval(metrics[metric_key], seed=seed)
        conditions.append(payload)

    condition_names = set(condition_metrics.keys())
    comparisons = summarize_paired_comparisons(run_condition_tables, condition_names)
    best = min(conditions, key=lambda item: float(item["heldout_penalized_gap"]["mean"]))["condition_name"] if conditions else None
    return {
        "run_count": used_run_count,
        "condition_count": len(conditions),
        "best_heldout_condition": best,
        "conditions": conditions,
        "paired_comparisons": comparisons,
    }


def summarize_paired_comparisons(run_condition_tables: list[dict[str, dict[str, Any]]], condition_names: set[str]) -> list[dict[str, Any]]:
    specs = []
    nn = find_condition_by_suffix(condition_names, "_baseline_nearest_neighbor_constructive")
    savings = find_condition_by_suffix(condition_names, "_baseline_clarke_wright_savings")
    insertion = find_condition_by_suffix(condition_names, "_baseline_regret_insertion_local_search")
    evolved = find_condition_by_suffix(condition_names, "phase9_solver_evolution")
    direct = find_condition_by_suffix(condition_names, "_direct_generate_plus_one_repair")
    budget = find_condition_by_suffix(condition_names, "_budget_matched_no_replay")
    replay = find_condition_by_suffix(condition_names, "_replay_solver_evolution")
    if savings and nn:
        specs.append({"name": "savings_vs_nearest_neighbor", "candidate": savings, "reference": nn})
    if insertion and savings:
        specs.append({"name": "insertion_vs_savings", "candidate": insertion, "reference": savings})
    if evolved and nn:
        specs.append({"name": "evolved_vs_nearest_neighbor", "candidate": evolved, "reference": nn})
    if evolved and savings:
        specs.append({"name": "evolved_vs_clarke_wright", "candidate": evolved, "reference": savings})
    if evolved and insertion:
        specs.append({"name": "evolved_vs_regret_insertion", "candidate": evolved, "reference": insertion})
    if direct and savings:
        specs.append({"name": "direct_vs_clarke_wright", "candidate": direct, "reference": savings})
    if budget and savings:
        specs.append({"name": "budget_matched_vs_clarke_wright", "candidate": budget, "reference": savings})
    if replay and savings:
        specs.append({"name": "replay_vs_clarke_wright", "candidate": replay, "reference": savings})
    if direct and budget:
        specs.append({"name": "direct_vs_budget_matched", "candidate": direct, "reference": budget})
    if replay and budget:
        specs.append({"name": "replay_vs_budget_matched", "candidate": replay, "reference": budget})
    if replay and direct:
        specs.append({"name": "replay_vs_direct", "candidate": replay, "reference": direct})
    comparisons = []
    for spec_index, spec in enumerate(specs):
        metric_payload = {}
        paired_count = 0
        for metric_index, (metric_key, lower_is_better, label, _seed) in enumerate(AGGREGATE_METRICS):
            candidate_values = []
            reference_values = []
            for table in run_condition_tables:
                candidate = table.get(spec["candidate"])
                reference = table.get(spec["reference"])
                if candidate is None or reference is None:
                    continue
                candidate_values.append(float(candidate.get(metric_key, 0.0)))
                reference_values.append(float(reference.get(metric_key, 0.0)))
            paired_count = max(paired_count, len(candidate_values))
            metric_payload[label] = paired_bootstrap_delta(
                candidate_values,
                reference_values,
                lower_is_better=lower_is_better,
                seed=(spec_index * 1000) + (metric_index * 53) + 7,
            )
        comparisons.append(
            {
                "comparison_name": spec["name"],
                "candidate_condition": spec["candidate"],
                "reference_condition": spec["reference"],
                "paired_run_count": paired_count,
                "metrics": metric_payload,
            }
        )
    return comparisons


def render_markdown_report(aggregate_summary: dict[str, Any]) -> str:
    condition_names = [str(item.get("condition_name", "")) for item in aggregate_summary.get("conditions", [])]
    if any(name.startswith("phase9_closeout_") for name in condition_names):
        title = "# Phase 9 Closeout Budget-Control CVRP Aggregate Report"
    else:
        title = "# Phase 9 CVRP Suite Aggregate Report"
    lines = [
        title,
        "",
        "## Overview",
        f"- Run count: {aggregate_summary.get('run_count', 0)}.",
        f"- Condition count: {aggregate_summary.get('condition_count', 0)}.",
        f"- Best held-out condition: `{aggregate_summary.get('best_heldout_condition')}`.",
        "",
        "## Condition Means",
        "| Condition | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity | Robustness Dispersion |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in aggregate_summary.get("conditions", []):
        lines.append(
            "| {condition_name} | {feasibility} | {penalized} | {feasible_gap} | {runtime_ms} | {accepted_epochs} | {fallback_epochs} | {generation_errors} | {novelty} | {complexity} | {robustness} |".format(
                condition_name=item["condition_name"],
                feasibility=item["heldout_feasibility_rate"]["mean"],
                penalized=item["heldout_penalized_gap"]["mean"],
                feasible_gap=item["heldout_feasible_gap"]["mean"],
                runtime_ms=item["heldout_runtime_ms"]["mean"],
                accepted_epochs=item["accepted_epoch_count"]["mean"],
                fallback_epochs=item["fallback_epoch_count"]["mean"],
                generation_errors=item["generation_error_epoch_count"]["mean"],
                novelty=item["mean_code_novelty"]["mean"],
                complexity=item["mean_complexity"]["mean"],
                robustness=item["robustness_dispersion"]["mean"],
            )
        )
    lines.extend(["", "## Paired Comparisons"])
    for item in aggregate_summary.get("paired_comparisons", []):
        penalized = item["metrics"]["heldout_penalized_gap"]
        feasibility = item["metrics"]["heldout_feasibility_rate"]
        lines.extend(
            [
                f"### {item['comparison_name']}",
                f"- Candidate: `{item['candidate_condition']}` versus reference `{item['reference_condition']}` across {item['paired_run_count']} paired runs.",
                f"- Held-out penalized-gap delta: {penalized['mean_delta']} (95% CI {penalized['ci95_low']} to {penalized['ci95_high']}).",
                f"- Held-out feasibility-rate delta: {feasibility['mean_delta']} (95% CI {feasibility['ci95_low']} to {feasibility['ci95_high']}).",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate repeated phase-9 CVRP suite runs, including closeout control studies.")
    parser.add_argument("--runs-root", required=True, help="Directory containing phase-9 run_* folders.")
    args = parser.parse_args()
    runs_root = Path(args.runs_root)
    run_dirs = [path for path in sorted(runs_root.iterdir()) if path.is_dir() and path.name.startswith("run_")]
    if not run_dirs:
        raise ValueError(f"No run_* directories found under {runs_root}")
    suffix = run_dirs[-1].name.removeprefix("run_")
    aggregate_dir = runs_root / f"aggregate_{suffix}"
    aggregate_dir.mkdir(parents=True, exist_ok=True)
    summary = summarize_aggregate(run_dirs)
    _json_dump(aggregate_dir / "aggregate_summary.json", summary)
    report = render_markdown_report(summary)
    (aggregate_dir / "aggregate_report.md").write_text(report, encoding="utf-8")
    write_pdf_report(
        path=aggregate_dir / "aggregate_report.pdf",
        run_name=aggregate_dir.name,
        markdown_report=report,
        suite_summary=summary,
        condition_payloads=[],
    )
    print(f"Completed phase-9 aggregate. Results written to: {aggregate_dir}")


if __name__ == "__main__":
    main()
