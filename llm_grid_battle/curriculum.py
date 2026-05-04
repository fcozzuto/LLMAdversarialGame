from __future__ import annotations

from statistics import mean
from typing import Any

from .archive import ArchiveEntry, NemesisArchive
from .behavioral_descriptors import behavioral_profile_label
from .code_fingerprints import code_fingerprint
from .config import ConditionConfig, OpponentSpec
from .opponent_library import resolve_opponent_spec


def curriculum_enabled(config: ConditionConfig) -> bool:
    return bool(config.curriculum.enabled and config.curriculum.focal_agent and config.curriculum.opponent_agent)


def build_curriculum_state(config: ConditionConfig) -> dict[str, Any]:
    archive_policy = config.curriculum.archive
    return {
        "enabled": curriculum_enabled(config),
        "focal_agent": config.curriculum.focal_agent,
        "opponent_agent": config.curriculum.opponent_agent,
        "pool_cursor": 0,
        "loss_streak": 0,
        "archive": NemesisArchive(max_size=archive_policy.max_size),
        "accepted_scores_by_opponent": {},
        "incumbent": None,
        "last_rejection": None,
        "trace": [],
    }


def _cyclic_pool_pick(pool: list[OpponentSpec], state: dict[str, Any], stride: int) -> OpponentSpec:
    if not pool:
        raise ValueError("Curriculum opponent_pool cannot be empty when curriculum is enabled.")
    index = int(state.get("pool_cursor", 0)) % len(pool)
    state["pool_cursor"] = index + max(1, int(stride))
    return pool[index]


def resolve_epoch_opponent(
    *,
    config: ConditionConfig,
    state: dict[str, Any],
    epoch_index: int,
) -> dict[str, Any] | None:
    if not state.get("enabled"):
        return None

    archive_policy = config.curriculum.archive
    archive = state["archive"]
    if (
        archive_policy.enabled
        and archive_policy.reintroduce_every > 0
        and epoch_index > 1
        and len(archive) > 0
        and epoch_index % archive_policy.reintroduce_every == 0
    ):
        entry = archive.select()
        if entry is not None:
            agent, label, metadata = resolve_opponent_spec(
                OpponentSpec(
                    label=entry.label,
                    provider=entry.provider,
                    model=entry.model,
                    regenerate_each_epoch=False,
                    metadata=entry.metadata,
                ),
                slot_name=config.curriculum.opponent_agent,
            )
            return {
                "agent": agent,
                "label": label,
                "source": "archive",
                "metadata": metadata,
                "fixed_code": entry.code,
                "cache_key": f"{config.curriculum.opponent_agent}:archive:{label}:{code_fingerprint(entry.code)}",
            }

    pool = config.curriculum.opponent_pool
    if not pool:
        return None

    if config.curriculum.mode == "fixed_predator":
        spec = pool[0]
    else:
        spec = _cyclic_pool_pick(pool, state, config.curriculum.rotation_stride)
    agent, label, metadata = resolve_opponent_spec(spec, slot_name=config.curriculum.opponent_agent)
    source = "fixed_pool" if config.curriculum.mode == "fixed_predator" else "pool"
    return {
        "agent": agent,
        "label": label,
        "source": source,
        "metadata": metadata,
        "fixed_code": None,
        "cache_key": f"{config.curriculum.opponent_agent}:{label}",
    }


def current_baseline_score(state: dict[str, Any], opponent_label: str) -> float | None:
    values = state.get("accepted_scores_by_opponent", {}).get(opponent_label, [])
    if not values:
        return None
    recent = values[-3:]
    return float(mean(recent))


