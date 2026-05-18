from __future__ import annotations

import json
from typing import Any


def _active_archive_key(replay_mode: str) -> str:
    if replay_mode in {"random", "stratified_random", "diversity_weighted"}:
        return "experience_archive"
    if replay_mode in {"residual_failure", "diversity_residual"}:
        return "residual_archive"
    if replay_mode == "failure" or replay_mode == "diversity_failure":
        return "worst_archive"
    return "experience_archive"


def summarize_condition(condition_payload: dict[str, Any]) -> dict[str, Any]:
    epochs = condition_payload.get("epochs", [])
    replay_archives = condition_payload.get("replay_archives", {})
    replay_mode = condition_payload.get("replay", {}).get("mode", "none")
    active_archive_key = _active_archive_key(str(replay_mode))
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
        "experience_cases": len(replay_archives.get("experience_cases", [])),
        "worst_cases": len(replay_archives.get("worst_cases", [])),
        "failure_cases": len(replay_archives.get("failure_cases", condition_payload.get("archive", []))),
        "residual_failures": len(replay_archives.get("residual_failures", [])),
        "adversarial_layouts": len(replay_archives.get("adversarial_layouts", [])),
    }
    archive_diversities = [
        float((epoch.get("curriculum") or {}).get("archive_composition", {}).get(active_archive_key, {}).get("descriptor_diversity", 0.0))
        for epoch in epochs
    ]
    archive_hardnesses = [
        float((epoch.get("curriculum") or {}).get("archive_composition", {}).get(active_archive_key, {}).get("archive_hardness", 0.0))
        for epoch in epochs
    ]
    archive_size_biases = [
        float((epoch.get("curriculum") or {}).get("archive_composition", {}).get(active_archive_key, {}).get("size_bias", 0.0))
        for epoch in epochs
    ]
    failure_concentrations = [
        float((epoch.get("curriculum") or {}).get("archive_composition", {}).get(active_archive_key, {}).get("replay_failure_concentration", 0.0))
        for epoch in epochs
    ]
    replay_selection_diversities = [
        float((epoch.get("curriculum") or {}).get("replay_selection", {}).get("descriptor_diversity", 0.0))
        for epoch in epochs
        if (epoch.get("curriculum") or {}).get("replay_selection", {}).get("entry_count", 0) > 0
    ]
    replay_selection_expected = [
        float((epoch.get("curriculum") or {}).get("replay_selection", {}).get("selected_mean_expected_gap", 0.0))
        for epoch in epochs
        if (epoch.get("curriculum") or {}).get("replay_selection", {}).get("entry_count", 0) > 0
    ]
    replay_selection_residual = [
        float((epoch.get("curriculum") or {}).get("replay_selection", {}).get("selected_mean_residual_gap", 0.0))
        for epoch in epochs
        if (epoch.get("curriculum") or {}).get("replay_selection", {}).get("entry_count", 0) > 0
    ]
    last_curriculum = (last_epoch.get("curriculum") or {}) if epochs else {}
    final_archive_composition = (last_curriculum.get("archive_composition") or {}).get(active_archive_key, {})
    return {
        "condition_name": condition_payload["condition_name"],
        "replay_mode": replay_mode,
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
        "active_archive_key": active_archive_key,
        "mean_archive_descriptor_diversity": round(sum(archive_diversities) / len(archive_diversities), 6) if archive_diversities else 0.0,
        "final_archive_descriptor_diversity": round(float(final_archive_composition.get("descriptor_diversity", 0.0)), 6),
        "mean_archive_hardness": round(sum(archive_hardnesses) / len(archive_hardnesses), 6) if archive_hardnesses else 0.0,
        "final_archive_hardness": round(float(final_archive_composition.get("archive_hardness", 0.0)), 6),
        "mean_archive_size_bias": round(sum(archive_size_biases) / len(archive_size_biases), 6) if archive_size_biases else 0.0,
        "final_archive_size_bias": round(float(final_archive_composition.get("size_bias", 0.0)), 6),
        "mean_replay_failure_concentration": round(sum(failure_concentrations) / len(failure_concentrations), 6) if failure_concentrations else 0.0,
        "final_replay_failure_concentration": round(float(final_archive_composition.get("replay_failure_concentration", 0.0)), 6),
        "mean_replay_selection_diversity": round(sum(replay_selection_diversities) / len(replay_selection_diversities), 6) if replay_selection_diversities else 0.0,
        "mean_selected_expected_gap": round(sum(replay_selection_expected) / len(replay_selection_expected), 6) if replay_selection_expected else 0.0,
        "mean_selected_residual_gap": round(sum(replay_selection_residual) / len(replay_selection_residual), 6) if replay_selection_residual else 0.0,
        "elite_archive_size": len(condition_payload.get("elite_archive", [])),
        "final_behavior_profile": last_epoch.get("behavior_profile", "unknown"),
        "final_training_worst_instances": last_epoch.get("training_summary", {}).get("worst_instances", []),
        "final_evaluation": final_evaluation,
        "difficulty_model": condition_payload.get("difficulty_model", {}),
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
            "| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for condition in conditions:
        lines.append(
            "| {condition_name} | {replay_mode} | {selection_mode} | {compression_pressure} | {final_tsplib_gap} | {final_synthetic_gap} | {final_transfer_gap} | {mean_archive_descriptor_diversity} | {mean_archive_hardness} | {mean_replay_failure_concentration} | {mean_code_novelty} | {mean_complexity} | {adaptation_efficiency} |".format(
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
                f"- Active replay archive `{condition['active_archive_key']}` with mean diversity `{condition['mean_archive_descriptor_diversity']}`, mean hardness `{condition['mean_archive_hardness']}`, size bias `{condition['mean_archive_size_bias']}`, and failure concentration `{condition['mean_replay_failure_concentration']}`.",
                f"- Replay selection diversity `{condition['mean_replay_selection_diversity']}`, mean selected expected gap `{condition['mean_selected_expected_gap']}`, mean selected residual gap `{condition['mean_selected_residual_gap']}`.",
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
