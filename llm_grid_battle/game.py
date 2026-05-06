from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random
from typing import Any

from .config import ConditionConfig


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


def initialize_environment(
    *,
    config: ConditionConfig,
    seed: int,
    agent_names: list[str],
) -> dict[str, Any]:
    map_state = build_map(
        width=config.map.width,
        height=config.map.height,
        resource_count=config.map.resource_count,
        obstacle_count=config.map.obstacle_count,
        seed=seed,
    )
    roles = _resolve_agent_roles(config, agent_names)
    return {
        "name": str(config.environment.name or "resource_collection").lower(),
        "map_state": map_state,
        "roles": roles,
        "territory_owner": {},
        "territory_bonus_scores": {name: 0.0 for name in agent_names},
        "capture_history": [],
    }


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
    max_turns: int,
    environment_state: dict[str, Any],
    self_name: str,
    opponent_name: str,
    positions: dict[str, Coord],
    paths: dict[str, list[Coord]],
    scores: dict[str, float],
    reveal_scores: bool,
    reveal_paths: bool,
    undocumented_fields_profile: str = "none",
) -> dict[str, Any]:
    map_state: MapState = environment_state["map_state"]
    observation = {
        "environment_name": environment_state["name"],
        "turn_index": turn_index,
        "turns_remaining": max(0, int(max_turns) - int(turn_index) - 1),
        "grid_width": map_state.width,
        "grid_height": map_state.height,
        "self_name": self_name,
        "opponent_name": opponent_name,
        "self_role": environment_state["roles"].get(self_name, "symmetric"),
        "opponent_role": environment_state["roles"].get(opponent_name, "symmetric"),
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
        _environment_observation_fields(
            environment_state=environment_state,
            self_name=self_name,
            opponent_name=opponent_name,
            positions=positions,
        )
    )
    observation.update(
        _undocumented_observation_fields(
            profile=undocumented_fields_profile,
            map_state=map_state,
            self_name=self_name,
            positions=positions,
        )
    )
    return observation


def resolve_environment_turn(
    *,
    config: ConditionConfig,
    environment_state: dict[str, Any],
    turn_index: int,
    previous_positions: dict[str, Coord],
    positions: dict[str, Coord],
    scores: dict[str, float],
    agent_names: list[str],
) -> dict[str, Any]:
    environment_name = str(environment_state["name"])
    if environment_name == "pursuit_evasion":
        return _resolve_pursuit_evasion_turn(
            config=config,
            environment_state=environment_state,
            turn_index=turn_index,
            previous_positions=previous_positions,
            positions=positions,
            scores=scores,
            agent_names=agent_names,
        )
    if environment_name == "territory_control":
        return _resolve_territory_control_turn(
            config=config,
            environment_state=environment_state,
            turn_index=turn_index,
            positions=positions,
            scores=scores,
            agent_names=agent_names,
        )
    return _resolve_resource_collection_turn(
        config=config,
        environment_state=environment_state,
        positions=positions,
        scores=scores,
        agent_names=agent_names,
    )


def finalize_environment_summary(
    *,
    config: ConditionConfig,
    environment_state: dict[str, Any],
    positions: dict[str, Coord],
    scores: dict[str, float],
) -> dict[str, Any]:
    environment_name = str(environment_state["name"])
    summary = {
        "name": environment_name,
        "roles": dict(environment_state.get("roles", {})),
    }
    if environment_name == "pursuit_evasion":
        capture_history = environment_state.get("capture_history", [])
        pursuer = next(
            (name for name, role in environment_state.get("roles", {}).items() if role == "pursuer"),
            "",
        )
        evader = next(
            (name for name, role in environment_state.get("roles", {}).items() if role == "evader"),
            "",
        )
        final_distance = (
            abs(positions[pursuer][0] - positions[evader][0]) + abs(positions[pursuer][1] - positions[evader][1])
            if pursuer and evader
            else 0
        )
        summary.update(
            {
                "capture_count": len(capture_history),
                "captures": capture_history,
                "final_distance": final_distance,
                "capture_radius": int(config.environment.capture_radius),
            }
        )
        return summary
    if environment_name == "territory_control":
        ownership = environment_state.get("territory_owner", {})
        counts = Counter(owner for owner in ownership.values() if owner)
        summary.update(
            {
                "territory_owner_counts": {name: int(counts.get(name, 0)) for name in positions},
                "territory_bonus_scores": {
                    name: float(environment_state.get("territory_bonus_scores", {}).get(name, 0.0))
                    for name in positions
                },
                "controlled_cells": [[cell[0], cell[1], owner] for cell, owner in sorted(ownership.items())],
                "final_scores": {name: float(scores.get(name, 0.0)) for name in positions},
            }
        )
        return summary
    map_state: MapState = environment_state["map_state"]
    summary["remaining_resource_count"] = len(map_state.resources)
    return summary


