from __future__ import annotations

import json
from typing import Any

from llm_tsp.code_features import complexity_score


def summarize_condition(condition_payload: dict[str, Any]) -> dict[str, Any]:
    epochs = condition_payload.get("epochs", [])
    execution_mode = str(condition_payload.get("execution_mode", "adaptive_controller"))
    accepted_novelties = [
        float(epoch.get("code_novelty", 0.0))
        for epoch in epochs
        if int(epoch.get("epoch_index", 0)) > 1 and bool((epoch.get("selection") or {}).get("accepted", False))
    ]
    complexities = [float(epoch.get("code_fingerprint", {}).get("complexity_score", 0.0)) for epoch in epochs if epoch.get("code_fingerprint")]
    if not complexities:
        controller_code = str(condition_payload.get("accepted_controller_code") or "")
        if controller_code:
            complexities = [complexity_score(controller_code)]
    training_gaps = [float(epoch.get("training_summary", {}).get("mean_optimality_gap", 0.0)) for epoch in epochs if epoch.get("training_summary")]
    transfer_probe_gaps = [
        float(epoch.get("transfer_probe", {}).get("mean_optimality_gap", 0.0))
        for epoch in epochs
        if (epoch.get("transfer_probe") or {}).get("enabled")
    ]
    final_evaluation = condition_payload.get("final_evaluation") or {}
    combined = final_evaluation.get("combined", {})
    final_tsplib_gap = float(combined.get("mean_tsplib_gap", 0.0))
    final_family_gap = float(combined.get("mean_family_gap", 0.0))
    final_transfer_gap = float(combined.get("mean_transfer_gap", 0.0))
    final_selector_regret = float(combined.get("mean_selector_regret", 0.0))
    final_tsplib_runtime_ms = float(combined.get("mean_tsplib_runtime_ms", 0.0))
    cumulative_novelty = sum(accepted_novelties)
    initial_probe = transfer_probe_gaps[0] if transfer_probe_gaps else (training_gaps[0] if training_gaps else 0.0)
    final_probe = final_transfer_gap if "mean_transfer_gap" in combined else (transfer_probe_gaps[-1] if transfer_probe_gaps else 0.0)
    adaptation_efficiency = (initial_probe - final_probe) / cumulative_novelty if cumulative_novelty >= 1e-3 else 0.0
    controller = condition_payload.get("accepted_controller_spec") or {}
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
        "final_selector_regret": round(final_selector_regret, 6),
        "final_tsplib_runtime_ms": round(final_tsplib_runtime_ms, 6),
        "final_training_gap": round(float(last_epoch.get("training_summary", {}).get("mean_optimality_gap", 0.0)), 6) if last_epoch else 0.0,
        "mean_runtime_ms_last": round(float(last_epoch.get("training_summary", {}).get("mean_runtime_ms", 0.0)), 6) if last_epoch else 0.0,
        "mean_distance_evaluations_last": round(float(last_epoch.get("training_summary", {}).get("mean_distance_evaluations", 0.0)), 6) if last_epoch else 0.0,
        "selected_fixed_heuristic": str(condition_payload.get("selected_fixed_heuristic", "")),
        "controller_signature": str(condition_payload.get("controller_signature", "")),
        "controller_rules": controller,
    }


