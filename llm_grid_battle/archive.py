from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

from .behavioral_descriptors import behavioral_cell, behavioral_distance, behavioral_profile_label


@dataclass
class ArchiveEntry:
    label: str
    provider: str
    model: str
    code: str
    metadata: dict[str, Any] = field(default_factory=dict)
    source_epoch: int = 0
    score_margin: float = 0.0
    times_selected: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "provider": self.provider,
            "model": self.model,
            "code": self.code,
            "metadata": self.metadata,
            "source_epoch": self.source_epoch,
            "score_margin": round(self.score_margin, 4),
            "times_selected": self.times_selected,
        }


class NemesisArchive:
    def __init__(self, max_size: int) -> None:
        self.max_size = max(1, int(max_size))
        self._entries: list[ArchiveEntry] = []
        self._cursor = 0

    def record(self, entry: ArchiveEntry) -> bool:
        for existing in self._entries:
            if existing.label == entry.label and existing.code == entry.code:
                if entry.score_margin > existing.score_margin:
                    existing.score_margin = entry.score_margin
                    existing.source_epoch = entry.source_epoch
                return False
        self._entries.append(entry)
        self._entries.sort(key=lambda item: (item.score_margin, item.source_epoch, -item.times_selected), reverse=True)
        if len(self._entries) > self.max_size:
            self._entries = self._entries[: self.max_size]
        return True

    def select(self) -> ArchiveEntry | None:
        if not self._entries:
            return None
        entry = self._entries[self._cursor % len(self._entries)]
        self._cursor = (self._cursor + 1) % len(self._entries)
        entry.times_selected += 1
        return entry

    def hardest(self, limit: int) -> list[ArchiveEntry]:
        return list(self._entries[: max(0, int(limit))])

    def recent(self, limit: int) -> list[ArchiveEntry]:
        entries = sorted(self._entries, key=lambda item: item.source_epoch, reverse=True)
        return entries[: max(0, int(limit))]

    def to_list(self) -> list[dict[str, Any]]:
        return [entry.to_dict() for entry in self._entries]

    def __len__(self) -> int:
        return len(self._entries)


@dataclass
class ElitePolicyEntry:
    cell: str
    behavior_profile: str
    code: str
    descriptor: dict[str, float]
    fingerprint: str
    score: float
    source_epoch: int
    opponent_label: str
    selection_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "cell": self.cell,
            "behavior_profile": self.behavior_profile,
            "code": self.code,
            "descriptor": self.descriptor,
            "fingerprint": self.fingerprint,
            "score": round(self.score, 4),
            "source_epoch": self.source_epoch,
            "opponent_label": self.opponent_label,
            "selection_reason": self.selection_reason,
        }


class FocalEliteArchive:
    def __init__(self, max_size: int) -> None:
        self.max_size = max(1, int(max_size))
        self._entries_by_cell: dict[str, ElitePolicyEntry] = {}

    def cell_for(self, descriptor: dict[str, float] | None) -> str:
        return behavioral_cell(descriptor)

    def get(self, descriptor: dict[str, float] | None) -> ElitePolicyEntry | None:
        return self._entries_by_cell.get(self.cell_for(descriptor))

    def nearest_distance(self, descriptor: dict[str, float] | None) -> float:
        if not descriptor or not self._entries_by_cell:
            return 0.0
        return min(behavioral_distance(descriptor, entry.descriptor) for entry in self._entries_by_cell.values())

    def would_open_cell(self, descriptor: dict[str, float] | None) -> bool:
        return self.cell_for(descriptor) not in self._entries_by_cell

    def recent(self, limit: int) -> list[ElitePolicyEntry]:
        entries = sorted(self._entries_by_cell.values(), key=lambda item: item.source_epoch, reverse=True)
        return entries[: max(0, int(limit))]

    def coverage(self) -> int:
        return len(self._entries_by_cell)

    def record(self, entry: ElitePolicyEntry, *, score_tolerance: float) -> tuple[bool, str]:
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
        return sorted({entry.behavior_profile for entry in self._entries_by_cell.values()})

    def to_list(self) -> list[dict[str, Any]]:
        return [
            entry.to_dict()
            for entry in sorted(
                self._entries_by_cell.values(),
                key=lambda item: (item.behavior_profile, item.source_epoch, item.score),
            )
        ]

    def _trim(self) -> None:
        if len(self._entries_by_cell) <= self.max_size:
            return
        survivors = sorted(
            self._entries_by_cell.values(),
            key=lambda item: (item.score, item.source_epoch),
            reverse=True,
        )[: self.max_size]
        self._entries_by_cell = {entry.cell: entry for entry in survivors}

    def __len__(self) -> int:
        return len(self._entries_by_cell)

    def default_profile(self, descriptor: dict[str, float] | None) -> str:
        return behavioral_profile_label(descriptor)