def _resolve_agent_roles(config: ConditionConfig, agent_names: list[str]) -> dict[str, str]:
    explicit = {str(key): str(value) for key, value in config.environment.role_assignments.items()}
    if explicit:
        return {name: explicit.get(name, "symmetric") for name in agent_names}
    if str(config.environment.name).lower() == "pursuit_evasion" and len(agent_names) >= 2:
        return {
            agent_names[0]: "pursuer",
            agent_names[1]: "evader",
        }
    return {name: "symmetric" for name in agent_names}


def _environment_observation_fields(
    *,
    environment_state: dict[str, Any],
    self_name: str,
    opponent_name: str,
    positions: dict[str, Coord],
) -> dict[str, Any]:
    environment_name = str(environment_state["name"])
    if environment_name == "pursuit_evasion":
        return {
            "capture_radius": int(environment_state.get("capture_radius", 0)),
            "capture_history_count": len(environment_state.get("capture_history", [])),
        }
    if environment_name == "territory_control":
        width = int(environment_state["map_state"].width)
        height = int(environment_state["map_state"].height)
        ownership: dict[Coord, str] = environment_state.get("territory_owner", {})
        self_territory = [list(cell) for cell, owner in sorted(ownership.items()) if owner == self_name]
        opponent_territory = [list(cell) for cell, owner in sorted(ownership.items()) if owner == opponent_name]
        unclaimed_cells = [
            [x, y]
            for y in range(height)
            for x in range(width)
            if (x, y) not in ownership and (x, y) not in positions.values()
        ]
        return {
            "self_territory": self_territory,
            "opponent_territory": opponent_territory,
            "self_territory_count": len(self_territory),
            "opponent_territory_count": len(opponent_territory),
            "unclaimed_cells": unclaimed_cells,
        }
    return {}