def summarize_suite(condition_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    conditions = [summarize_condition(payload) for payload in condition_payloads]
    best_fixed = next((item for item in conditions if item["execution_mode"] == "best_fixed"), None)
    oracle = next((item for item in conditions if item["execution_mode"] == "oracle_selector"), None)
    baseline_runtime = max(1e-9, float(best_fixed["final_tsplib_runtime_ms"])) if best_fixed else 1.0
    oracle_gap = float(oracle["final_tsplib_gap"]) if oracle else 0.0
    for condition in conditions:
        runtime_inflation = (float(condition["final_tsplib_runtime_ms"]) / baseline_runtime) - 1.0
        condition["final_runtime_inflation"] = round(runtime_inflation, 6)
        condition["final_runtime_adjusted_gap"] = round(
            float(condition["final_tsplib_gap"]) * (1.0 + max(0.0, runtime_inflation)),
            6,
        )
        condition["final_selector_regret"] = round(float(condition["final_tsplib_gap"]) - oracle_gap, 6) if oracle else condition["final_selector_regret"]

    frontier = _pareto_frontier(conditions)
    for condition in conditions:
        condition["pareto_efficient"] = condition["condition_name"] in frontier

    best_transfer = min(conditions, key=lambda item: item["final_transfer_gap"]) if conditions else None
    best_tsplib = min(conditions, key=lambda item: item["final_tsplib_gap"]) if conditions else None
    best_regret = min(conditions, key=lambda item: item["final_selector_regret"]) if conditions else None
    return {
        "condition_count": len(conditions),
        "conditions": conditions,
        "best_transfer_condition": best_transfer["condition_name"] if best_transfer else None,
        "best_tsplib_condition": best_tsplib["condition_name"] if best_tsplib else None,
        "best_regret_condition": best_regret["condition_name"] if best_regret else None,
        "pareto_conditions": sorted(frontier),
    }


def render_markdown_report(
    suite_summary: dict[str, Any],
    llm_report: str | None = None,
    *,
    run_metadata: dict[str, Any] | None = None,
) -> str:
    conditions = suite_summary.get("conditions", [])
    lines = [
        "# Adaptive Heuristic Portfolio TSP Report",
        "",
        "## Overview",
        f"- Condition count: {suite_summary.get('condition_count', 0)}.",
        f"- Best held-out TSPLIB gap: `{suite_summary.get('best_tsplib_condition')}`.",
        f"- Best combined transfer gap: `{suite_summary.get('best_transfer_condition')}`.",
        f"- Lowest selector regret: `{suite_summary.get('best_regret_condition')}`.",
        f"- Pareto-efficient conditions: {', '.join(suite_summary.get('pareto_conditions', [])) or 'none'}.",
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
            "| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for condition in conditions:
        lines.append(
            "| {condition_name} | {execution_mode} | {replay_mode} | {final_tsplib_gap} | {final_selector_regret} | {final_tsplib_runtime_ms} | {final_runtime_adjusted_gap} | {final_family_gap} | {final_transfer_gap} | {mean_code_novelty} | {mean_complexity} | {pareto_efficient} |".format(
                **condition
            )
        )
    lines.append("")
    lines.append("## Condition Notes")
    for condition in conditions:
        lines.extend(
            [
                f"### {condition['condition_name']}",
                f"- Execution mode `{condition['execution_mode']}` with replay `{condition['replay_mode']}`.",
                f"- Final held-out gap `{condition['final_tsplib_gap']}`, selector regret `{condition['final_selector_regret']}`, runtime-adjusted gap `{condition['final_runtime_adjusted_gap']}`.",
                f"- Family transfer `{condition['final_family_gap']}` and combined transfer `{condition['final_transfer_gap']}`.",
                f"- Runtime `{condition['final_tsplib_runtime_ms']}` ms, runtime inflation `{condition['final_runtime_inflation']}`, mean novelty `{condition['mean_code_novelty']}`, and complexity `{condition['mean_complexity']}`.",
                f"- Pareto efficient: `{condition['pareto_efficient']}`.",
            ]
        )
        if condition["selected_fixed_heuristic"]:
            lines.append(f"- Fixed heuristic choice: `{condition['selected_fixed_heuristic']}`.")
        if condition["controller_signature"]:
            lines.append(f"- Controller signature: `{condition['controller_signature']}`.")
        if condition.get("controller_rules"):
            lines.append(f"- Controller rule summary: {json.dumps(condition['controller_rules'], sort_keys=True)}")
        lines.append("")
    if llm_report:
        lines.extend(["## Judge Appendix", llm_report.strip()])
    return "\n".join(lines).strip() + "\n"


def _pareto_frontier(conditions: list[dict[str, Any]]) -> set[str]:
    frontier: set[str] = set()
    for candidate in conditions:
        dominated = False
        for reference in conditions:
            if reference is candidate:
                continue
            if _dominates(reference, candidate):
                dominated = True
                break
        if not dominated:
            frontier.add(str(candidate["condition_name"]))
    return frontier


def _dominates(reference: dict[str, Any], candidate: dict[str, Any]) -> bool:
    non_worse = (
        float(reference["final_tsplib_gap"]) <= float(candidate["final_tsplib_gap"])
        and float(reference["final_tsplib_runtime_ms"]) <= float(candidate["final_tsplib_runtime_ms"])
        and float(reference["mean_complexity"]) <= float(candidate["mean_complexity"])
    )
    strictly_better = (
        float(reference["final_tsplib_gap"]) < float(candidate["final_tsplib_gap"])
        or float(reference["final_tsplib_runtime_ms"]) < float(candidate["final_tsplib_runtime_ms"])
        or float(reference["mean_complexity"]) < float(candidate["mean_complexity"])
    )
    return non_worse and strictly_better
