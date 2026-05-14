from __future__ import annotations

import json
from typing import Any


def summarize_condition(condition_payload: dict[str, Any]) -> dict[str, Any]:
    epochs = condition_payload.get("epochs", [])
    replay_archives = condition_payload.get("replay_archives", {})
    accepted_novelties = [
        float(epoch.get("code_novelty", 0.0))
        for epoch in epochs
        if int(epoch.get("epoch_index", 0)) > 1 and bool((epoch.get("selection") or {}).get("accepted", False))
    ]
    complexities = [float(epoch.get("code_fingerprint", {}).get("complexity_score", 0.0)) for epoch in epochs]
    training_gaps = [float(epoch.get("training_summary", {}).get("mean_optimality_gap", 0.0)) for epoch in epochs]
    transfer_probe_gaps = [
        float(epoch.get("transfer_probe", {}).get("mean_optimality_gap", 0.0))
        for epoch in epochs
        if (epoch.get("transfer_probe") or {}).get("enabled")
    ]
    final_evaluation = condition_payload.get("final_evaluation") or {}
    final_tsplib_gap = float(final_evaluation.get("combined", {}).get("mean_tsplib_gap", 0.0))
    final_synthetic_gap = float(final_evaluation.get("combined", {}).get("mean_synthetic_gap", 0.0))
    final_transfer_gap = float(final_evaluation.get("combined", {}).get("mean_transfer_gap", 0.0))
    cumulative_novelty = sum(accepted_novelties)
    initial_probe = transfer_probe_gaps[0] if transfer_probe_gaps else (training_gaps[0] if training_gaps else 0.0)
    has_final_transfer = "mean_transfer_gap" in (final_evaluation.get("combined") or {})
    final_probe = final_transfer_gap if has_final_transfer else (transfer_probe_gaps[-1] if transfer_probe_gaps else 0.0)
    adaptation_efficiency = (initial_probe - final_probe) / cumulative_novelty if cumulative_novelty >= 1e-3 else 0.0
    last_epoch = epochs[-1] if epochs else {}
    accepted_epoch_count = sum(1 for epoch in epochs if bool((epoch.get("selection") or {}).get("accepted", False)))
    archive_sizes = {
        "worst_cases": len(replay_archives.get("worst_cases", [])),
        "failure_cases": len(replay_archives.get("failure_cases", condition_payload.get("archive", []))),
        "adversarial_layouts": len(replay_archives.get("adversarial_layouts", [])),
    }
    return {
        "condition_name": condition_payload["condition_name"],
        "replay_mode": condition_payload.get("replay", {}).get("mode", "none"),
        "selection_mode": condition_payload.get("selection", {}).get("mode", "score_only"),
        "compression_pressure": bool(condition_payload.get("selection", {}).get("compression_pressure", False)),
        "epoch_count": len(epochs),
        "accepted_epoch_count": accepted_epoch_count,
        "mean_training_gap_last": round(training_gaps[-1], 6) if training_gaps else 0.0,
        "mean_transfer_probe_gap_last": round(transfer_probe_gaps[-1], 6) if transfer_probe_gaps else 0.0,
        "mean_code_novelty": round(sum(accepted_novelties) / len(accepted_novelties), 6) if accepted_novelties else 0.0,
        "last_code_novelty": round(accepted_novelties[-1], 6) if accepted_novelties else 0.0,
        "mean_complexity": round(sum(complexities) / len(complexities), 6) if complexities else 0.0,
        "final_complexity": round(complexities[-1], 6) if complexities else 0.0,
        "adaptation_efficiency": round(adaptation_efficiency, 6),
        "final_tsplib_gap": round(final_tsplib_gap, 6),
        "final_synthetic_gap": round(final_synthetic_gap, 6),
        "final_transfer_gap": round(final_transfer_gap, 6),
        "archive_size": sum(archive_sizes.values()),
        "archive_sizes": archive_sizes,
        "elite_archive_size": len(condition_payload.get("elite_archive", [])),
        "final_behavior_profile": last_epoch.get("behavior_profile", "unknown"),
        "final_training_worst_instances": last_epoch.get("training_summary", {}).get("worst_instances", []),
        "final_evaluation": final_evaluation,
    }


def summarize_suite(condition_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    conditions = [summarize_condition(payload) for payload in condition_payloads]
    best_transfer = min(conditions, key=lambda item: item["final_transfer_gap"]) if conditions else None
    best_holdout = min(conditions, key=lambda item: item["final_tsplib_gap"]) if conditions else None
    best_synthetic = min(conditions, key=lambda item: item["final_synthetic_gap"]) if conditions else None
    return {
        "condition_count": len(conditions),
        "conditions": conditions,
        "best_transfer_condition": best_transfer["condition_name"] if best_transfer else None,
        "best_holdout_condition": best_holdout["condition_name"] if best_holdout else None,
        "best_synthetic_condition": best_synthetic["condition_name"] if best_synthetic else None,
    }


def render_markdown_report(
    suite_summary: dict[str, Any],
    llm_report: str | None = None,
    *,
    run_metadata: dict[str, Any] | None = None,
) -> str:
    conditions = suite_summary.get("conditions", [])
    lines = [
        "# Replay-Aware TSP Benchmark Report",
        "",
        "## Overview",
        f"- Condition count: {suite_summary.get('condition_count', 0)}.",
        f"- Best final transfer gap: `{suite_summary.get('best_transfer_condition')}`.",
        f"- Best TSPLIB holdout gap: `{suite_summary.get('best_holdout_condition')}`.",
        f"- Best synthetic holdout gap: `{suite_summary.get('best_synthetic_condition')}`.",
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
            "| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for condition in conditions:
        lines.append(
            "| {condition_name} | {replay_mode} | {selection_mode} | {compression_pressure} | {final_tsplib_gap} | {final_synthetic_gap} | {final_transfer_gap} | {mean_code_novelty} | {mean_complexity} | {adaptation_efficiency} |".format(
                **condition
            )
        )

    lines.append("")
    lines.append("## Condition Notes")
    for condition in conditions:
        lines.extend(
            [
                f"### {condition['condition_name']}",
                f"- Replay mode: `{condition['replay_mode']}` with selection mode `{condition['selection_mode']}`.",
                f"- Final transfer gaps: TSPLIB `{condition['final_tsplib_gap']}`, synthetic `{condition['final_synthetic_gap']}`, combined `{condition['final_transfer_gap']}`.",
                f"- Accepted-epoch count `{condition['accepted_epoch_count']}`, mean accepted code novelty `{condition['mean_code_novelty']}`, and final complexity `{condition['final_complexity']}`.",
                f"- Adaptation efficiency `{condition['adaptation_efficiency']}` and archive sizes `{condition['archive_sizes']}` / elite `{condition['elite_archive_size']}`.",
            ]
        )
        evaluation = condition.get("final_evaluation", {})
        for panel in evaluation.get("panels", []):
            family_text = ", ".join(
                f"{item['family']}={item['mean_optimality_gap']}"
                for item in panel.get("family_means", [])
            )
            lines.append(
                f"- Panel `{panel.get('panel_name')}` mean gap `{panel.get('mean_optimality_gap', 0.0)}` across {panel.get('instance_count', 0)} instances"
                + (f"; family means: {family_text}." if family_text else ".")
            )
        worst_cases = condition.get("final_training_worst_instances", [])
        if worst_cases:
            lines.append(f"- Worst recent training cases: {json.dumps(worst_cases[:3], sort_keys=True)}")
        lines.append("")

    if llm_report:
        lines.extend(["## Judge Appendix", llm_report.strip()])

    return "\n".join(lines).strip() + "\n"
