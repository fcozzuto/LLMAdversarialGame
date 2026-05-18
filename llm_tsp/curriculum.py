from __future__ import annotations

from statistics import mean
from typing import Any

from .archive import EliteHeuristicArchive, EliteHeuristicEntry, ReplayArchive, ReplayEntry
from .behavioral_descriptors import behavioral_cell, behavioral_profile_label
from .benchmark import TSPInstance
from .code_features import code_fingerprint
from .config import TSPConditionConfig
from .replay_policies import archive_composition_snapshots, select_replay_entries


def build_curriculum_state(
    config: TSPConditionConfig,
    adversarial_instances: list[TSPInstance],
    *,
    reference_instances: list[TSPInstance] | None = None,
    difficulty_model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    adversarial_archive = ReplayArchive(max_size=max(config.replay.archive_max_size, len(adversarial_instances), 1))
    adversarial_archive.record_many(
        [
            ReplayEntry(
                instance=instance.to_dict(),
                gap=0.0,
                expected_gap=0.0,
                residual_gap=0.0,
                source_epoch=0,
                replay_kind="adversarial_layout",
            )
            for instance in adversarial_instances
        ]
    )
    return {
        "experience_archive": ReplayArchive(max_size=config.replay.experience_archive_max_size),
        "worst_archive": ReplayArchive(max_size=config.replay.archive_max_size),
        "failure_archive": ReplayArchive(max_size=config.replay.archive_max_size),
        "residual_archive": ReplayArchive(max_size=config.replay.archive_max_size, ranking_metric="residual_gap"),
        "adversarial_archive": adversarial_archive,
        "elite_archive": EliteHeuristicArchive(max_size=config.selection.elite_archive_max_size),
        "incumbent": None,
        "last_rejection": None,
        "last_replay_selection": {},
        "non_improving_streak": 0,
        "replay_reference_instances": list(reference_instances or adversarial_instances),
        "difficulty_model": difficulty_model,
        "selection_epoch_cursor": 0,
        "trace": [],
    }


def current_baseline_score(state: dict[str, Any]) -> float | None:
    incumbent = state.get("incumbent")
    if not incumbent:
        return None
    return float(incumbent.get("mean_training_score", 0.0))


def build_prompt_context(config: TSPConditionConfig, state: dict[str, Any]) -> dict[str, Any]:
    experience_archive = state["experience_archive"]
    elite_archive = state["elite_archive"]
    worst_archive = state["worst_archive"]
    failure_archive = state["failure_archive"]
    residual_archive = state["residual_archive"]
    adversarial_archive = state["adversarial_archive"]
    archive_snapshots = archive_composition_snapshots(state)
    return {
        "enabled": True,
        "replay_mode": config.replay.mode,
        "experience_archive_size": len(experience_archive),
        "worst_archive_size": len(worst_archive),
        "worst_archive_examples": [entry.to_dict() for entry in worst_archive.hardest(4)],
        "failure_archive_size": len(failure_archive),
        "failure_archive_examples": [entry.to_dict() for entry in failure_archive.hardest(4)],
        "residual_archive_size": len(residual_archive),
        "residual_archive_examples": [entry.to_dict() for entry in residual_archive.hardest(4, metric="residual_gap")],
        "adversarial_archive_size": len(adversarial_archive),
        "adversarial_archive_examples": [entry.to_dict() for entry in adversarial_archive.hardest(4)],
        "archive_composition": archive_snapshots,
        "elite_archive_size": len(elite_archive),
        "elite_profiles": elite_archive.profiles()[:6],
        "last_replay_selection": dict(state.get("last_replay_selection", {})),
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


def replay_pool(config: TSPConditionConfig, state: dict[str, Any]) -> list[dict[str, Any]]:
    selected = select_replay_entries(config, state)
    return [entry.to_dict() for entry in _dedupe_entries(selected, limit=len(selected))]


def record_epoch_outcome(
    *,
    config: TSPConditionConfig,
    state: dict[str, Any],
    epoch_index: int,
    executed_code: str,
    descriptor: dict[str, float],
    selection_decision: dict[str, Any] | None,
    training_results: list[dict[str, Any]],
    adversarial_probe_results: list[dict[str, Any]],
    mean_training_score: float,
) -> dict[str, Any]:
    experience_archive = state["experience_archive"]
    worst_archive = state["worst_archive"]
    failure_archive = state["failure_archive"]
    residual_archive = state["residual_archive"]
    adversarial_archive = state["adversarial_archive"]
    archive_events: dict[str, Any] = {}

    experience_archive.record_many(
        [
            ReplayEntry(
                instance=dict(item["instance"]),
                gap=float(item["optimality_gap"]),
                expected_gap=float(item.get("expected_gap", 0.0)),
                residual_gap=float(item.get("residual_gap", 0.0)),
                source_epoch=epoch_index,
                replay_kind="training_experience",
            )
            for item in training_results
        ]
    )
    if adversarial_probe_results:
        experience_archive.record_many(
            [
                ReplayEntry(
                    instance=dict(item["instance"]),
                    gap=float(item["optimality_gap"]),
                    expected_gap=float(item.get("expected_gap", 0.0)),
                    residual_gap=float(item.get("residual_gap", 0.0)),
                    source_epoch=epoch_index,
                    replay_kind="adversarial_experience",
                )
                for item in adversarial_probe_results
            ]
        )
    archive_events["experience_archive"] = {
        "archive_size": len(experience_archive),
    }

    worst_archive.record_many(
        [
            ReplayEntry(
                instance=dict(item["instance"]),
                gap=float(item["optimality_gap"]),
                expected_gap=float(item.get("expected_gap", 0.0)),
                residual_gap=float(item.get("residual_gap", 0.0)),
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
                    expected_gap=float(item.get("expected_gap", 0.0)),
                    residual_gap=float(item.get("residual_gap", 0.0)),
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

    residual_training = [
        item for item in training_results
        if float(item.get("residual_gap", 0.0)) > 0.0
    ]
    if residual_training:
        residual_archive.record_many(
            [
                ReplayEntry(
                    instance=dict(item["instance"]),
                    gap=float(item["optimality_gap"]),
                    expected_gap=float(item.get("expected_gap", 0.0)),
                    residual_gap=float(item.get("residual_gap", 0.0)),
                    source_epoch=epoch_index,
                    replay_kind="residual_failure_gap",
                )
                for item in residual_training
            ]
        )
        worst_residual = max(residual_training, key=lambda item: float(item.get("residual_gap", 0.0)))
        archive_events["residual_failures"] = {
            "count": len(residual_training),
            "worst_instance_name": worst_residual["instance"]["name"],
            "worst_residual_gap": round(float(worst_residual["residual_gap"]), 6),
            "archive_size": len(residual_archive),
        }

    if adversarial_probe_results:
        adversarial_archive.record_many(
            [
                ReplayEntry(
                    instance=dict(item["instance"]),
                    gap=float(item["optimality_gap"]),
                    expected_gap=float(item.get("expected_gap", 0.0)),
                    residual_gap=float(item.get("residual_gap", 0.0)),
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
        "replay_selection": dict(state.get("last_replay_selection", {})),
        "archive_composition": archive_composition_snapshots(state),
        "experience_archive_mean_gap": round(mean([entry.gap for entry in experience_archive.hardest(6)]), 6) if len(experience_archive) else 0.0,
        "worst_archive_mean_gap": round(mean([entry.gap for entry in worst_archive.hardest(4)]), 6) if len(worst_archive) else 0.0,
        "failure_archive_mean_gap": round(mean([entry.gap for entry in failure_archive.hardest(4)]), 6) if len(failure_archive) else 0.0,
        "residual_archive_mean_gap": round(mean([entry.residual_gap for entry in residual_archive.hardest(4, metric="residual_gap")]), 6) if len(residual_archive) else 0.0,
        "adversarial_archive_mean_gap": round(mean([entry.gap for entry in adversarial_archive.hardest(4)]), 6) if len(adversarial_archive) else 0.0,
    }
    state["trace"].append(trace_entry)
    return trace_entry
