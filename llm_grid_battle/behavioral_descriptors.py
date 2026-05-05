from __future__ import annotations

from collections import Counter
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
    "revisit_ratio",
    "resource_pursuit_ratio",
    "opponent_pursuit_ratio",
    "opponent_avoidance_ratio",
    "resource_switch_ratio",
    "center_bias",
    "move_direction_entropy",
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


def _nearest_distance(position: tuple[int, int], points: list[tuple[int, int]]) -> float:
    if not points:
        return 0.0
    px, py = position
    return float(min(abs(px - tx) + abs(py - ty) for tx, ty in points))


def _center_bias(path: list[tuple[int, int]], width: int, height: int) -> float:
    if not path:
        return 0.0
    center_x = (width - 1) / 2.0
    center_y = (height - 1) / 2.0
    max_distance = max(1.0, abs(0 - center_x) + abs(0 - center_y))
    mean_distance = sum(abs(x - center_x) + abs(y - center_y) for x, y in path) / len(path)
    return round(max(0.0, 1.0 - (mean_distance / max_distance)), 4)


def _normalized_entropy(counter: Counter[tuple[int, int]]) -> float:
    total = sum(counter.values())
    if total <= 0 or len(counter) <= 1:
        return 0.0
    entropy = 0.0
    for count in counter.values():
        probability = count / total
        entropy -= probability * math.log(probability, 2)
    return round(entropy / math.log(len(counter), 2), 4)


def _bin_ratio(value: float, *, bins: int = 5) -> int:
    clipped = min(0.9999, max(0.0, float(value)))
    return min(bins - 1, max(0, int(clipped * bins)))


