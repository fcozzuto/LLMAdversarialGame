from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any


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
        self._entries.sort(key=lambda item: (item.score_margin, -item.times_selected), reverse=True)
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

    def to_list(self) -> list[dict[str, Any]]:
        return [entry.to_dict() for entry in self._entries]

    def __len__(self) -> int:
        return len(self._entries)
