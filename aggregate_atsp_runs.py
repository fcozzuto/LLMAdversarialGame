from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any

from llm_grid_battle.pdf_report import write_pdf_report
from routing_aggregate_utils import bootstrap_mean_interval, build_default_paired_specs, summarize_paired_comparisons


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
            condition_metrics[name]["final_transfer_gap"].append(float(condition.get("final_transfer_gap", 0.0)))
            condition_metrics[name]["final_tsplib_gap"].append(float(condition.get("final_tsplib_gap", 0.0)))
            condition_metrics[name]["final_synthetic_gap"].append(float(condition.get("final_synthetic_gap", 0.0)))
            condition_metrics[name]["mean_code_novelty"].append(float(condition.get("mean_code_novelty", 0.0)))
            condition_metrics[name]["mean_complexity"].append(float(condition.get("mean_complexity", 0.0)))
            condition_metrics[name]["adaptation_efficiency"].append(float(condition.get("adaptation_efficiency", 0.0)))
        run_condition_tables.append(condition_table)

    conditions = []
    for name, metrics in sorted(condition_metrics.items()):
        conditions.append(
            {
                "condition_name": name,
                "final_transfer_gap": bootstrap_mean_interval(metrics["final_transfer_gap"], seed=11),
                "final_tsplib_gap": bootstrap_mean_interval(metrics["final_tsplib_gap"], seed=13),
                "final_synthetic_gap": bootstrap_mean_interval(metrics["final_synthetic_gap"], seed=17),
                "mean_code_novelty": bootstrap_mean_interval(metrics["mean_code_novelty"], seed=19),
                "mean_complexity": bootstrap_mean_interval(metrics["mean_complexity"], seed=23),
                "adaptation_efficiency": bootstrap_mean_interval(metrics["adaptation_efficiency"], seed=29),
            }
        )

    best_condition = min(
        conditions,
        key=lambda item: float(item["final_transfer_gap"]["mean"]),
    )["condition_name"] if conditions else None
    paired_comparisons = summarize_paired_comparisons(
        run_condition_tables=run_condition_tables,
        primary_metric_key="final_tsplib_gap",
        comparison_specs=build_default_paired_specs(set(condition_metrics.keys())),
        benchmark_label="tsplib_atsp_gap",
    )
    return {
        "run_count": used_run_count,
        "condition_count": len(conditions),
        "best_transfer_condition": best_condition,
        "conditions": conditions,
        "paired_comparisons": paired_comparisons,
    }


def render_markdown_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Replay-Aware ATSP Aggregate Report",
        "",
        "## Overview",
        f"- Run count: {summary.get('run_count', 0)}.",
        f"- Condition count: {summary.get('condition_count', 0)}.",
        f"- Best mean transfer gap: `{summary.get('best_transfer_condition')}`.",
        "",
        "## Condition Comparison",
        "| Condition | Mean Transfer Gap | Mean TSPLIB ATSP Gap | Mean Synthetic Gap | Mean Accepted Novelty | Mean Complexity | Mean Adaptation Efficiency |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in summary.get("conditions", []):
        lines.append(
            f"| {condition['condition_name']} | {condition['final_transfer_gap']['mean']} | {condition['final_tsplib_gap']['mean']} | "
            f"{condition['final_synthetic_gap']['mean']} | {condition['mean_code_novelty']['mean']} | "
            f"{condition['mean_complexity']['mean']} | {condition['adaptation_efficiency']['mean']} |"
        )
    lines.extend(
        [
            "",
            "## Bootstrap Confidence Intervals",
        ]
    )
    for condition in summary.get("conditions", []):
        lines.extend(
            [
                f"### {condition['condition_name']}",
                f"- Transfer gap 95% CI: `{condition['final_transfer_gap']['ci95_low']}` to `{condition['final_transfer_gap']['ci95_high']}`.",
                f"- TSPLIB ATSP gap 95% CI: `{condition['final_tsplib_gap']['ci95_low']}` to `{condition['final_tsplib_gap']['ci95_high']}`.",
                f"- Synthetic gap 95% CI: `{condition['final_synthetic_gap']['ci95_low']}` to `{condition['final_synthetic_gap']['ci95_high']}`.",
                f"- Mean accepted novelty 95% CI: `{condition['mean_code_novelty']['ci95_low']}` to `{condition['mean_code_novelty']['ci95_high']}`.",
            ]
        )
    paired = summary.get("paired_comparisons", [])
    if paired:
        lines.extend(
            [
                "",
                "## Paired Comparisons",
                "Negative delta favors the candidate for transfer gap, benchmark gap, synthetic gap, novelty, and complexity. Positive delta favors the candidate for adaptation efficiency.",
                "",
                "| Comparison | Paired Runs | Transfer Delta | Transfer 95% CI | ATSP Delta | ATSP 95% CI | Novelty Delta | Complexity Delta | Adaptation Delta |",
                "| --- | ---: | ---: | --- | ---: | --- | ---: | ---: | ---: |",
            ]
        )
        for item in paired:
            transfer = item["metrics"]["transfer_gap"]
            benchmark = item["metrics"]["tsplib_atsp_gap"]
            novelty = item["metrics"]["accepted_novelty"]
            complexity = item["metrics"]["complexity"]
            adaptation = item["metrics"]["adaptation_efficiency"]
            lines.append(
                f"| {item['candidate_condition']} vs {item['reference_condition']} | {item['paired_run_count']} | "
                f"{transfer['mean_delta']} | `{transfer['ci95_low']}` to `{transfer['ci95_high']}` | "
                f"{benchmark['mean_delta']} | `{benchmark['ci95_low']}` to `{benchmark['ci95_high']}` | "
                f"{novelty['mean_delta']} | {complexity['mean_delta']} | {adaptation['mean_delta']} |"
            )
        lines.extend(["", "### Paired Notes"])
        for item in paired:
            transfer = item["metrics"]["transfer_gap"]
            benchmark = item["metrics"]["tsplib_atsp_gap"]
            lines.extend(
                [
                    f"- `{item['candidate_condition']}` vs `{item['reference_condition']}` used {item['paired_run_count']} paired runs.",
                    f"- Mean transfer-gap delta: `{transfer['mean_delta']}` with 95% CI `{transfer['ci95_low']}` to `{transfer['ci95_high']}`; candidate better on {transfer['improved_run_fraction']:.1%} of paired runs.",
                    f"- Mean TSPLIB ATSP-gap delta: `{benchmark['mean_delta']}` with 95% CI `{benchmark['ci95_low']}` to `{benchmark['ci95_high']}`.",
                ]
            )
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate replay-aware ATSP suite runs.")
    parser.add_argument("--runs-root", default="runs/atsp_suite/replay_transfer", help="Root directory containing run_* folders.")
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
    print(f"Wrote aggregate report to {output_dir}")


if __name__ == "__main__":
    main()
