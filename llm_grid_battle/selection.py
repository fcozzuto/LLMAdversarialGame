from __future__ import annotations

from typing import Any

from .config import SelectionPolicyConfig


def _passed_auxiliary_gate(summary: dict[str, Any] | None) -> bool:
    if not summary or not summary.get("enabled"):
        return True
    return bool(summary.get("passed", False))


def decide_candidate_acceptance(
    *,
    policy: SelectionPolicyConfig,
    candidate_score: float,
    baseline_score: float | None,
    behavioral_distance: float,
    elite_distance: float,
    opens_new_elite_cell: bool,
    elite_cell_score: float | None,
    replay_summary: dict[str, Any] | None = None,
    holdout_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    score_delta = candidate_score - baseline_score if baseline_score is not None else None
    decision = {
        "mode": policy.mode,
        "accepted": True,
        "reason": "accept_all",
        "candidate_score": round(candidate_score, 4),
        "baseline_score": round(baseline_score, 4) if baseline_score is not None else None,
        "score_delta": round(score_delta, 4) if score_delta is not None else None,
        "behavioral_distance": round(behavioral_distance, 4),
        "elite_distance": round(elite_distance, 4),
        "opens_new_elite_cell": bool(opens_new_elite_cell),
        "elite_cell_score": round(elite_cell_score, 4) if elite_cell_score is not None else None,
        "novelty_threshold": round(policy.novelty_threshold, 4),
        "score_tolerance": round(policy.score_tolerance, 4),
        "replay_summary": replay_summary,
        "holdout_summary": holdout_summary,
    }
    if policy.mode == "accept_all":
        return decision

    current_gate_passed = False
    base_reason = "no_score_or_diversity_gain"
    if baseline_score is None:
        current_gate_passed = True
        base_reason = "no_baseline_for_opponent"
    elif float(score_delta or 0.0) >= 0.0:
        current_gate_passed = True
        base_reason = "score_improved_or_matched"
    else:
        diversity_pass = False
        if (
            policy.elite_archive_enabled
            and opens_new_elite_cell
            and elite_distance >= float(policy.elite_distance_threshold)
            and float(score_delta or 0.0) >= -float(policy.score_tolerance)
        ):
            diversity_pass = True
            base_reason = "opened_new_behavior_cell_within_score_tolerance"
        elif policy.elite_archive_enabled and elite_distance >= float(policy.elite_distance_threshold):
            if float(score_delta or 0.0) >= -float(policy.score_tolerance):
                diversity_pass = True
                base_reason = "diversity_gain_within_score_tolerance"
        elif policy.elite_archive_enabled and elite_cell_score is not None and float(score_delta or 0.0) >= -float(policy.elite_score_tolerance):
            diversity_pass = True
            base_reason = "competitive_with_existing_behavior_cell"
        elif behavioral_distance >= float(policy.novelty_threshold) and float(score_delta or 0.0) >= -float(policy.score_tolerance):
            diversity_pass = True
            base_reason = "behavioral_diversity_within_score_tolerance"
        current_gate_passed = diversity_pass

    if not current_gate_passed:
        decision["accepted"] = False
        decision["reason"] = base_reason
        return decision

    if not _passed_auxiliary_gate(replay_summary):
        decision["accepted"] = False
        decision["reason"] = "rejected_by_replay_checks"
        return decision

    if not _passed_auxiliary_gate(holdout_summary):
        decision["accepted"] = False
        decision["reason"] = "rejected_by_holdout_checks"
        return decision

    decision["reason"] = base_reason
    return decision
