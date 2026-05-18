from __future__ import annotations

import math
import random
from typing import Any

from .archive import ReplayArchive, ReplayEntry
from .instance_features import descriptor_distance, stratification_key, summarize_archive_composition


def select_replay_entries(config: Any, state: dict[str, Any]) -> list[ReplayEntry]:
    count = max(0, int(config.replay.replay_instance_count))
    if count <= 0 or str(config.replay.mode) == "none":
        return []

    mode = str(config.replay.mode)
    experience_pool = _combined_unique_entries([state["experience_archive"], state["adversarial_archive"]])
    raw_failure_pool = state["worst_archive"].hardest(max(count * 4, count), metric="gap")
    residual_pool = state["residual_archive"].hardest(max(count * 4, count), metric="residual_gap")
    reference_instances = list(state.get("replay_reference_instances", []))

    if mode == "random":
        selected = _uniform_random(experience_pool, count=count, seed=_selection_seed(state, 101))
    elif mode == "failure":
        selected = raw_failure_pool[:count]
    elif mode == "stratified_random":
        selected = _stratified_random(experience_pool, count=count, seed=_selection_seed(state, 211))
    elif mode == "diversity_weighted":
        selected = _diversity_weighted(
            experience_pool,
            count=count,
            seed=_selection_seed(state, 307),
            severity_key="gap",
        )
    elif mode == "residual_failure":
        selected = residual_pool[:count]
    elif mode == "diversity_failure":
        selected = _diversity_weighted(
            raw_failure_pool,
            count=count,
            seed=_selection_seed(state, 401),
            severity_key="gap",
        )
    elif mode == "diversity_residual":
        selected = _diversity_weighted(
            residual_pool,
            count=count,
            seed=_selection_seed(state, 503),
            severity_key="residual_gap",
        )
    else:
        selected = []

    _note_selected_across_archives(
        state,
        selected,
        archive_names=["experience_archive", "worst_archive", "failure_archive", "residual_archive", "adversarial_archive"],
    )
    state["last_replay_selection"] = summarize_selection(selected, reference_instances=reference_instances)
    return selected


def summarize_selection(entries: list[ReplayEntry], *, reference_instances: list[Any]) -> dict[str, Any]:
    composition = summarize_archive_composition(entries, reference_instances=reference_instances).to_dict()
    composition["selected_instance_names"] = [str(entry.instance.get("name", "")) for entry in entries]
    composition["selected_replay_kinds"] = [str(entry.replay_kind) for entry in entries]
    composition["selected_mean_expected_gap"] = round(
        sum(float(entry.expected_gap) for entry in entries) / len(entries),
        6,
    ) if entries else 0.0
    composition["selected_mean_residual_gap"] = round(
        sum(float(entry.residual_gap) for entry in entries) / len(entries),
        6,
    ) if entries else 0.0
    return composition


def archive_composition_snapshots(state: dict[str, Any]) -> dict[str, Any]:
    reference_instances = list(state.get("replay_reference_instances", []))
    snapshots: dict[str, Any] = {}
    for key in ("experience_archive", "worst_archive", "failure_archive", "residual_archive", "adversarial_archive"):
        archive = state.get(key)
        if archive is None:
            continue
        snapshots[key] = summarize_archive_composition(
            archive.entries(),
            reference_instances=reference_instances,
        ).to_dict()
    return snapshots


def _selection_seed(state: dict[str, Any], salt: int) -> int:
    epoch_index = int(state.get("selection_epoch_cursor", 0))
    return (epoch_index * 104_729) + int(salt)


def _uniform_random(entries: list[ReplayEntry], *, count: int, seed: int) -> list[ReplayEntry]:
    if not entries:
        return []
    rng = random.Random(seed)
    count = min(max(0, int(count)), len(entries))
    return list(rng.sample(entries, k=count))


def _stratified_random(entries: list[ReplayEntry], *, count: int, seed: int) -> list[ReplayEntry]:
    if not entries:
        return []
    rng = random.Random(seed)
    groups: dict[str, list[ReplayEntry]] = {}
    for entry in entries:
        groups.setdefault(stratification_key(entry.instance), []).append(entry)
    ordered_keys = sorted(groups)
    selected: list[ReplayEntry] = []
    while ordered_keys and len(selected) < count:
        next_keys: list[str] = []
        for key in ordered_keys:
            pool = groups.get(key, [])
            if not pool:
                continue
            index = rng.randrange(len(pool))
            selected.append(pool.pop(index))
            if pool:
                next_keys.append(key)
            if len(selected) >= count:
                break
        ordered_keys = next_keys
    return selected[:count]


def _diversity_weighted(
    entries: list[ReplayEntry],
    *,
    count: int,
    seed: int,
    severity_key: str,
) -> list[ReplayEntry]:
    if not entries:
        return []
    rng = random.Random(seed)
    candidate_pool = list(entries)
    selected: list[ReplayEntry] = []
    while candidate_pool and len(selected) < count:
        best_index = 0
        best_score = None
        for index, entry in enumerate(candidate_pool):
            diversity_bonus = 0.0
            if selected:
                diversity_bonus = min(descriptor_distance(entry.instance, chosen.instance) for chosen in selected)
            under_selection_bonus = 1.0 / (1.0 + float(entry.times_selected))
            severity_bonus = _severity(entry, severity_key)
            tiny_noise = rng.random() * 1e-6
            score = (0.55 * diversity_bonus) + (0.3 * under_selection_bonus) + (0.15 * severity_bonus) + tiny_noise
            if best_score is None or score > best_score:
                best_score = score
                best_index = index
        selected.append(candidate_pool.pop(best_index))
    return selected


def _severity(entry: ReplayEntry, key: str) -> float:
    if key == "residual_gap":
        return max(0.0, float(entry.residual_gap))
    return max(0.0, float(entry.gap))


def _combined_unique_entries(archives: list[ReplayArchive]) -> list[ReplayEntry]:
    merged: dict[str, ReplayEntry] = {}
    for archive in archives:
        for entry in archive.entries():
            name = str(entry.instance.get("name", ""))
            if name not in merged or _merge_priority(entry) > _merge_priority(merged[name]):
                merged[name] = entry
    return list(sorted(merged.values(), key=lambda entry: entry.instance.get("name", "")))


def _merge_priority(entry: ReplayEntry) -> tuple[float, float, int]:
    return (
        float(entry.residual_gap),
        float(entry.gap),
        int(entry.source_epoch),
    )


def _note_selected_across_archives(
    state: dict[str, Any],
    entries: list[ReplayEntry],
    *,
    archive_names: list[str],
) -> None:
    if not entries:
        return
    for name in archive_names:
        archive = state.get(name)
        if isinstance(archive, ReplayArchive):
            archive.note_selected(entries)
