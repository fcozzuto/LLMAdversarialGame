from __future__ import annotations

from typing import Any

from .config import SelectionPolicyConfig


def decide_candidate_acceptance(
    *,
    policy: SelectionPolicyConfig,
    candidate_score: float,
    baseline_score: float | None,
    behavioral_distance: float,
) -> dict[str, Any]:
    decision = {
        "mode": policy.mode,
        "accepted": True,
        "reason": "accept_all",
        "candidate_score": round(candidate_score, 4),
        "baseline_score": round(baseline_score, 4) if baseline_score is not None else None,
        "score_delta": round(candidate_score - baseline_score, 4) if baseline_score is not None else None,
        "behavioral_distance": round(behavioral_distance, 4),
        "novelty_threshold": round(policy.novelty_threshold, 4),
        "score_tolerance": round(policy.score_tolerance, 4),
    }
    if policy.mode == "accept_all":
        return decision

    if baseline_score is None:
        decision["reason"] = "no_baseline_for_opponent"
        return decision

    score_delta = candidate_score - baseline_score
    decision["score_delta"] = round(score_delta, 4)
    if score_delta >= 0:
        decision["reason"] = "score_improved_or_matched"
        return decision

    if behavioral_distance >= float(policy.novelty_threshold) and score_delta >= -float(policy.score_tolerance):
        decision["reason"] = "diversity_gain_within_score_tolerance"
        return decision

    decision["accepted"] = False
    decision["reason"] = "no_score_or_diversity_gain"
    return decision
