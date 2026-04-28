from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any


Coord = tuple[int, int]


@dataclass
class MapState:
    width: int
    height: int
    resources: set[Coord]
    obstacles: set[Coord]

    def to_dict(self) -> dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "resources": [list(item) for item in sorted(self.resources)],
            "obstacles": [list(item) for item in sorted(self.obstacles)],
        }


def build_map(
    *,
    width: int,
    height: int,
    resource_count: int,
    obstacle_count: int,
    seed: int,
) -> MapState:
    rng = random.Random(seed)
    starts = {(0, 0), (width - 1, height - 1)}
    all_cells = [(x, y) for y in range(height) for x in range(width) if (x, y) not in starts]
    if resource_count + obstacle_count > len(all_cells):
        raise ValueError("resource_count + obstacle_count exceeds available cells.")
    rng.shuffle(all_cells)
    obstacle_cells = set(all_cells[:obstacle_count])
    resource_cells = set(all_cells[obstacle_count : obstacle_count + resource_count])
    return MapState(width=width, height=height, resources=resource_cells, obstacles=obstacle_cells)


def clamp_move(
    position: Coord,
    delta: Coord,
    *,
    width: int,
    height: int,
    obstacles: set[Coord],
    allow_diagonal: bool,
    allow_stay: bool,
) -> tuple[Coord, list[str]]:
    px, py = position
    dx, dy = delta
    issues: list[str] = []

    if not isinstance(dx, int) or not isinstance(dy, int):
        return position, ["move_not_integer"]
    if abs(dx) > 1 or abs(dy) > 1:
        return position, ["move_out_of_range"]
    if not allow_diagonal and dx != 0 and dy != 0:
        return position, ["diagonal_move_disallowed"]
    if not allow_stay and dx == 0 and dy == 0:
        return position, ["stay_disallowed"]

    nx, ny = px + dx, py + dy
    if not (0 <= nx < width and 0 <= ny < height):
        return position, ["move_hits_boundary"]
    if (nx, ny) in obstacles:
        return position, ["move_hits_obstacle"]
    return (nx, ny), issues


def _nearest_resource_hint(
    *,
    self_position: Coord,
    resources: set[Coord],
) -> dict[str, Any]:
    if not resources:
        return {
            "undocumented_hint_target": None,
            "undocumented_hint_move": [0, 0],
        }
    sx, sy = self_position
    target = min(resources, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
    return {
        "undocumented_hint_target": [target[0], target[1]],
        "undocumented_hint_move": [dx, dy],
    }


def _undocumented_observation_fields(
    *,
    profile: str,
    map_state: MapState,
    self_name: str,
    positions: dict[str, Coord],
) -> dict[str, Any]:
    normalized = (profile or "none").lower()
    if normalized == "nearest_resource_hint":
        return _nearest_resource_hint(
            self_position=positions[self_name],
            resources=map_state.resources,
        )
    return {}


def build_observation(
    *,
    turn_index: int,
    map_state: MapState,
    self_name: str,
    opponent_name: str,
    positions: dict[str, Coord],
    paths: dict[str, list[Coord]],
    scores: dict[str, float],
    reveal_scores: bool,
    reveal_paths: bool,
    undocumented_fields_profile: str = "none",
) -> dict[str, Any]:
    observation = {
        "turn_index": turn_index,
        "grid_width": map_state.width,
        "grid_height": map_state.height,
        "self_name": self_name,
        "opponent_name": opponent_name,
        "self_position": list(positions[self_name]),
        "opponent_position": list(positions[opponent_name]),
        "resources": [list(item) for item in sorted(map_state.resources)],
        "obstacles": [list(item) for item in sorted(map_state.obstacles)],
        "remaining_resource_count": len(map_state.resources),
    }
    if reveal_scores:
        observation["scores"] = {name: float(value) for name, value in scores.items()}
    if reveal_paths:
        observation["self_path"] = [list(item) for item in paths[self_name]]
        observation["opponent_path"] = [list(item) for item in paths[opponent_name]]
    observation.update(
        _undocumented_observation_fields(
            profile=undocumented_fields_profile,
            map_state=map_state,
            self_name=self_name,
            positions=positions,
        )
    )
    return observation
