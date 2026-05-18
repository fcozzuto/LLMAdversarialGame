from __future__ import annotations

import json
from typing import Any


def summarize_condition(condition_payload: dict[str, Any]) -> dict[str, Any]:
    epochs = condition_payload.get("epochs", [])
    execution_mode = str(condition_payload.get("execution_mode", "modular_operator"))
    accepted_novelties = [
        float(epoch.get("code_novelty", 0.0))
        for epoch in epochs
        if int(epoch.get("epoch_index", 0)) > 1 and bool((epoch.get("selection") or {}).get("accepted", False))
    ]
    complexities = [float(epoch.get("code_fingerprint", {}).get("complexity_score", 0.0)) for epoch in epochs if epoch.get("code_fingerprint")]
    training_gaps = [float(epoch.get("training_summary", {}).get("mean_optimality_gap", 0.0)) for epoch in epochs if epoch.get("training_summary")]
    transfer_probe_gaps = [
        float(epoch.get("transfer_probe", {}).get("mean_optimality_gap", 0.0))
        for epoch in epochs
        if (epoch.get("transfer_probe") or {}).get("enabled")
    ]
    final_evaluation = condition_payload.get("final_evaluation") or {}
    final_tsplib_gap = float(final_evaluation.get("combined", {}).get("mean_tsplib_gap", 0.0))
    final_family_gap = float(final_evaluation.get("combined", {}).get("mean_family_gap", 0.0))
    final_transfer_gap = float(final_evaluation.get("combined", {}).get("mean_transfer_gap", 0.0))
    cumulative_novelty = sum(accepted_novelties)
    initial_probe = transfer_probe_gaps[0] if transfer_probe_gaps else (training_gaps[0] if training_gaps else 0.0)
    final_probe = final_transfer_gap if "mean_transfer_gap" in (final_evaluation.get("combined") or {}) else (transfer_probe_gaps[-1] if transfer_probe_gaps else 0.0)
    adaptation_efficiency = (initial_probe - final_probe) / cumulative_novelty if cumulative_novelty >= 1e-3 else 0.0
    validation = condition_payload.get("operator_validation") or {}
    last_epoch = epochs[-1] if epochs else {}
    return {
        "condition_name": condition_payload.get("condition_name", "unknown_condition"),
        "execution_mode": execution_mode,
        "replay_mode": str(condition_payload.get("replay", {}).get("mode", "none")),
        "selection_mode": str(condition_payload.get("selection", {}).get("mode", "score_only")),
        "compression_pressure": bool(condition_payload.get("selection", {}).get("compression_pressure", False)),
        "epoch_count": len(epochs),
        "accepted_epoch_count": sum(1 for epoch in epochs if bool((epoch.get("selection") or {}).get("accepted", False))),
        "mean_code_novelty": round(sum(accepted_novelties) / len(accepted_novelties), 6) if accepted_novelties else 0.0,
        "last_code_novelty": round(accepted_novelties[-1], 6) if accepted_novelties else 0.0,
        "mean_complexity": round(sum(complexities) / len(complexities), 6) if complexities else 0.0,
        "final_complexity": round(complexities[-1], 6) if complexities else 0.0,
        "adaptation_efficiency": round(adaptation_efficiency, 6),
        "final_tsplib_gap": round(final_tsplib_gap, 6),
        "final_family_gap": round(final_family_gap, 6),
        "final_transfer_gap": round(final_transfer_gap, 6),
        "final_training_gap": round(float(last_epoch.get("training_summary", {}).get("mean_optimality_gap", 0.0)), 6) if last_epoch else 0.0,
        "mean_runtime_ms_last": round(float(last_epoch.get("training_summary", {}).get("mean_runtime_ms", 0.0)), 6) if last_epoch else 0.0,
        "mean_distance_evaluations_last": round(float(last_epoch.get("training_summary", {}).get("mean_distance_evaluations", 0.0)), 6) if last_epoch else 0.0,
        "operator_type": str((condition_payload.get("accepted_operator_spec") or {}).get("operator_type", "n/a")),
        "host_scaffold": str(condition_payload.get("operator", {}).get("host_scaffold", "n/a")),
        "surviving_candidate": bool(validation.get("surviving_candidate", False)),
        "transplant_mean_gap_delta": round(float(validation.get("transplant_results", {}).get("mean_gap_delta", 0.0)), 6) if validation else 0.0,
        "positive_scaffold_count": int(validation.get("transplant_results", {}).get("positive_scaffold_count", 0)) if validation else 0,
        "pareto_gap_delta": round(float(validation.get("pareto_results", {}).get("gap_delta", 0.0)), 6) if validation else 0.0,
        "pareto_runtime_inflation": round(float(validation.get("pareto_results", {}).get("runtime_inflation", 0.0)), 6) if validation else 0.0,
        "operator_validation": validation,
    }


