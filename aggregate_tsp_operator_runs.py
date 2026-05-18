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
    ("mean_code_novelty", 19),
    ("mean_complexity", 23),
    ("adaptation_efficiency", 29),
    ("transplant_mean_gap_delta", 31),
    ("positive_scaffold_count", 37),
    ("pareto_runtime_inflation", 41),
]


def _json_dump(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def summarize_aggregate(run_dirs: list[Path]) -> dict[str, Any]:
    condition_metrics: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    run_condition_tables: list[dict[str, dict[str, Any]]] = []
    rediscovery: dict[str, list[dict[str, Any]]] = defaultdict(list)
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
            validation = condition.get("operator_validation", {})
            signature = str(validation.get("rediscovery_signature", "")).strip()
            if signature:
                rediscovery[signature].append(
                    {
                        "run_name": run_dir.name,
                        "condition_name": name,
                        "operator_name": validation.get("operator_name"),
                        "novelty_classification": validation.get("novelty_classification"),
                        "surviving_candidate": bool(validation.get("surviving_candidate", False)),
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
    paired_comparisons = summarize_phase7_paired_comparisons(run_condition_tables, condition_names)
    rediscovery_summary = summarize_rediscovery(rediscovery)
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
        "rediscovery_summary": rediscovery_summary,
        "discovery_answers": build_discovery_answers(paired_comparisons, rediscovery_summary),
    }


def summarize_phase7_paired_comparisons(
    run_condition_tables: list[dict[str, dict[str, Any]]],
    condition_names: set[str],
) -> list[dict[str, Any]]:
    specs: list[dict[str, str]] = []
    baseline_only = _find_unique_condition(condition_names, "baseline_heuristic_only")
    full_solver = _find_unique_condition(condition_names, "full_solver_evolution")
    modular_base = _find_unique_condition(condition_names, "modular_operator_evolution")
    modular_random = _find_unique_condition(condition_names, "modular_operator_random_replay")
    modular_residual = _find_unique_condition(condition_names, "modular_operator_diversity_residual_replay")
    modular_compression = _find_unique_condition(condition_names, "modular_operator_compression_pressure")
    modular_pareto = _find_unique_condition(condition_names, "modular_operator_pareto_selection")
    if modular_base and baseline_only:
        specs.append({"name": "modular_vs_baseline_only", "candidate": modular_base, "reference": baseline_only})
    if modular_base and full_solver:
        specs.append({"name": "modular_vs_full_solver", "candidate": modular_base, "reference": full_solver})
    if modular_random and modular_base:
        specs.append({"name": "random_vs_modular_base", "candidate": modular_random, "reference": modular_base})
    if modular_residual and modular_random:
        specs.append({"name": "diversity_residual_vs_random", "candidate": modular_residual, "reference": modular_random})
    if modular_compression and modular_base:
        specs.append({"name": "compression_vs_modular_base", "candidate": modular_compression, "reference": modular_base})
    if modular_pareto and modular_base:
        specs.append({"name": "pareto_vs_modular_base", "candidate": modular_pareto, "reference": modular_base})

    metrics = [
        ("final_transfer_gap", True, "transfer_gap"),
        ("final_tsplib_gap", True, "tsplib_gap"),
        ("final_family_gap", True, "family_gap"),
        ("mean_code_novelty", True, "accepted_novelty"),
        ("mean_complexity", True, "complexity"),
        ("transplant_mean_gap_delta", True, "transplant_gap_delta"),
        ("pareto_runtime_inflation", True, "runtime_inflation"),
        ("positive_scaffold_count", False, "positive_scaffold_count"),
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
                seed=(spec_index * 1_000) + (metric_index * 73) + 5,
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


def summarize_rediscovery(rediscovery: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    signatures = []
    surviving_signatures = []
    for signature, entries in sorted(rediscovery.items(), key=lambda item: (-len(item[1]), item[0])):
        survivors = [entry for entry in entries if entry["surviving_candidate"]]
        payload = {
            "signature": signature,
            "count": len(entries),
            "surviving_count": len(survivors),
            "conditions": sorted({entry["condition_name"] for entry in entries}),
            "novelty_classifications": sorted({str(entry["novelty_classification"]) for entry in entries if entry["novelty_classification"]}),
        }
        signatures.append(payload)
        if survivors:
            surviving_signatures.append(payload)
    return {
        "signature_count": len(signatures),
        "signatures": signatures,
        "surviving_signatures": surviving_signatures,
        "most_common_signature": signatures[0]["signature"] if signatures else None,
        "most_common_surviving_signature": surviving_signatures[0]["signature"] if surviving_signatures else None,
    }


def build_discovery_answers(
    paired_comparisons: list[dict[str, Any]],
    rediscovery_summary: dict[str, Any],
) -> dict[str, str]:
    lookup = {item["comparison_name"]: item for item in paired_comparisons}
    modular_vs_full = lookup.get("modular_vs_full_solver")
    random_vs_base = lookup.get("random_vs_modular_base")
    residual_vs_random = lookup.get("diversity_residual_vs_random")
    pareto_vs_base = lookup.get("pareto_vs_modular_base")

    modular_answer = "Insufficient paired data."
    if modular_vs_full:
        transfer = modular_vs_full["metrics"]["transfer_gap"]
        transplant = modular_vs_full["metrics"]["transplant_gap_delta"]
        modular_answer = (
            f"Relative to full-solver evolution, the base modular operator condition changed transfer by {transfer['mean_delta']} "
            f"and transplant quality by {transplant['mean_delta']}."
        )

    replay_answer = "Insufficient paired data."
    if random_vs_base and residual_vs_random:
        replay_transfer = random_vs_base["metrics"]["transfer_gap"]["mean_delta"]
        residual_transfer = residual_vs_random["metrics"]["transfer_gap"]["mean_delta"]
        replay_answer = (
            f"Random replay changed modular transfer by {replay_transfer} versus the no-replay modular baseline, "
            f"while diversity-residual replay changed transfer by {residual_transfer} versus random replay."
        )

    survivor_answer = (
        f"Rediscovery produced {rediscovery_summary.get('signature_count', 0)} distinct signatures; "
        f"the most common surviving signature is `{rediscovery_summary.get('most_common_surviving_signature')}`."
        if rediscovery_summary.get("signature_count", 0)
        else "No rediscovery signatures were observed."
    )
    pareto_answer = "Insufficient paired data."
    if pareto_vs_base:
        pareto_answer = (
            f"Pareto selection changed transfer by {pareto_vs_base['metrics']['transfer_gap']['mean_delta']} "
            f"and runtime inflation by {pareto_vs_base['metrics']['runtime_inflation']['mean_delta']} relative to the base modular condition."
        )
    return {
        "modular_vs_full_solver": modular_answer,
        "replay_mechanism": replay_answer,
        "rediscovery": survivor_answer,
        "pareto_tradeoff": pareto_answer,
    }


def render_markdown_report(aggregate_summary: dict[str, Any]) -> str:
    lines = [
        "# Phase 7 Aggregate Report",
        "",
        "## Overview",
        f"- Run count: {aggregate_summary.get('run_count', 0)}.",
        f"- Condition count: {aggregate_summary.get('condition_count', 0)}.",
        f"- Best transfer condition: `{aggregate_summary.get('best_transfer_condition')}`.",
        "",
        "## Condition Means",
        "| Condition | Final Transfer Gap | Final TSPLIB Gap | Final Family Gap | Mean Novelty | Mean Complexity | Transplant Delta | Pareto Runtime Inflation |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in aggregate_summary.get("conditions", []):
        lines.append(
            "| {condition_name} | {transfer} | {tsplib} | {family} | {novelty} | {complexity} | {transplant} | {runtime} |".format(
                condition_name=condition["condition_name"],
                transfer=condition["final_transfer_gap"]["mean"],
                tsplib=condition["final_tsplib_gap"]["mean"],
                family=condition["final_family_gap"]["mean"],
                novelty=condition["mean_code_novelty"]["mean"],
                complexity=condition["mean_complexity"]["mean"],
                transplant=condition["transplant_mean_gap_delta"]["mean"],
                runtime=condition["pareto_runtime_inflation"]["mean"],
            )
        )
    lines.extend(
        [
            "",
            "## Paired Comparisons",
        ]
    )
    for comparison in aggregate_summary.get("paired_comparisons", []):
        transfer = comparison["metrics"]["transfer_gap"]
        tsplib = comparison["metrics"]["tsplib_gap"]
        lines.append(
            f"- `{comparison['comparison_name']}`: transfer delta `{transfer['mean_delta']}` (95% CI `{transfer['ci95_low']}` to `{transfer['ci95_high']}`), "
            f"TSPLIB delta `{tsplib['mean_delta']}`."
        )
    lines.extend(
        [
            "",
            "## Rediscovery",
            f"- Signature count: {aggregate_summary.get('rediscovery_summary', {}).get('signature_count', 0)}.",
            f"- Most common surviving signature: `{aggregate_summary.get('rediscovery_summary', {}).get('most_common_surviving_signature')}`.",
        ]
    )
    for item in aggregate_summary.get("rediscovery_summary", {}).get("surviving_signatures", [])[:8]:
        lines.append(
            f"- `{item['signature']}` appeared {item['count']} times with {item['surviving_count']} surviving candidates."
        )
    lines.extend(
        [
            "",
            "## Discovery Answers",
        ]
    )
    for key, value in sorted((aggregate_summary.get("discovery_answers") or {}).items()):
        lines.append(f"- {key}: {value}")
    return "\n".join(lines).strip() + "\n"


def _find_unique_condition(condition_names: set[str], family: str) -> str | None:
    matches = sorted(name for name in condition_names if name.endswith(family))
    return matches[0] if len(matches) == 1 else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate repeated phase-7 TSP operator-suite runs.")
    parser.add_argument("--runs-root", required=True, help="Directory containing run_* subdirectories.")
    args = parser.parse_args()

    runs_root = Path(args.runs_root)
    run_dirs = sorted(path for path in runs_root.iterdir() if path.is_dir() and path.name.startswith("run_"))
    if not run_dirs:
        raise SystemExit(f"No run directories found under {runs_root}")

    aggregate_summary = summarize_aggregate(run_dirs)
    latest_suffix = run_dirs[-1].name.replace("run_", "")
    output_dir = runs_root / f"aggregate_{latest_suffix}"
    output_dir.mkdir(parents=True, exist_ok=True)
    _json_dump(output_dir / "aggregate_summary.json", aggregate_summary)

    report = render_markdown_report(aggregate_summary)
    (output_dir / "aggregate_report.md").write_text(report, encoding="utf-8")
    write_pdf_report(
        path=output_dir / "aggregate_report.pdf",
        run_name=output_dir.name,
        markdown_report=report,
        suite_summary=aggregate_summary,
        condition_payloads=[],
    )
    print(f"Completed phase-7 aggregate. Results written to: {output_dir}")


if __name__ == "__main__":
    main()