def _resolve_collection(
    *,
    positions: dict[str, Coord],
    resources: set[Coord],
    agent_names: list[str],
    tie_break: str,
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    score_delta = {name: 0.0 for name in agent_names}
    collections: list[dict[str, Any]] = []
    for resource in list(resources):
        claimants = [name for name in agent_names if positions[name] == resource]
        if not claimants:
            continue
        if len(claimants) == 1:
            winner = claimants[0]
            score_delta[winner] += 1.0
            resources.remove(resource)
            collections.append({"resource": list(resource), "winner": winner, "points": 1.0})
            continue
        if tie_break == "split":
            for name in claimants:
                score_delta[name] += 0.5
            resources.remove(resource)
            collections.append({"resource": list(resource), "winner": "split", "points": 0.5})
        elif tie_break == "agent_a":
            winner = claimants[0]
            score_delta[winner] += 1.0
            resources.remove(resource)
            collections.append({"resource": list(resource), "winner": winner, "points": 1.0})
        elif tie_break == "agent_b":
            winner = claimants[-1]
            score_delta[winner] += 1.0
            resources.remove(resource)
            collections.append({"resource": list(resource), "winner": winner, "points": 1.0})
        else:
            resources.remove(resource)
            collections.append({"resource": list(resource), "winner": "contested_removed", "points": 0.0})
    return score_delta, collections


def _resolve_resource_collection_turn(
    *,
    config: ConditionConfig,
    environment_state: dict[str, Any],
    positions: dict[str, Coord],
    scores: dict[str, float],
    agent_names: list[str],
) -> dict[str, Any]:
    map_state: MapState = environment_state["map_state"]
    score_delta, collections = _resolve_collection(
        positions=positions,
        resources=map_state.resources,
        agent_names=agent_names,
        tie_break=config.game.tie_break,
    )
    next_scores = {name: float(scores.get(name, 0.0)) + float(score_delta[name]) for name in agent_names}
    return {
        "scores": next_scores,
        "done": not map_state.resources,
        "collections": collections,
        "environment_events": [{"type": "collection", **item} for item in collections],
    }


def _resolve_pursuit_evasion_turn(
    *,
    config: ConditionConfig,
    environment_state: dict[str, Any],
    turn_index: int,
    previous_positions: dict[str, Coord],
    positions: dict[str, Coord],
    scores: dict[str, float],
    agent_names: list[str],
) -> dict[str, Any]:
    roles = environment_state.get("roles", {})
    pursuer = next((name for name in agent_names if roles.get(name) == "pursuer"), agent_names[0])
    evader = next((name for name in agent_names if name != pursuer), agent_names[-1])
    capture_radius = max(0, int(config.environment.capture_radius))
    next_scores = {name: float(scores.get(name, 0.0)) for name in agent_names}
    environment_events: list[dict[str, Any]] = []

    current_distance = abs(positions[pursuer][0] - positions[evader][0]) + abs(positions[pursuer][1] - positions[evader][1])
    crossed_paths = (
        previous_positions[pursuer] == positions[evader]
        and previous_positions[evader] == positions[pursuer]
    )
    captured = current_distance <= capture_radius or crossed_paths
    if captured:
        next_scores[pursuer] += float(config.environment.capture_points)
        capture_event = {
            "type": "capture",
            "turn_index": int(turn_index),
            "pursuer": pursuer,
            "evader": evader,
            "distance": int(current_distance),
            "crossed_paths": bool(crossed_paths),
        }
        environment_state["capture_history"].append(capture_event)
        environment_events.append(capture_event)
    else:
        next_scores[evader] += float(config.environment.survival_points_per_turn)
        environment_events.append(
            {
                "type": "survival_tick",
                "turn_index": int(turn_index),
                "evader": evader,
                "points": float(config.environment.survival_points_per_turn),
                "distance": int(current_distance),
            }
        )

    return {
        "scores": next_scores,
        "done": bool(captured and config.environment.capture_ends_game),
        "collections": [],
        "environment_events": environment_events,
    }


def _resolve_territory_control_turn(
    *,
    config: ConditionConfig,
    environment_state: dict[str, Any],
    turn_index: int,
    positions: dict[str, Coord],
    scores: dict[str, float],
    agent_names: list[str],
) -> dict[str, Any]:
    ownership: dict[Coord, str] = environment_state.setdefault("territory_owner", {})
    bonus_bank: dict[str, float] = environment_state.setdefault(
        "territory_bonus_scores",
        {name: 0.0 for name in agent_names},
    )
    environment_events: list[dict[str, Any]] = []
    cell_claimants: dict[Coord, list[str]] = {}
    for name, cell in positions.items():
        cell_claimants.setdefault(cell, []).append(name)

    for cell, claimants in sorted(cell_claimants.items()):
        if len(claimants) != 1:
            environment_events.append(
                {
                    "type": "territory_contested",
                    "turn_index": int(turn_index),
                    "cell": [cell[0], cell[1]],
                    "claimants": list(claimants),
                }
            )
            continue
        owner = claimants[0]
        previous_owner = ownership.get(cell)
        if previous_owner == owner:
            continue
        if previous_owner is None or bool(config.environment.territory_flip_on_entry):
            ownership[cell] = owner
            environment_events.append(
                {
                    "type": "territory_claim",
                    "turn_index": int(turn_index),
                    "cell": [cell[0], cell[1]],
                    "owner": owner,
                    "previous_owner": previous_owner,
                }
            )

    counts = Counter(owner for owner in ownership.values() if owner)
    if (
        int(config.environment.territory_control_bonus_interval) > 0
        and (turn_index + 1) % int(config.environment.territory_control_bonus_interval) == 0
    ):
        max_cells = max(counts.values(), default=0)
        leaders = [name for name in agent_names if counts.get(name, 0) == max_cells and max_cells > 0]
        if len(leaders) == 1:
            leader = leaders[0]
            bonus_bank[leader] = float(bonus_bank.get(leader, 0.0)) + float(config.environment.territory_control_bonus)
            environment_events.append(
                {
                    "type": "territory_control_bonus",
                    "turn_index": int(turn_index),
                    "leader": leader,
                    "points": float(config.environment.territory_control_bonus),
                    "controlled_cells": int(max_cells),
                }
            )

    next_scores = {
        name: float(counts.get(name, 0)) + float(bonus_bank.get(name, 0.0))
        for name in agent_names
    }
    return {
        "scores": next_scores,
        "done": False,
        "collections": [],
        "environment_events": environment_events,
    }
