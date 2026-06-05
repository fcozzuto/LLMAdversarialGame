from __future__ import annotations

from typing import Any


def summarize_condition(condition_payload: dict[str, Any]) -> dict[str, Any]:
    epochs = condition_payload.get("epochs", [])
    accepted_epochs = [epoch for epoch in epochs if bool(epoch.get("accepted", False))]
    generation_error_epochs = [epoch for epoch in epochs if epoch.get("generation_error")]
    fallback_epochs = [epoch for epoch in epochs if bool(epoch.get("generation_fallback_used", False))]
    final = condition_payload["final_evaluation"]
    holdout = final["holdout"]
    return {
        "condition_name": condition_payload["condition_name"],
        "execution_mode": condition_payload["execution_mode"],
        "epoch_count": len(epochs),
        "accepted_epoch_count": len(accepted_epochs),
        "generation_error_epoch_count": len(generation_error_epochs),
        "fallback_epoch_count": len(fallback_epochs),
        "train_feasibility_rate": float(final["train"]["feasibility_rate"]),
        "train_penalized_gap": float(final["train"]["mean_penalized_gap"]),
        "train_feasible_gap": float(final["train"]["mean_feasible_gap"] or 0.0),
        "heldout_feasibility_rate": float(holdout["feasibility_rate"]),
        "heldout_penalized_gap": float(holdout["mean_penalized_gap"]),
        "heldout_feasible_gap": float(holdout["mean_feasible_gap"] or 0.0),
        "heldout_runtime_ms": float(holdout["mean_runtime_ms"]),
        "mean_code_novelty": _mean([float(epoch.get("code_novelty", 0.0)) for epoch in accepted_epochs]),
        "mean_complexity": _mean([float(epoch.get("complexity", 0.0)) for epoch in accepted_epochs]),
        "robustness_dispersion": _family_dispersion(holdout["family_means"]),
        "skipped": bool(condition_payload.get("skipped", False)),
        "skip_reason": condition_payload.get("skip_reason"),
    }


def summarize_suite(condition_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    summaries = [summarize_condition(payload) for payload in condition_payloads]
    valid = [item for item in summaries if not bool(item.get("skipped", False))]
    best = min(valid, key=lambda item: (item["heldout_penalized_gap"], -item["heldout_feasibility_rate"])) if valid else None
    return {
        "condition_count": len(summaries),
        "best_heldout_condition": best["condition_name"] if best else None,
        "conditions": summaries,
    }


def render_markdown_report(condition_payloads: list[dict[str, Any]], suite_summary: dict[str, Any], *, judge_text_value: str | None = None) -> str:
    lines = [
        "# Phase 9 CVRP Suite Report",
        "",
        "## Overview",
        f"- Condition count: {suite_summary.get('condition_count', 0)}.",
        f"- Best held-out condition: `{suite_summary.get('best_heldout_condition')}`.",
        "",
        "## Condition Summary",
        "| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in suite_summary.get("conditions", []):
        feasible_gap = item["heldout_feasible_gap"] if item["heldout_feasibility_rate"] > 0 else "n/a"
        lines.append(
            "| {condition_name} | {execution_mode} | {heldout_feasibility_rate} | {heldout_penalized_gap} | {feasible_gap} | {heldout_runtime_ms} | {accepted_epoch_count} | {fallback_epoch_count} | {generation_error_epoch_count} | {mean_code_novelty} | {mean_complexity} |".format(
                condition_name=item["condition_name"],
                execution_mode=item["execution_mode"],
                heldout_feasibility_rate=item["heldout_feasibility_rate"],
                heldout_penalized_gap=item["heldout_penalized_gap"],
                feasible_gap=feasible_gap,
                heldout_runtime_ms=item["heldout_runtime_ms"],
                accepted_epoch_count=item["accepted_epoch_count"],
                fallback_epoch_count=item["fallback_epoch_count"],
                generation_error_epoch_count=item["generation_error_epoch_count"],
                mean_code_novelty=item["mean_code_novelty"],
                mean_complexity=item["mean_complexity"],
            )
        )
    lines.extend(["", "## Condition Notes"])
    for payload, item in zip(condition_payloads, suite_summary.get("conditions", [])):
        lines.extend(
            [
                f"### {item['condition_name']}",
                f"- Execution mode: `{item['execution_mode']}`.",
                f"- Train feasibility rate: {item['train_feasibility_rate']}.",
                f"- Train penalized gap: {item['train_penalized_gap']}.",
                f"- Held-out feasibility rate: {item['heldout_feasibility_rate']}.",
                f"- Held-out penalized gap: {item['heldout_penalized_gap']}.",
                f"- Held-out runtime ms: {item['heldout_runtime_ms']}.",
                f"- Accepted epoch count: {item['accepted_epoch_count']}.",
                f"- Fallback epoch count: {item['fallback_epoch_count']}.",
                f"- Generation-error epoch count: {item['generation_error_epoch_count']}.",
                f"- Robustness dispersion across held-out structure families: {item['robustness_dispersion']}.",
            ]
        )
        holdout = payload["final_evaluation"]["holdout"]
        if holdout["worst_instances"]:
            lines.append("- Worst held-out instances:")
            for record in holdout["worst_instances"]:
                lines.append(
                    f"  - {record['instance_name']}: feasible={record['feasible']}, penalized gap={record['penalized_gap']}, errors={record['errors']}"
                )
    if judge_text_value:
        lines.extend(["", "## Judge Note", judge_text_value.strip()])
    return "\n".join(lines).strip() + "\n"


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 6) if values else 0.0


def _family_dispersion(family_means: list[dict[str, Any]]) -> float:
    penalized = [float(item["mean_penalized_gap"]) for item in family_means if item.get("mean_penalized_gap") is not None]
    if len(penalized) < 2:
        return 0.0
    mean_value = sum(penalized) / len(penalized)
    variance = sum((value - mean_value) ** 2 for value in penalized) / len(penalized)
    return round(variance ** 0.5, 6)
