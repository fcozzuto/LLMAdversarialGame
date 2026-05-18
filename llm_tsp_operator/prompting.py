from __future__ import annotations

import json
from typing import Any

from .code_validation import TARGET_CHARACTERS, TARGET_NON_EMPTY_LINES


def build_generation_prompt(
    *,
    epoch_index: int,
    history: list[dict[str, Any]],
    training_panel: list[dict[str, Any]],
    host_scaffold: str,
    allowed_operator_types: list[str],
    curriculum_context: dict[str, Any] | None = None,
) -> str:
    parts = [
        "You are designing one deterministic reusable TSP operator for a constrained modular solver scaffold.",
        "Return only raw Python source code.",
        "The first line must be exactly: def build_operator():",
        "Do not use markdown fences.",
        "Do not include explanation before or after the function.",
        "Do not use imports.",
        "Return a dictionary only; do not write a full TSP solver.",
        "",
        "You are not allowed to rewrite the solver scaffold.",
        f"The current host scaffold is: {host_scaffold}.",
        "Your job is to propose one modular operator that can later be transplanted into multiple simple TSP scaffolds.",
        "",
        "Supported operator types:",
        "- candidate_ranker: score and reorder local-search candidate moves.",
        "- perturbation: choose a deterministic escape schedule for stagnation.",
        "- candidate_pruner: adapt candidate-list size from instance descriptors.",
        "- acceptance: control bounded worse-move acceptance for restart comparison.",
        "- restart_controller: control restart-count growth under stagnation.",
        "- scaffold_selector: choose among simple baseline scaffolds from instance descriptors.",
        f"- Allowed in this condition: {', '.join(allowed_operator_types)}.",
        "",
        "Fixed interface:",
        "- Return a dictionary with keys `name`, `description`, and `operator_type`.",
        "- Then include only fields valid for that operator type.",
        "",
        "Valid fields by operator type:",
        "- candidate_ranker: move_delta_weight, crossing_bonus, span_bonus, nn_rank_penalty, trap_bonus, cluster_bonus, long_edge_bonus",
        "- perturbation: primary_mode, secondary_mode, stagnation_threshold, strength, attempts, escalation_strength",
        "- candidate_pruner: base_candidate_limit, size_sensitivity, trap_bonus, grid_bonus, cluster_bonus, stagnation_bonus",
        "- acceptance: mode, base_threshold, temperature, stagnation_bonus, late_search_cooling",
        "- restart_controller: base_restart_count, max_restart_count, stagnation_trigger, seed_pool_size, restart_growth, use_perturbation_restarts",
        "- scaffold_selector: preferred_random_like, preferred_clustered, preferred_grid_like, preferred_two_cluster_bottleneck, preferred_elongated, preferred_nearest_neighbor_trap, fallback",
        "",
        "Design objective:",
        "- Improve held-out transfer without turning into a full solver rewrite.",
        "- Prefer compact, reusable operators over brittle tuning.",
        "- Use instance descriptors when they genuinely help transfer.",
        "- Avoid gratuitous lexical churn; later-stage edits should be smaller unless a failure mode is clear.",
        f"- Use at most {TARGET_NON_EMPTY_LINES} non-empty lines when feasible.",
        f"- Keep the function under {TARGET_CHARACTERS} characters when feasible.",
        "",
        f"Epoch: {epoch_index}",
        "",
        "Current training panel summary:",
        *[f"- {json.dumps(item, sort_keys=True)}" for item in training_panel],
    ]

    if history:
        latest = history[-1]
        latest_summary = latest.get("training_summary", {})
        parts.extend(
            [
                "",
                "Recent performance:",
                f"- Latest mean training gap: {latest_summary.get('mean_optimality_gap', 0.0)}",
                f"- Latest transfer probe gap: {latest.get('transfer_probe', {}).get('mean_optimality_gap', 'n/a')}",
                f"- Latest code novelty: {latest.get('code_novelty', 0.0)}",
                f"- Latest complexity score: {latest.get('code_fingerprint', {}).get('complexity_score', 0.0)}",
                f"- Latest runtime mean (ms): {latest_summary.get('mean_runtime_ms', 0.0)}",
                f"- Latest distance evaluations mean: {latest_summary.get('mean_distance_evaluations', 0.0)}",
            ]
        )
        latest_operator = latest.get("accepted_operator_code") or latest.get("executed_code")
        if latest_operator:
            parts.extend(
                [
                    "",
                    "Latest accepted operator code:",
                    "BEGIN_ACCEPTED_OPERATOR",
                    latest_operator,
                    "END_ACCEPTED_OPERATOR",
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
                f"- Elite archive size: {curriculum_context.get('elite_archive_size', 0)}",
                f"- Non-improving streak: {curriculum_context.get('non_improving_streak', 0)}",
                f"- Last acceptance reason: {curriculum_context.get('last_acceptance_reason', 'n/a')}",
            ]
        )
        archive_composition = curriculum_context.get("archive_composition", {})
        if archive_composition:
            experience = archive_composition.get("experience_archive", {})
            residual = archive_composition.get("residual_archive", {})
            parts.extend(
                [
                    f"- Experience-archive diversity: {experience.get('descriptor_diversity', 0.0)} and hardness: {experience.get('archive_hardness', 0.0)}",
                    f"- Residual-failure archive diversity: {residual.get('descriptor_diversity', 0.0)} and residual hardness: {residual.get('archive_residual_hardness', 0.0)}",
                ]
            )
        last_replay_selection = curriculum_context.get("last_replay_selection", {})
        if last_replay_selection:
            parts.extend(
                [
                    f"- Last replay selection diversity: {last_replay_selection.get('descriptor_diversity', 0.0)}",
                    f"- Last replay selection expected gap: {last_replay_selection.get('selected_mean_expected_gap', 0.0)}",
                    f"- Last replay selection residual gap: {last_replay_selection.get('selected_mean_residual_gap', 0.0)}",
                ]
            )
        if curriculum_context.get("worst_archive_examples"):
            parts.append("- Worst-performing training cases in archive:")
            for item in curriculum_context["worst_archive_examples"][:4]:
                parts.append(f"  {json.dumps(item, sort_keys=True)}")
        if curriculum_context.get("residual_archive_examples"):
            parts.append("- Residual failure cases in archive:")
            for item in curriculum_context["residual_archive_examples"][:4]:
                parts.append(f"  {json.dumps(item, sort_keys=True)}")
        if curriculum_context.get("compression_pressure"):
            parts.append("- Compression pressure is enabled: prefer simpler operators unless extra complexity clearly improves transfer.")
        if curriculum_context.get("require_substantial_change"):
            parts.append("- Substantial change is required because the current operator appears stuck or brittle.")

    parts.extend(
        [
            "",
            "Output only raw Python source code.",
        ]
    )
    return "\n".join(parts)
