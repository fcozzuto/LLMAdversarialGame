from __future__ import annotations

from statistics import mean
from typing import Any

from .archive import EliteHeuristicArchive, EliteHeuristicEntry, ReplayArchive, ReplayEntry
from .behavioral_descriptors import behavioral_cell, behavioral_profile_label
from .benchmark import CVRPInstance
from .code_features import code_fingerprint
from .config import CVRPConditionConfig


def build_curriculum_state(config: CVRPConditionConfig, adversarial_instances: list[CVRPInstance]) -> dict[str, Any]:
    adversarial_archive = ReplayArchive(max_size=max(config.replay.archive_max_size, len(adversarial_instances), 1))
    adversarial_archive.record_many(
        [
            ReplayEntry(
                instance=instance.to_dict(),
                gap=0.0,
                source_epoch=0,
                replay_kind="adversarial_layout",
            )
            for instance in adversarial_instances
        ]
    )
    return {
        "worst_archive": ReplayArchive(max_size=config.replay.archive_max_size),
        "failure_archive": ReplayArchive(max_size=config.replay.archive_max_size),
        "adversarial_archive": adversarial_archive,
        "elite_archive": EliteHeuristicArchive(max_size=config.selection.elite_archive_max_size),
        "incumbent": None,
        "last_rejection": None,
        "non_improving_streak": 0,
        "trace": [],
    }


def current_baseline_score(state: dict[str, Any]) -> float | None:
    incumbent = state.get("incumbent")
    if not incumbent:
        return None
    return float(incumbent.get("mean_training_score", 0.0))


def build_prompt_context(config: CVRPConditionConfig, state: dict[str, Any]) -> dict[str, Any]:
    elite_archive = state["elite_archive"]
    worst_archive = state["worst_archive"]
    failure_archive = state["failure_archive"]
    adversarial_archive = state["adversarial_archive"]
    return {
        "enabled": True,
        "replay_mode": config.replay.mode,
        "worst_archive_size": len(worst_archive),
        "worst_archive_examples": [entry.to_dict() for entry in worst_archive.hardest(4)],
        "failure_archive_size": len(failure_archive),
        "failure_archive_examples": [entry.to_dict() for entry in failure_archive.hardest(4)],
        "adversarial_archive_size": len(adversarial_archive),
        "adversarial_archive_examples": [entry.to_dict() for entry in adversarial_archive.hardest(4)],
        "elite_archive_size": len(elite_archive),
        "elite_profiles": elite_archive.profiles()[:6],
        "non_improving_streak": int(state.get("non_improving_streak", 0)),
        "last_acceptance_reason": (state.get("incumbent") or {}).get("selection_reason", "n/a"),
        "compression_pressure": bool(config.selection.compression_pressure),
        "require_substantial_change": int(state.get("non_improving_streak", 0)) >= 2,
    }


def _dedupe_entries(entries: list[ReplayEntry], *, limit: int) -> list[ReplayEntry]:
    selected: list[ReplayEntry] = []
    seen_names: set[str] = set()
    for entry in entries:
        name = str(entry.instance.get("name", ""))
        if name in seen_names:
            continue
        selected.append(entry)
        seen_names.add(name)
        if len(selected) >= limit:
            break
    return selected


def replay_pool(config: CVRPConditionConfig, state: dict[str, Any]) -> list[dict[str, Any]]:
    count = max(0, int(config.replay.replay_instance_count))
    if count <= 0:
        return []
    if config.replay.mode == "random":
        selected = _dedupe_entries(
            state["worst_archive"].randomish(count) + state["adversarial_archive"].randomish(count),
            limit=count,
        )
        state["worst_archive"].note_selected(selected)
        state["adversarial_archive"].note_selected(selected)
        return [entry.to_dict() for entry in selected]
    if config.replay.mode == "failure":
        selected = state["failure_archive"].hardest(count)
        state["failure_archive"].note_selected(selected)
        return [entry.to_dict() for entry in selected]
    return []


