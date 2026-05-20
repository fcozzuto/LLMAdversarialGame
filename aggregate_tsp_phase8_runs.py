from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any

from llm_grid_battle.pdf_report import write_pdf_report
from routing_aggregate_utils import bootstrap_mean_interval, paired_bootstrap_delta


AGGREGATE_METRICS = [
    ("final_transfer_gap", 11),
    ("final_tsplib_gap", 13),
    ("final_family_gap", 17),
    ("final_selector_regret", 19),
    ("final_runtime_adjusted_gap", 23),
    ("final_runtime_inflation", 29),
    ("mean_code_novelty", 31),
    ("mean_complexity", 37),
    ("adaptation_efficiency", 41),
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
            for metric_key, _seed in AGGREGATE_METRICS:
                condition_metrics[name][metric_key].append(float(condition.get(metric_key, 0.0)))
        run_condition_tables.append(condition_table)

    conditions = []
    for name, metrics in sorted(condition_metrics.items()):
        payload = {"condition_name": name}
        for metric_key, seed in AGGREGATE_METRICS:
            payload[metric_key] = bootstrap_mean_interval(metrics[metric_key], seed=seed)
        conditions.append(payload)

    condition_names = set(condition_metrics.keys())
    paired_comparisons = summarize_phase8_paired_comparisons(run_condition_tables, condition_names)
    best_condition = min(
        conditions,
        key=lambda item: float(item["final_tsplib_gap"]["mean"]),
    )["condition_name"] if conditions else None
    return {
        "run_count": used_run_count,
        "condition_count": len(conditions),
        "best_tsplib_condition": best_condition,
        "conditions": conditions,
        "paired_comparisons": paired_comparisons,
        "portfolio_answers": build_portfolio_answers(paired_comparisons),
    }


def summarize_phase8_paired_comparisons(
    run_condition_tables: list[dict[str, dict[str, Any]]],
    condition_names: set[str],
) -> list[dict[str, Any]]:
    specs: list[dict[str, str]] = []
    best_fixed = _find_unique_condition(condition_names, "best_fixed")
    random_portfolio = _find_unique_condition(condition_names, "random_portfolio")
    oracle = _find_unique_condition(condition_names, "oracle_selector")
    supervised = _find_unique_condition(condition_names, "supervised_selector")
    static_selector = _find_unique_condition(condition_names, "static_selector")
    adaptive = _find_unique_condition(condition_names, "adaptive_controller")
    replay_adaptive = _find_unique_condition(condition_names, "adaptive_controller_replay")
    full_solver = _find_unique_condition(condition_names, "full_solver")
    if random_portfolio and best_fixed:
        specs.append({"name": "random_vs_best_fixed", "candidate": random_portfolio, "reference": best_fixed})
    if supervised and best_fixed:
        specs.append({"name": "supervised_vs_best_fixed", "candidate": supervised, "reference": best_fixed})
    if static_selector and supervised:
        specs.append({"name": "static_vs_supervised", "candidate": static_selector, "reference": supervised})
    if adaptive and static_selector:
        specs.append({"name": "adaptive_vs_static", "candidate": adaptive, "reference": static_selector})
    if replay_adaptive and adaptive:
        specs.append({"name": "replay_vs_adaptive", "candidate": replay_adaptive, "reference": adaptive})
    if full_solver and adaptive:
        specs.append({"name": "full_solver_vs_adaptive", "candidate": full_solver, "reference": adaptive})
    if oracle and best_fixed:
        specs.append({"name": "oracle_vs_best_fixed", "candidate": oracle, "reference": best_fixed})

    metrics = [
        ("final_tsplib_gap", True, "tsplib_gap"),
        ("final_transfer_gap", True, "transfer_gap"),
        ("final_selector_regret", True, "selector_regret"),
        ("final_runtime_adjusted_gap", True, "runtime_adjusted_gap"),
        ("final_runtime_inflation", True, "runtime_inflation"),
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
                seed=(spec_index * 1000) + (metric_index * 79) + 9,
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
    matches: list[str] = []
    for name in sorted(condition_names):
        if family == "best_fixed" and name.endswith("_best_single_fixed_heuristic"):
            matches.append(name)
        elif family == "random_portfolio" and name.endswith("_random_portfolio"):
            matches.append(name)
        elif family == "oracle_selector" and name.endswith("_oracle_selector"):
            matches.append(name)
        elif family == "supervised_selector" and name.endswith("_supervised_ml_selector"):
            matches.append(name)
        elif family == "static_selector" and name.endswith("_llm_static_selector"):
            matches.append(name)
        elif family == "adaptive_controller" and name.endswith("_llm_evolved_adaptive_controller"):
            matches.append(name)
        elif family == "adaptive_controller_replay" and name.endswith("_llm_evolved_controller_diversity_failure_replay"):
            matches.append(name)
        elif family == "full_solver" and name.endswith("_full_solver_evolution"):
            matches.append(name)
    return matches[0] if len(matches) == 1 else None


def build_portfolio_answers(paired_comparisons: list[dict[str, Any]]) -> dict[str, str]:
    lookup = {item["comparison_name"]: item for item in paired_comparisons}
    adaptive = lookup.get("adaptive_vs_static")
    replay = lookup.get("replay_vs_adaptive")
    full_solver = lookup.get("full_solver_vs_adaptive")
    supervised = lookup.get("supervised_vs_best_fixed")
    oracle = lookup.get("oracle_vs_best_fixed")
    answers = {
        "selector_progress": "Insufficient paired data.",
        "replay_effect": "Insufficient paired data.",
        "interpretability_tradeoff": "Insufficient paired data.",
    }
    if supervised and adaptive and oracle:
        answers["selector_progress"] = (
            f"Supervised selection changed held-out TSPLIB gap by {supervised['metrics']['tsplib_gap']['mean_delta']} versus the best fixed heuristic. "
            f"Adaptive LLM control changed held-out TSPLIB gap by {adaptive['metrics']['tsplib_gap']['mean_delta']} versus the static LLM selector, "
            f"while the oracle remained {oracle['metrics']['tsplib_gap']['mean_delta']} better than the best fixed heuristic."
        )
    if replay:
        answers["replay_effect"] = (
            f"Diversity-failure replay changed held-out TSPLIB gap by {replay['metrics']['tsplib_gap']['mean_delta']} "
            f"and selector regret by {replay['metrics']['selector_regret']['mean_delta']} relative to the no-replay adaptive controller."
        )
    if full_solver and adaptive:
        answers["interpretability_tradeoff"] = (
            f"Full-solver evolution changed held-out TSPLIB gap by {full_solver['metrics']['tsplib_gap']['mean_delta']} "
            f"and runtime-adjusted gap by {full_solver['metrics']['runtime_adjusted_gap']['mean_delta']} relative to the adaptive controller."
        )
    return answers


def render_markdown_report(aggregate_summary: dict[str, Any]) -> str:
    lines = [
        "# Phase 8 Aggregate Report",
        "",
        "## Overview",
        f"- Run count: {aggregate_summary.get('run_count', 0)}.",
        f"- Condition count: {aggregate_summary.get('condition_count', 0)}.",
        f"- Best held-out TSPLIB condition: `{aggregate_summary.get('best_tsplib_condition')}`.",
        "",
        "## Condition Means",
        "| Condition | Final TSPLIB Gap | Final Transfer Gap | Selector Regret | Runtime-Adjusted Gap | Runtime Inflation | Mean Novelty | Mean Complexity |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in aggregate_summary.get("conditions", []):
        lines.append(
            "| {condition_name} | {tsplib} | {transfer} | {regret} | {runtime_gap} | {runtime_inflation} | {novelty} | {complexity} |".format(
                condition_name=condition["condition_name"],
                tsplib=condition["final_tsplib_gap"]["mean"],
                transfer=condition["final_transfer_gap"]["mean"],
                regret=condition["final_selector_regret"]["mean"],
                runtime_gap=condition["final_runtime_adjusted_gap"]["mean"],
                runtime_inflation=condition["final_runtime_inflation"]["mean"],
                novelty=condition["mean_code_novelty"]["mean"],
                complexity=condition["mean_complexity"]["mean"],
            )
        )
    lines.extend(["", "## Paired Comparisons"])
    for comparison in aggregate_summary.get("paired_comparisons", []):
        transfer = comparison["metrics"]["transfer_gap"]
        regret = comparison["metrics"]["selector_regret"]
        lines.extend(
            [
                f"### {comparison['comparison_name']}",
                f"- Candidate: `{comparison['candidate_condition']}` versus reference `{comparison['reference_condition']}` across {comparison['paired_run_count']} paired runs.",
                f"- Held-out TSPLIB gap delta: {comparison['metrics']['tsplib_gap']['mean_delta']} (95% CI {comparison['metrics']['tsplib_gap']['ci95_low']} to {comparison['metrics']['tsplib_gap']['ci95_high']}).",
                f"- Transfer gap delta: {transfer['mean_delta']} (95% CI {transfer['ci95_low']} to {transfer['ci95_high']}).",
                f"- Selector regret delta: {regret['mean_delta']} (95% CI {regret['ci95_low']} to {regret['ci95_high']}).",
            ]
        )
    lines.extend(
        [
            "",
            "## Portfolio Answers",
            f"- Selector progress: {aggregate_summary.get('portfolio_answers', {}).get('selector_progress', 'n/a')}",
            f"- Replay effect: {aggregate_summary.get('portfolio_answers', {}).get('replay_effect', 'n/a')}",
            f"- Interpretability tradeoff: {aggregate_summary.get('portfolio_answers', {}).get('interpretability_tradeoff', 'n/a')}",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate repeated phase-8 adaptive heuristic portfolio runs.")
    parser.add_argument("--runs-root", required=True, help="Directory containing phase-8 run_* folders.")
    args = parser.parse_args()

    runs_root = Path(args.runs_root)
    run_dirs = [path for path in sorted(runs_root.iterdir()) if path.is_dir() and path.name.startswith("run_")]
    if not run_dirs:
        raise ValueError(f"No run_* directories found under {runs_root}")

    latest_run_name = run_dirs[-1].name
    suffix = latest_run_name.removeprefix("run_")
    aggregate_dir = runs_root / f"aggregate_{suffix}"
    aggregate_dir.mkdir(parents=True, exist_ok=True)

    aggregate_summary = summarize_aggregate(run_dirs)
    _json_dump(aggregate_dir / "aggregate_summary.json", aggregate_summary)
    report = render_markdown_report(aggregate_summary)
    (aggregate_dir / "aggregate_report.md").write_text(report, encoding="utf-8")
    write_pdf_report(
        path=aggregate_dir / "aggregate_report.pdf",
        run_name=aggregate_dir.name,
        markdown_report=report,
        suite_summary=aggregate_summary,
        condition_payloads=[],
    )
    print(f"Completed phase-8 aggregate. Results written to: {aggregate_dir}")


if __name__ == "__main__":
    main()