def compute_behavioral_descriptor(epoch: dict[str, Any], agent_name: str) -> dict[str, float]:
    turn_log = epoch.get("turn_log", [])
    turns = max(1, len(turn_log))
    width, height = _infer_map_dimensions(epoch)
    board_area = max(1, width * height)
    path = [tuple(point) for point in epoch.get("paths", {}).get(agent_name, [])]
    unique_cells = len(set(path))
    move_count = max(1, len(path) - 1)
    initial_resources = [tuple(point) for point in epoch.get("initial_resources", []) if len(point) == 2]

    stay_moves = 0
    diagonal_moves = 0
    exploration_moves = 0
    revisit_moves = 0
    resource_pursuit_moves = 0
    opponent_pursuit_moves = 0
    opponent_avoidance_moves = 0
    resource_target_switches = 0
    direction_counter: Counter[tuple[int, int]] = Counter()
    previous_nearest_resource: tuple[int, int] | None = None
    seen: set[tuple[int, int]] = set()
    for index in range(1, len(path)):
        previous = path[index - 1]
        current = path[index]
        dx = int(current[0] - previous[0])
        dy = int(current[1] - previous[1])
        direction_counter[(dx, dy)] += 1
        if dx == 0 and dy == 0:
            stay_moves += 1
        if dx != 0 and dy != 0:
            diagonal_moves += 1
        if current in seen:
            revisit_moves += 1
        else:
            exploration_moves += 1
        seen.add(previous)

        nearest_prev = _nearest_distance(previous, initial_resources)
        nearest_curr = _nearest_distance(current, initial_resources)
        if nearest_curr < nearest_prev:
            resource_pursuit_moves += 1

        if initial_resources:
            nearest_resource = min(initial_resources, key=lambda item: abs(item[0] - current[0]) + abs(item[1] - current[1]))
            if previous_nearest_resource is not None and nearest_resource != previous_nearest_resource:
                resource_target_switches += 1
            previous_nearest_resource = nearest_resource

    agent_names = list(epoch.get("paths", {}).keys())
    opponent_name = next((name for name in agent_names if name != agent_name), agent_name)
    opponent_path = [tuple(point) for point in epoch.get("paths", {}).get(opponent_name, [])]
    overlap_steps = 0
    distances: list[float] = []
    if path and opponent_path:
        max_steps = min(len(path), len(opponent_path))
        max_distance = max(1.0, float((width - 1) + (height - 1)))
        for index in range(1, max_steps):
            previous_distance = abs(path[index - 1][0] - opponent_path[index - 1][0]) + abs(path[index - 1][1] - opponent_path[index - 1][1])
            current_distance = abs(path[index][0] - opponent_path[index][0]) + abs(path[index][1] - opponent_path[index][1])
            if current_distance < previous_distance:
                opponent_pursuit_moves += 1
            elif current_distance > previous_distance:
                opponent_avoidance_moves += 1
        for index in range(max_steps):
            if path[index] == opponent_path[index]:
                overlap_steps += 1
            distances.append(
                (abs(path[index][0] - opponent_path[index][0]) + abs(path[index][1] - opponent_path[index][1]))
                / max_distance
            )

    issue_counts = _count_move_issues(turn_log, agent_name)
    score = float(epoch.get("scores", {}).get(agent_name, 0.0))
    descriptor = {
        "score_ratio": round(score / max(1, len(initial_resources)), 4),
        "stay_ratio": round(stay_moves / move_count, 4),
        "diagonal_ratio": round(diagonal_moves / move_count, 4),
        "unique_cell_ratio": round(unique_cells / board_area, 4),
        "path_overlap_ratio": round(overlap_steps / max(1, min(len(path), len(opponent_path))), 4),
        "boundary_hit_rate": round(issue_counts["boundary"] / turns, 4),
        "obstacle_hit_rate": round(issue_counts["obstacle"] / turns, 4),
        "invalid_move_rate": round(issue_counts["invalid"] / turns, 4),
        "mean_opponent_distance": round(sum(distances) / len(distances), 4) if distances else 0.0,
        "exploration_ratio": round(exploration_moves / move_count, 4),
        "revisit_ratio": round(revisit_moves / move_count, 4),
        "resource_pursuit_ratio": round(resource_pursuit_moves / move_count, 4),
        "opponent_pursuit_ratio": round(opponent_pursuit_moves / move_count, 4),
        "opponent_avoidance_ratio": round(opponent_avoidance_moves / move_count, 4),
        "resource_switch_ratio": round(resource_target_switches / move_count, 4),
        "center_bias": _center_bias(path, width, height),
        "move_direction_entropy": _normalized_entropy(direction_counter),
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
    if float(descriptor.get("opponent_pursuit_ratio", 0.0)) >= 0.45 and float(descriptor.get("mean_opponent_distance", 1.0)) <= 0.4:
        return "interceptor"
    if float(descriptor.get("opponent_avoidance_ratio", 0.0)) >= 0.4 and float(descriptor.get("mean_opponent_distance", 0.0)) >= 0.55:
        return "avoider"
    if float(descriptor.get("resource_switch_ratio", 0.0)) >= 0.35 and float(descriptor.get("exploration_ratio", 0.0)) >= 0.35:
        return "opportunistic_switcher"
    if float(descriptor.get("exploration_ratio", 0.0)) >= 0.45 and float(descriptor.get("revisit_ratio", 0.0)) <= 0.25:
        return "explorer"
    if float(descriptor.get("resource_pursuit_ratio", 0.0)) >= 0.45:
        return "collector"
    return "balanced"


def behavioral_cell(descriptor: dict[str, float] | None) -> str:
    if not descriptor:
        return "unknown:0:0:0:0"
    pressure_balance = (
        float(descriptor.get("opponent_pursuit_ratio", 0.0))
        - float(descriptor.get("opponent_avoidance_ratio", 0.0))
        + 1.0
    ) / 2.0
    return ":".join(
        [
            behavioral_profile_label(descriptor),
            str(_bin_ratio(float(descriptor.get("exploration_ratio", 0.0)))),
            str(_bin_ratio(float(descriptor.get("revisit_ratio", 0.0)))),
            str(_bin_ratio(pressure_balance)),
            str(_bin_ratio(float(descriptor.get("resource_switch_ratio", 0.0)))),
        ]
    )
