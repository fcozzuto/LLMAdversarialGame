from __future__ import annotations

import math
from typing import Any


DESCRIPTOR_KEYS = (
    "score_ratio",
    "stay_ratio",
    "diagonal_ratio",
    "unique_cell_ratio",
    "path_overlap_ratio",
    "boundary_hit_rate",
    "obstacle_hit_rate",
    "invalid_move_rate",
    "mean_opponent_distance",
    "exploration_ratio",
)


def _infer_map_dimensions(epoch: dict[str, Any]) -> tuple[int, int]:
    dimensions = epoch.get("map_dimensions", {})
    width = int(dimensions.get("width", 0))
    height = int(dimensions.get("height", 0))
    if width > 0 and height > 0:
        return width, height

    max_x = 0
    max_y = 0
    for point in epoch.get("initial_resources", []) + epoch.get("obstacles", []):
        if len(point) == 2:
            max_x = max(max_x, int(point[0]))
            max_y = max(max_y, int(point[1]))
    for path in epoch.get("paths", {}).values():
        for point in path:
            if len(point) == 2:
                max_x = max(max_x, int(point[0]))
                max_y = max(max_y, int(point[1]))
    return max_x + 1, max_y + 1


def _count_move_issues(turn_log: list[dict[str, Any]], agent_name: str) -> dict[str, int]:
    counts = {
        "boundary": 0,
        "obstacle": 0,
        "invalid": 0,
    }
    for turn in turn_log:
        issues = turn.get("move_issues", {}).get(agent_name, [])
        for issue in issues:
            if issue == "move_hits_boundary":
                counts["boundary"] += 1
            elif issue == "move_hits_obstacle":
                counts["obstacle"] += 1
            else:
                counts["invalid"] += 1
    return counts


def compute_behavioral_descriptor(epoch: dict[str, Any], agent_name: str) -> dict[str, float]:
    turn_log = epoch.get("turn_log", [])
    turns = max(1, len(turn_log))
    width, height = _infer_map_dimensions(epoch)
    board_area = max(1, width * height)
    path = [tuple(point) for point in epoch.get("paths", {}).get(agent_name, [])]
    unique_cells = len(set(path))
    move_count = max(1, len(path) - 1)
    stay_moves = 0
    diagonal_moves = 0
    exploration_moves = 0
    for index in range(1, len(path)):
        dx = int(path[index][0] - path[index - 1][0])
        dy = int(path[index][1] - path[index - 1][1])
        if dx == 0 and dy == 0:
            stay_moves += 1
        if dx != 0 and dy != 0:
            diagonal_moves += 1
        if path[index] not in set(path[:index]):
            exploration_moves += 1

    agent_names = list(epoch.get("paths", {}).keys())
    opponent_name = next((name for name in agent_names if name != agent_name), agent_name)
    opponent_path = [tuple(point) for point in epoch.get("paths", {}).get(opponent_name, [])]
    overlap_steps = 0
    distances: list[float] = []
    if path and opponent_path:
        max_steps = min(len(path), len(opponent_path))
        max_distance = max(1.0, float((width - 1) + (height - 1)))
        for index in range(max_steps):
            if path[index] == opponent_path[index]:
                overlap_steps += 1
            distances.append(
                (abs(path[index][0] - opponent_path[index][0]) + abs(path[index][1] - opponent_path[index][1]))
                / max_distance
            )

    issue_counts = _count_move_issues(turn_log, agent_name)
    initial_resources = max(1, len(epoch.get("initial_resources", [])))
    score = float(epoch.get("scores", {}).get(agent_name, 0.0))
    descriptor = {
        "score_ratio": round(score / initial_resources, 4),
        "stay_ratio": round(stay_moves / move_count, 4),
        "diagonal_ratio": round(diagonal_moves / move_count, 4),
        "unique_cell_ratio": round(unique_cells / board_area, 4),
        "path_overlap_ratio": round(overlap_steps / max(1, min(len(path), len(opponent_path))), 4),
        "boundary_hit_rate": round(issue_counts["boundary"] / turns, 4),
        "obstacle_hit_rate": round(issue_counts["obstacle"] / turns, 4),
        "invalid_move_rate": round(issue_counts["invalid"] / turns, 4),
        "mean_opponent_distance": round(sum(distances) / len(distances), 4) if distances else 0.0,
        "exploration_ratio": round(exploration_moves / move_count, 4),
    }
    return descriptor


def behavioral_distance(left: dict[str, float] | None, right: dict[str, float] | None) -> float:
    if not left or not right:
        return 0.0
    squared = 0.0
    for key in DESCRIPTOR_KEYS:
        squared += (float(left.get(key, 0.0)) - float(right.get(key, 0.0))) ** 2
    return round(math.sqrt(squared / len(DESCRIPTOR_KEYS)), 4)


def behavioral_profile_label(descriptor: dict[str, float] | None) -> str:
    if not descriptor:
        return "unknown"
    if float(descriptor.get("stay_ratio", 0.0)) >= 0.35:
        return "static_guard"
    if float(descriptor.get("path_overlap_ratio", 0.0)) >= 0.15 and float(descriptor.get("mean_opponent_distance", 1.0)) <= 0.35:
        return "opponent_contester"
    if float(descriptor.get("exploration_ratio", 0.0)) >= 0.4 and float(descriptor.get("unique_cell_ratio", 0.0)) >= 0.2:
        return "explorer"
    return "resource_collector"