def summarize_suite(condition_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    conditions = [summarize_condition(payload) for payload in condition_payloads]
    best_transfer = min(conditions, key=lambda item: item["final_transfer_gap"]) if conditions else None
    best_tsplib = min(conditions, key=lambda item: item["final_tsplib_gap"]) if conditions else None
    survivors = [item["condition_name"] for item in conditions if item["surviving_candidate"]]
    return {
        "condition_count": len(conditions),
        "conditions": conditions,
        "best_transfer_condition": best_transfer["condition_name"] if best_transfer else None,
        "best_tsplib_condition": best_tsplib["condition_name"] if best_tsplib else None,
        "surviving_conditions": survivors,
    }


def render_markdown_report(
    suite_summary: dict[str, Any],
    llm_report: str | None = None,
    *,
    run_metadata: dict[str, Any] | None = None,
) -> str:
    conditions = suite_summary.get("conditions", [])
    lines = [
        "# Modular Operator Discovery TSP Report",
        "",
        "## Overview",
        f"- Condition count: {suite_summary.get('condition_count', 0)}.",
        f"- Best final transfer gap: `{suite_summary.get('best_transfer_condition')}`.",
        f"- Best held-out TSPLIB gap: `{suite_summary.get('best_tsplib_condition')}`.",
        f"- Surviving modular candidates: {', '.join(suite_summary.get('surviving_conditions', [])) or 'none'}.",
    ]
    if run_metadata:
        lines.extend(
            [
                "",
                "## Run Metadata",
                *[f"- {key}: {value}" for key, value in run_metadata.items()],
            ]
        )
    lines.extend(
        [
            "",
            "## Condition Comparison",
            "| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
        ]
    )
    for condition in conditions:
        lines.append(
            "| {condition_name} | {execution_mode} | {replay_mode} | {selection_mode} | {final_tsplib_gap} | {final_family_gap} | {final_transfer_gap} | {mean_code_novelty} | {mean_complexity} | {surviving_candidate} | {transplant_mean_gap_delta} | {pareto_runtime_inflation} |".format(
                **condition
            )
        )
    lines.append("")
    lines.append("## Condition Notes")
    for condition in conditions:
        lines.extend(
            [
                f"### {condition['condition_name']}",
                f"- Execution mode `{condition['execution_mode']}` on host scaffold `{condition['host_scaffold']}`.",
                f"- Final gaps: TSPLIB `{condition['final_tsplib_gap']}`, family holdout `{condition['final_family_gap']}`, combined `{condition['final_transfer_gap']}`.",
                f"- Accepted novelty `{condition['mean_code_novelty']}`, complexity `{condition['mean_complexity']}`, and adaptation efficiency `{condition['adaptation_efficiency']}`.",
                f"- Last-epoch runtime `{condition['mean_runtime_ms_last']}` ms and distance evaluations `{condition['mean_distance_evaluations_last']}`.",
                f"- Validation: surviving `{condition['surviving_candidate']}`, transplant delta `{condition['transplant_mean_gap_delta']}`, positive scaffolds `{condition['positive_scaffold_count']}`, Pareto runtime inflation `{condition['pareto_runtime_inflation']}`.",
            ]
        )
        validation = condition.get("operator_validation", {})
        if validation:
            lines.append(f"- Validation summary: {json.dumps(validation.get('pareto_results', {}), sort_keys=True)}")
        lines.append("")
    if llm_report:
        lines.extend(["## Judge Appendix", llm_report.strip()])
    return "\n".join(lines).strip() + "\n"
