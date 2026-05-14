from __future__ import annotations

import json
from typing import Any

from .code_validation import TARGET_CHARACTERS, TARGET_NON_EMPTY_LINES


def build_generation_prompt(
    *,
    epoch_index: int,
    history: list[dict[str, Any]],
    training_panel: list[dict[str, Any]],
    curriculum_context: dict[str, Any] | None = None,
) -> str:
    parts = [
        "You are designing a deterministic heuristic configuration for a constrained TSP solver scaffold.",
        "Return only raw Python source code.",
        "The first line must be exactly: def build_heuristic():",
        "Do not use markdown fences.",
        "Do not include explanation before or after the function.",
        "Do not use imports.",
        "Return a dictionary only; do not write a full TSP solver.",
        "",
        "The fixed scaffold already implements:",
        "- nearest-neighbor style construction",
        "- candidate pruning",
        "- 2-opt local search",
        "- bounded 3-opt sampling",
        "- route perturbation",
        "- deterministic restart logic",
        "- simple decomposition/clustering bias",
        "- deterministic acceptance schedules for perturbed restarts",
        "",
        "You may only control these operator families through the returned dictionary:",
        "- construction.seed_mode: farthest_from_centroid | nearest_centroid | lowest_x | highest_y",
        "- construction.candidate_limit: 4..40",
        "- construction.lookahead_limit: 1..8",
        "- construction.distance_weight: 0.4..2.5",
        "- construction.density_penalty: 0.0..1.2",
        "- construction.angle_penalty: 0.0..1.0",
        "- construction.regret_bonus: 0.0..1.0",
        "- construction.cluster_mode: none | x_sweep | y_sweep | radial",
        "- construction.cluster_count: 1..6",
        "- construction.cluster_bonus: 0.0..1.0",
        "- local_search.two_opt_passes: 1..8",
        "- local_search.two_opt_candidate_limit: 6..40",
        "- local_search.use_three_opt: bool",
        "- local_search.three_opt_samples: 0..20",
        "- local_search.or_opt_span: 1..3",
        "- perturbation.enabled: bool",
        "- perturbation.mode: double_bridge | segment_reversal | shuffle_window",
        "- perturbation.strength: 1..4",
        "- perturbation.attempts: 1..4",
        "- restart.restart_count: 1..10",
        "- restart.seed_pool_size: 1..10",
        "- restart.use_perturbation_restarts: bool",
        "- acceptance.mode: improving_only | threshold | annealed",
        "- acceptance.worse_acceptance_threshold: 0.0..0.05",
        "- acceptance.annealing_temperature: 0.0..0.05",
        "",
        "Design objective:",
        "- Reduce mean optimality gap on the training panel.",
        "- Improve transfer to unseen held-out and synthetic families when feedback indicates regressions there.",
        "- Prefer reusable changes over lexical churn.",
        "- Keep later-stage edits compact unless a clear failure mode requires a structural shift.",
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
            ]
        )
        worst_cases = latest_summary.get("worst_instances", [])
        if worst_cases:
            parts.append("- Worst recent cases:")
            for item in worst_cases[:4]:
                parts.append(f"  {json.dumps(item, sort_keys=True)}")
        incumbent_code = latest.get("accepted_code") or latest.get("executed_code")
        if incumbent_code:
            parts.extend(
                [
                    "",
                    "Latest accepted heuristic code:",
                    "BEGIN_ACCEPTED_HEURISTIC",
                    incumbent_code,
                    "END_ACCEPTED_HEURISTIC",
                ]
            )

    if curriculum_context and curriculum_context.get("enabled"):
        parts.extend(
            [
                "",
                "Replay-aware context:",
                f"- Replay mode: {curriculum_context.get('replay_mode', 'none')}",
                f"- Worst-case archive size: {curriculum_context.get('worst_archive_size', 0)}",
                f"- Failure archive size: {curriculum_context.get('failure_archive_size', 0)}",
                f"- Adversarial-layout archive size: {curriculum_context.get('adversarial_archive_size', 0)}",
                f"- Elite archive size: {curriculum_context.get('elite_archive_size', 0)}",
                f"- Non-improving streak: {curriculum_context.get('non_improving_streak', 0)}",
                f"- Last acceptance reason: {curriculum_context.get('last_acceptance_reason', 'n/a')}",
            ]
        )
        if curriculum_context.get("worst_archive_examples"):
            parts.append("- Worst-performing training cases in archive:")
            for item in curriculum_context["worst_archive_examples"][:4]:
                parts.append(f"  {json.dumps(item, sort_keys=True)}")
        if curriculum_context.get("failure_archive_examples"):
            parts.append("- Catastrophic failure cases in archive:")
            for item in curriculum_context["failure_archive_examples"][:4]:
                parts.append(f"  {json.dumps(item, sort_keys=True)}")
        if curriculum_context.get("adversarial_archive_examples"):
            parts.append("- Adversarial geometric layouts tracked in archive:")
            for item in curriculum_context["adversarial_archive_examples"][:4]:
                parts.append(f"  {json.dumps(item, sort_keys=True)}")
        if curriculum_context.get("compression_pressure"):
            parts.append("- Compression pressure is enabled: prefer smaller edits and avoid unnecessary complexity increases.")
        if curriculum_context.get("require_substantial_change"):
            parts.append("- Substantial change is required because the current heuristic is stuck or failing badly.")

    parts.extend(
        [
            "",
            "Output only raw Python source code.",
        ]
    )
    return "\n".join(parts)