def record_epoch_outcome(
    *,
    config: CVRPConditionConfig,
    state: dict[str, Any],
    epoch_index: int,
    executed_code: str,
    descriptor: dict[str, float],
    selection_decision: dict[str, Any] | None,
    training_results: list[dict[str, Any]],
    adversarial_probe_results: list[dict[str, Any]],
    mean_training_score: float,
) -> dict[str, Any]:
    worst_archive = state["worst_archive"]
    failure_archive = state["failure_archive"]
    adversarial_archive = state["adversarial_archive"]
    archive_events: dict[str, Any] = {}

    worst_archive.record_many(
        [
            ReplayEntry(
                instance=dict(item["instance"]),
                gap=float(item["optimality_gap"]),
                source_epoch=epoch_index,
                replay_kind="worst_training_gap",
            )
            for item in training_results
        ]
    )
    if training_results:
        worst_training = max(training_results, key=lambda item: float(item.get("optimality_gap", 0.0)))
        archive_events["worst_training"] = {
            "archive_size": len(worst_archive),
            "worst_instance_name": worst_training["instance"]["name"],
            "worst_gap": round(float(worst_training["optimality_gap"]), 6),
        }

    catastrophic = [
        item for item in training_results
        if float(item.get("optimality_gap", 0.0)) >= float(config.replay.catastrophic_gap_threshold)
    ]
    if catastrophic:
        failure_archive.record_many(
            [
                ReplayEntry(
                    instance=dict(item["instance"]),
                    gap=float(item["optimality_gap"]),
                    source_epoch=epoch_index,
                    replay_kind="catastrophic_gap",
                )
                for item in catastrophic
            ]
        )
        worst = max(catastrophic, key=lambda item: float(item.get("optimality_gap", 0.0)))
        archive_events["catastrophic_failures"] = {
            "count": len(catastrophic),
            "worst_instance_name": worst["instance"]["name"],
            "worst_gap": round(float(worst["optimality_gap"]), 6),
            "archive_size": len(failure_archive),
        }

    if adversarial_probe_results:
        adversarial_archive.record_many(
            [
                ReplayEntry(
                    instance=dict(item["instance"]),
                    gap=float(item["optimality_gap"]),
                    source_epoch=epoch_index,
                    replay_kind="adversarial_layout",
                )
                for item in adversarial_probe_results
            ]
        )
        worst_adversarial = max(adversarial_probe_results, key=lambda item: float(item.get("optimality_gap", 0.0)))
        archive_events["adversarial_layouts"] = {
            "archive_size": len(adversarial_archive),
            "worst_instance_name": worst_adversarial["instance"]["name"],
            "worst_gap": round(float(worst_adversarial["optimality_gap"]), 6),
        }

    elite_event = None
    if selection_decision and bool(selection_decision.get("accepted", False)):
        incumbent = {
            "epoch_index": epoch_index,
            "code": executed_code,
            "fingerprint": code_fingerprint(executed_code),
            "descriptor": descriptor,
            "behavior_profile": behavioral_profile_label(descriptor),
            "behavior_cell": behavioral_cell(descriptor),
            "selection_reason": selection_decision.get("reason"),
            "mean_training_score": mean_training_score,
        }
        state["incumbent"] = incumbent
        state["last_rejection"] = None
        state["non_improving_streak"] = 0
        if config.selection.elite_archive_enabled:
            elite_entry = EliteHeuristicEntry(
                cell=behavioral_cell(descriptor),
                behavior_profile=behavioral_profile_label(descriptor),
                code=executed_code,
                descriptor=descriptor,
                fingerprint=code_fingerprint(executed_code),
                score=mean_training_score,
                source_epoch=epoch_index,
                selection_reason=str(selection_decision.get("reason", "")),
            )
            recorded, reason = state["elite_archive"].record(
                elite_entry,
                score_tolerance=config.selection.elite_score_tolerance,
            )
            elite_event = {
                "recorded": recorded,
                "reason": reason,
                "coverage": state["elite_archive"].coverage(),
            }
    elif selection_decision:
        state["non_improving_streak"] = int(state.get("non_improving_streak", 0)) + 1
        state["last_rejection"] = {
            "epoch_index": epoch_index,
            "reason": selection_decision.get("reason"),
            "score_delta": selection_decision.get("score_delta"),
            "behavioral_distance": selection_decision.get("behavioral_distance"),
        }

    trace_entry = {
        "epoch_index": epoch_index,
        "selection": selection_decision,
        "archive_events": archive_events,
        "elite_event": elite_event,
        "worst_archive_mean_gap": round(mean([entry.gap for entry in worst_archive.hardest(4)]), 6) if len(worst_archive) else 0.0,
        "failure_archive_mean_gap": round(mean([entry.gap for entry in failure_archive.hardest(4)]), 6) if len(failure_archive) else 0.0,
        "adversarial_archive_mean_gap": round(mean([entry.gap for entry in adversarial_archive.hardest(4)]), 6) if len(adversarial_archive) else 0.0,
    }
    state["trace"].append(trace_entry)
    return trace_entry
