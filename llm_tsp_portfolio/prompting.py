from __future__ import annotations

import json
from typing import Any

from .code_validation import TARGET_CHARACTERS, TARGET_NON_EMPTY_LINES


def build_generation_prompt(
    *,
    epoch_index: int,
    history: list[dict[str, Any]],
    training_panel: list[dict[str, Any]],
    heuristic_catalog: list[dict[str, Any]],
    heuristic_reference: dict[str, Any],
    curriculum_context: dict[str, Any] | None = None,
    single_shot: bool = False,
    include_online_state: bool = True,
) -> str:
    parts = [
        "You are designing one deterministic TSP hyper-heuristic controller.",
        "Return only raw Python source code.",
        "The first line must be exactly: def build_controller():",
        "Do not use markdown fences.",
        "Do not include explanation before or after the function.",
        "Do not use imports.",
        "Return a dictionary only; do not write a full TSP solver.",
        "",
        "Research goal:",
        "- Approach the oracle heuristic portfolio on unseen held-out TSPLIB instances.",
        "- Beat a fixed heuristic or random portfolio when possible.",
        "- Prefer interpretable instance-adaptive rules over opaque lexical churn.",
        "",
        "You are controlling a frozen portfolio of known components, not inventing new low-level operators.",
        "Your controller may only select, schedule, and tune known heuristics from the frozen portfolio below.",
        "",
        "Frozen portfolio:",
    ]
    for item in heuristic_catalog:
        parts.append(f"- {item['name']}: {item['description']} | components={', '.join(item['components'])}")
    parts.extend(
        [
            "",
            "Fixed interface:",
            "- Return a dictionary with the keys listed below.",
            "- Every heuristic-valued field must be one of the frozen portfolio names above.",
            "- The fields define interpretable instance-conditioned heuristic selection plus bounded online schedule adjustments.",
            "",
            "Required string fields:",
            "- name",
            "- description",
            "- default_heuristic",
            "- random_like_heuristic",
            "- clustered_heuristic",
            "- grid_like_heuristic",
            "- two_cluster_bottleneck_heuristic",
            "- corridor_heuristic",
            "- nearest_neighbor_trap_heuristic",
            "- stagnation_switch_heuristic",
            "",
            "Required bounded numeric fields:",
            "- stagnation_threshold int in [1, 6]",
            "- low_improvement_threshold float in [0.0, 0.25]",
            "- failed_perturbation_threshold int in [0, 4]",
            "- time_budget_trigger float in [0.2, 1.0]",
            "- candidate_limit_offset int in [-6, 6]",
            "- restart_offset int in [-3, 4]",
            "- temperature_scale float in [0.5, 1.8]",
            "- acceptance_bias float in [-0.01, 0.02]",
            "",
            "Instance descriptors available to reason about:",
            "- number of cities",
            "- coordinate spread",
            "- distance distribution statistics",
            "- nearest-neighbor distance mean, variance, and CV",
            "- MST length",
            "- convex hull ratio",
            "- clustering score and cluster separation",
            "- grid-likeness",
            "- bottleneck / two-cluster score",
            "- corridor score / elongated structure",
            "- nearest-neighbor trap score",
            "",
            "Training portfolio reference summary:",
            json.dumps(heuristic_reference, indent=2, sort_keys=True),
            "",
            f"Epoch: {epoch_index}",
            "",
            "Current training panel summary:",
            *[f"- {json.dumps(item, sort_keys=True)}" for item in training_panel],
        ]
    )
    if not single_shot and include_online_state:
        parts.extend(
            [
                "",
                "Online search-state features available to the adaptive controller runtime:",
                "- stagnation length",
                "- recent improvement rate",
                "- current tour length",
                "- number of accepted swaps",
                "- time budget used",
                "- edge-length skew in the current tour",
                "- failed perturbation count",
            ]
        )

    if history:
        latest = history[-1]
        latest_summary = latest.get("training_summary", {})
        parts.extend(
            [
                "",
                "Recent performance:",
                f"- Latest mean training gap: {latest_summary.get('mean_optimality_gap', 0.0)}",
                f"- Latest transfer probe gap: {latest.get('transfer_probe', {}).get('mean_optimality_gap', 'n/a')}",
                f"- Latest selector regret: {latest.get('transfer_probe', {}).get('mean_selector_regret', 'n/a')}",
                f"- Latest code novelty: {latest.get('code_novelty', 0.0)}",
                f"- Latest complexity score: {latest.get('code_fingerprint', {}).get('complexity_score', 0.0)}",
                f"- Latest runtime mean (ms): {latest_summary.get('mean_runtime_ms', 0.0)}",
                "",
                "Latest accepted controller code:",
                "BEGIN_ACCEPTED_CONTROLLER",
                str(latest.get("accepted_controller_code") or latest.get("executed_code") or ""),
                "END_ACCEPTED_CONTROLLER",
            ]
        )

    if curriculum_context and curriculum_context.get("enabled"):
        parts.extend(
            [
                "",
                "Replay-aware context:",
                f"- Replay mode: {curriculum_context.get('replay_mode', 'none')}",
                f"- Experience archive size: {curriculum_context.get('experience_archive_size', 0)}",
                f"- Worst-case archive size: {curriculum_context.get('worst_archive_size', 0)}",
                f"- Failure archive size: {curriculum_context.get('failure_archive_size', 0)}",
                f"- Residual-failure archive size: {curriculum_context.get('residual_archive_size', 0)}",
                f"- Adversarial-layout archive size: {curriculum_context.get('adversarial_archive_size', 0)}",
                f"- Non-improving streak: {curriculum_context.get('non_improving_streak', 0)}",
            ]
        )
        archive_composition = curriculum_context.get("archive_composition", {})
        if archive_composition:
            failure = archive_composition.get("failure_archive", {})
            residual = archive_composition.get("residual_archive", {})
            parts.extend(
                [
                    f"- Failure-archive diversity: {failure.get('descriptor_diversity', 0.0)} and hardness: {failure.get('archive_hardness', 0.0)}",
                    f"- Residual-failure diversity: {residual.get('descriptor_diversity', 0.0)} and residual hardness: {residual.get('archive_residual_hardness', 0.0)}",
                ]
            )
        if curriculum_context.get("compression_pressure"):
            parts.append("- Compression pressure is enabled: prefer smaller edits and simpler rules unless transfer clearly improves.")

    parts.extend(
        [
            "",
            "Design guidance:",
            "- Use clustered or bottleneck-aware heuristics only when the descriptors justify them.",
            "- If the training summary suggests broad random-like coverage, prefer general rules over over-specialization.",
            "- Small later-stage edits are better than thrashing.",
            "- Do not invent new heuristic names or new low-level operators.",
            f"- Use at most {TARGET_NON_EMPTY_LINES} non-empty lines when feasible.",
            f"- Keep the function under {TARGET_CHARACTERS} characters when feasible.",
        ]
    )
    if single_shot:
        parts.append("- This is a one-shot static selector baseline. Use only instance-conditioned rules; online search-state switching is not used in this condition.")
    elif not include_online_state:
        parts.append("- Online search-state features are disabled in this configuration, so rely on instance-conditioned control only.")
    else:
        parts.append("- This is an adaptive controller search, so improve held-out transfer while keeping the controller interpretable.")
    parts.extend(
        [
            "",
            "Output only raw Python source code.",
        ]
    )
    return "\n".join(parts)
