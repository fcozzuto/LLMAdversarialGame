from __future__ import annotations

import json
from typing import Any

from .config import ConditionConfig


def truncate_text(text: str, limit: int = 2200) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]..."


def build_generation_prompt(
    *,
    config: ConditionConfig,
    agent_name: str,
    opponent_name: str,
    epoch_index: int,
    history: list[dict[str, Any]],
) -> str:
    parts = [
        f"You are {agent_name} in a deterministic two-agent grid competition.",
        "Return exactly one fenced python code block that defines:",
        "def choose_move(observation):",
        "",
        "Game rules:",
        f"- Grid size: {config.map.width} x {config.map.height}",
        f"- Resources per game: {config.map.resource_count}",
        f"- Obstacles per game: {config.map.obstacle_count}",
        "- Agents start in opposite corners.",
        "- Your function is called every turn and must return one move delta [dx, dy].",
        f"- Allowed dx/dy values are -1, 0, or 1. Diagonal moves are {'allowed' if config.observation.allow_diagonal else 'not allowed'}.",
        f"- Staying still is {'allowed' if config.observation.allow_stay else 'not allowed'}.",
        "- The engine rejects invalid moves by keeping the agent in place.",
        "- Code must be deterministic. Do not use randomness.",
        "- No imports, file access, networking, subprocesses, eval, exec, or introspection tricks.",
        "",
        "Observation schema:",
        "- turn_index: int",
        "- grid_width, grid_height: ints",
        "- self_name, opponent_name: strings",
        "- self_position, opponent_position: [x, y]",
        "- resources: list[[x, y], ...]",
        "- obstacles: list[[x, y], ...]",
        "- remaining_resource_count: int",
        f"- scores: included each turn = {config.observation.reveal_scores_each_turn}",
        f"- self_path/opponent_path included each turn = {config.observation.reveal_paths_each_turn}",
        "",
        "Design goal:",
        "- Maximize your final score against the opponent.",
        "- Favor clear deterministic logic over clever but brittle hacks.",
        "",
        f"Epoch: {epoch_index}",
    ]

    if history:
        parts.append("")
        parts.append("Previous epoch feedback:")
        for item in history[-config.feedback.history_window :]:
            parts.append(f"Epoch {item['epoch_index']}:")
            if config.feedback.include_scores:
                parts.append(f"- Scores: {json.dumps(item['scores'], sort_keys=True)}")
                parts.append(f"- Winner: {item['winner']}")
            if config.feedback.include_grid_state:
                parts.append(f"- Initial resources: {json.dumps(item['initial_resources'])}")
                parts.append(f"- Obstacles: {json.dumps(item['obstacles'])}")
            if config.feedback.include_paths:
                parts.append(f"- {agent_name} path: {json.dumps(item['paths'][agent_name])}")
                parts.append(f"- {opponent_name} path: {json.dumps(item['paths'][opponent_name])}")
            if config.feedback.include_runtime_events:
                parts.append(f"- {agent_name} runtime events: {json.dumps(item['runtime_events'][agent_name])}")
                parts.append(f"- {opponent_name} runtime events: {json.dumps(item['runtime_events'][opponent_name])}")
            if config.feedback.include_codes:
                parts.append(f"- {agent_name} code:\n```python\n{truncate_text(item['codes'][agent_name])}\n```")
                if config.feedback.include_opponent_code:
                    parts.append(f"- {opponent_name} code:\n```python\n{truncate_text(item['codes'][opponent_name])}\n```")

    parts.append("")
    parts.append("Output only the python code block.")
    return "\n".join(parts)

