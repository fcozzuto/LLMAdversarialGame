from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import random
from typing import Any

from .behavioral_descriptors import behavioral_cell, behavioral_distance, behavioral_profile_label


@dataclass
class ReplayEntry:
    instance: dict[str, Any]
    gap: float
    source_epoch: int
    replay_kind: str
    expected_gap: float = 0.0
    residual_gap: float = 0.0
    times_selected: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "instance": dict(self.instance),
            "gap": round(self.gap, 6),
            "expected_gap": round(self.expected_gap, 6),
            "residual_gap": round(self.residual_gap, 6),
            "source_epoch": self.source_epoch,
            "replay_kind": self.replay_kind,
            "times_selected": self.times_selected,
        }


class ReplayArchive:
    def __init__(self, max_size: int, *, ranking_metric: str = "gap") -> None:
        self.max_size = max(1, int(max_size))
        self.ranking_metric = str(ranking_metric)
        self._entries: list[ReplayEntry] = []
        self._cursor = 0

    def record(self, entry: ReplayEntry) -> bool:
        name = str(entry.instance.get("name", ""))
        for existing in self._entries:
            if str(existing.instance.get("name", "")) == name:
                if (
                    entry.gap > existing.gap
                    or entry.residual_gap > existing.residual_gap
                    or (entry.gap == existing.gap and entry.source_epoch >= existing.source_epoch)
                ):
                    existing.gap = entry.gap
                    existing.expected_gap = entry.expected_gap
                    existing.residual_gap = entry.residual_gap
                    existing.source_epoch = entry.source_epoch
                    existing.replay_kind = entry.replay_kind
                    existing.instance = dict(entry.instance)
                return False
        self._entries.append(entry)
        if len(self._entries) > self.max_size:
            self._entries = self.hardest(self.max_size, metric=self.ranking_metric)
        return True

    def record_many(self, entries: list[ReplayEntry]) -> int:
        recorded = 0
        for entry in entries:
            recorded += int(self.record(entry))
        return recorded

    def hardest(self, limit: int, *, metric: str = "gap") -> list[ReplayEntry]:
        ordered = sorted(
            self._entries,
            key=lambda item: (
                self._metric(item, metric),
                item.gap,
                item.source_epoch,
                -item.times_selected,
            ),
            reverse=True,
        )
        return list(ordered[: max(0, int(limit))])

    def randomish(self, limit: int) -> list[ReplayEntry]:
        if not self._entries:
            return []
        limit = min(max(0, int(limit)), len(self._entries))
        if limit <= 0:
            return []
        rng = random.Random((self._cursor * 9973) + len(self._entries))
        entries = rng.sample(self._entries, k=limit)
        self._cursor += 1
        return entries

    def select(self) -> ReplayEntry | None:
        if not self._entries:
            return None
        entry = self._entries[self._cursor % len(self._entries)]
        self._cursor = (self._cursor + 1) % len(self._entries)
        entry.times_selected += 1
        return entry

    def to_list(self) -> list[dict[str, Any]]:
        return [entry.to_dict() for entry in self._entries]

    def entries(self) -> list[ReplayEntry]:
        return list(self._entries)

    def note_selected(self, entries: list[ReplayEntry]) -> None:
        selected_names = {str(entry.instance.get("name", "")) for entry in entries}
        if not selected_names:
            return
        for entry in self._entries:
            if str(entry.instance.get("name", "")) in selected_names:
                entry.times_selected += 1

    def __len__(self) -> int:
        return len(self._entries)

    @staticmethod
    def _metric(entry: ReplayEntry, name: str) -> float:
        if name == "residual_gap":
            return float(entry.residual_gap)
        if name == "expected_gap":
            return float(entry.expected_gap)
        return float(entry.gap)


FailureArchive = ReplayArchive


@dataclass
class EliteHeuristicEntry:
    cell: str
    behavior_profile: str
    code: str
    descriptor: dict[str, float]
    fingerprint: str
    score: float
    source_epoch: int
    selection_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "cell": self.cell,
            "behavior_profile": self.behavior_profile,
            "code": self.code,
            "descriptor": dict(self.descriptor),
            "fingerprint": self.fingerprint,
            "score": round(self.score, 6),
            "source_epoch": self.source_epoch,
            "selection_reason": self.selection_reason,
        }


class EliteHeuristicArchive:
    def __init__(self, max_size: int) -> None:
        self.max_size = max(1, int(max_size))
        self._entries_by_cell: dict[str, EliteHeuristicEntry] = {}

    def cell_for(self, descriptor: dict[str, float] | None) -> str:
        return behavioral_cell(descriptor)

    def get(self, descriptor: dict[str, float] | None) -> EliteHeuristicEntry | None:
        return self._entries_by_cell.get(self.cell_for(descriptor))

    def nearest_distance(self, descriptor: dict[str, float] | None) -> float:
        if not descriptor or not self._entries_by_cell:
            return 0.0
        return min(behavioral_distance(descriptor, item.descriptor) for item in self._entries_by_cell.values())

    def would_open_cell(self, descriptor: dict[str, float] | None) -> bool:
        return self.cell_for(descriptor) not in self._entries_by_cell

    def coverage(self) -> int:
        return len(self._entries_by_cell)

    def record(self, entry: EliteHeuristicEntry, *, score_tolerance: float) -> tuple[bool, str]:
        existing = self._entries_by_cell.get(entry.cell)
        if existing is None:
            self._entries_by_cell[entry.cell] = entry
            self._trim()
            return True, "opened_new_behavior_cell"
        if entry.score >= existing.score - float(score_tolerance):
            if entry.score > existing.score or entry.source_epoch >= existing.source_epoch:
                self._entries_by_cell[entry.cell] = entry
                return True, "replaced_or_refreshed_behavior_cell"
        return False, "did_not_improve_behavior_cell"

    def profiles(self) -> list[str]:
        return sorted({item.behavior_profile for item in self._entries_by_cell.values()})

    def to_list(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in sorted(self._entries_by_cell.values(), key=lambda item: item.source_epoch)]

    def _trim(self) -> None:
        if len(self._entries_by_cell) <= self.max_size:
            return
        survivors = sorted(self._entries_by_cell.values(), key=lambda item: (item.score, item.source_epoch), reverse=True)[: self.max_size]
        self._entries_by_cell = {item.cell: item for item in survivors}

    def __len__(self) -> int:
        return len(self._entries_by_cell)

    def default_profile(self, descriptor: dict[str, float] | None) -> str:
        return behavioral_profile_label(descriptor)