def build_prompt_context(
    *,
    config: ConditionConfig,
    state: dict[str, Any],
    agent_name: str,
    epoch_index: int,
    opponent_info: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not state.get("enabled") or agent_name != state.get("focal_agent"):
        return None

    pressure = config.curriculum.pressure
    loss_streak = int(state.get("loss_streak", 0))
    incumbent = state.get("incumbent")
    rejection = state.get("last_rejection")
    opponent_label = str(opponent_info.get("label", "")) if opponent_info else ""
    baseline_score = current_baseline_score(state, opponent_label) if opponent_label else None
    loss_triggered = bool(
        pressure.enabled
        and (
            loss_streak >= int(pressure.loss_streak_trigger)
            or (
                rejection is not None
                and abs(float(rejection.get("score_delta", 0.0) or 0.0)) >= float(pressure.score_margin_trigger)
            )
        )
    )
    return {
        "enabled": True,
        "mode": config.curriculum.mode,
        "opponent_label": opponent_label,
        "opponent_source": opponent_info.get("source") if opponent_info else "",
        "opponent_metadata": opponent_info.get("metadata", {}) if opponent_info else {},
        "archive_size": len(state.get("archive")),
        "loss_streak": loss_streak,
        "loss_triggered": loss_triggered,
        "force_substantial_change": bool(loss_triggered and pressure.require_substantial_change),
        "mutation_instruction": pressure.custom_instruction if loss_triggered else "",
        "accepted_incumbent": incumbent,
        "last_rejection": rejection,
        "baseline_score_against_current_opponent": round(baseline_score, 4) if baseline_score is not None else None,
        "epoch_index": epoch_index,
    }


def record_epoch_outcome(
    *,
    config: ConditionConfig,
    state: dict[str, Any],
    epoch_result: dict[str, Any],
    opponent_info: dict[str, Any] | None,
    focal_descriptor: dict[str, float] | None,
    selection_decision: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not state.get("enabled"):
        return None

    focal_agent = str(state["focal_agent"])
    opponent_agent = str(state["opponent_agent"])
    focal_score = float(epoch_result["scores"][focal_agent])
    opponent_score = float(epoch_result["scores"][opponent_agent])
    score_margin = focal_score - opponent_score
    if score_margin < 0:
        state["loss_streak"] = int(state.get("loss_streak", 0)) + 1
    else:
        state["loss_streak"] = 0

    archive_event = None
    if opponent_info and config.curriculum.archive.enabled and score_margin <= -float(config.curriculum.archive.min_score_margin):
        entry = ArchiveEntry(
            label=str(opponent_info["label"]),
            provider=str(opponent_info["agent"].provider),
            model=str(opponent_info["agent"].model),
            code=str(epoch_result["submitted_codes"][opponent_agent]),
            metadata=dict(opponent_info.get("metadata", {})),
            source_epoch=int(epoch_result["epoch_index"]),
            score_margin=abs(score_margin),
        )
        added = state["archive"].record(entry)
        archive_event = {
            "recorded": added,
            "label": entry.label,
            "source_epoch": entry.source_epoch,
            "score_margin": round(entry.score_margin, 4),
            "archive_size": len(state["archive"]),
        }

    if opponent_info:
        if selection_decision is None or bool(selection_decision.get("accepted", False)):
            scores_by_opponent = state["accepted_scores_by_opponent"].setdefault(str(opponent_info["label"]), [])
            scores_by_opponent.append(focal_score)

    if selection_decision and bool(selection_decision.get("accepted", False)):
        incumbent = {
            "epoch_index": int(epoch_result["epoch_index"]),
            "code": str(epoch_result["submitted_codes"][focal_agent]),
            "fingerprint": code_fingerprint(str(epoch_result["submitted_codes"][focal_agent])),
            "descriptor": focal_descriptor or {},
            "behavior_profile": behavioral_profile_label(focal_descriptor or {}),
            "selection_reason": selection_decision.get("reason"),
        }
        state["incumbent"] = incumbent
        state["last_rejection"] = None
    elif selection_decision:
        state["last_rejection"] = {
            "epoch_index": int(epoch_result["epoch_index"]),
            "reason": selection_decision.get("reason"),
            "score_delta": selection_decision.get("score_delta"),
            "behavioral_distance": selection_decision.get("behavioral_distance"),
            "candidate_fingerprint": code_fingerprint(str(epoch_result["submitted_codes"][focal_agent])),
        }

    trace_entry = {
        "epoch_index": int(epoch_result["epoch_index"]),
        "mode": config.curriculum.mode,
        "opponent_label": str(opponent_info["label"]) if opponent_info else "",
        "opponent_source": str(opponent_info["source"]) if opponent_info else "",
        "loss_streak_after_epoch": int(state.get("loss_streak", 0)),
        "score_margin": round(score_margin, 4),
        "selection": selection_decision,
        "archive_event": archive_event,
    }
    state["trace"].append(trace_entry)
    return trace_entry


def resolve_holdout_pool(config: ConditionConfig) -> list[dict[str, Any]]:
    if not config.curriculum.evaluation.enabled:
        return []
    holdout: list[dict[str, Any]] = []
    for spec in config.curriculum.evaluation.holdout_opponents:
        agent, label, metadata = resolve_opponent_spec(spec, slot_name=config.curriculum.opponent_agent)
        holdout.append(
            {
                "agent": agent,
                "label": label,
                "metadata": metadata,
                "cache_key": f"holdout:{label}",
            }
        )
    return holdout
