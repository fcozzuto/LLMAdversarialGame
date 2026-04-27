from __future__ import annotations

import json
from typing import Any

from .config import ConditionConfig
from .code_validation import TARGET_CHARACTERS, TARGET_NON_EMPTY_LINES


def truncate_text(text: str, limit: int = 1400) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]..."


def _format_delta(value: float) -> str:
    rounded = round(value, 3)
    return f"{rounded:+.3f}"


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
        "Return only raw Python source code.",
        "The first line must be exactly: def choose_move(observation):",
        "Do not use markdown fences.",
        "Do not include any explanation before or after the function.",
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
        "- Keep the solution self-contained inside choose_move(observation) using only local deterministic logic derived from the observation.",
        "- Do not write import statements of any kind.",
        "- Do not use names beginning with __.",
        "- Do not depend on external files, external services, subprocesses, or hidden state.",
        "- Every control path must end by returning [dx, dy] with integer dx and dy in {-1, 0, 1}.",
        "- Do not leave placeholder logic, unfinished branches, or helper code without a final return path.",
        "- Return exactly one top-level function named choose_move.",
        "- Prefer concise heuristics over large helper stacks or full-grid search if brevity is at risk.",
        f"- Use at most {TARGET_NON_EMPTY_LINES} non-empty lines.",
        f"- Keep the function under {TARGET_CHARACTERS} characters.",
        "- If you cannot fit, simplify the strategy instead of adding more code.",
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
        "- Favor clear deterministic logic over brittle shortcuts.",
        "- If recent feedback does not show improvement or a decisive win, make a meaningful strategic change instead of repeating the same policy with cosmetic edits.",
        "- Keep innovating until you are winning decisively and consistently, then preserve the strong core and only refine obvious weaknesses.",
        "",
        f"Epoch: {epoch_index}",
    ]

    if history:
        latest = history[-1]
        latest_score = float(latest["scores"][agent_name])
        latest_opponent_score = float(latest["scores"][opponent_name])
        parts.extend(
            [
                "",
                "Recent performance signal:",
                f"- Most recent score margin: {_format_delta(latest_score - latest_opponent_score)}",
            ]
        )
        if len(history) >= 2:
            previous = history[-2]
            previous_score = float(previous["scores"][agent_name])
            score_delta = latest_score - previous_score
            parts.append(f"- Your score change vs previous epoch: {_format_delta(score_delta)}")
            if score_delta <= 0:
                parts.append(
                    "- Adaptation note: your score did not improve last epoch, so do not reuse the same policy unless you can justify a real strategic advantage."
                )
        if latest_score <= latest_opponent_score:
            parts.append(
                "- Adaptation note: you were not ahead last epoch, so prefer a materially different targeting, obstacle-handling, or opponent-response strategy."
            )

        feedback_items = history[-config.feedback.history_window :]
        if config.feedback.include_codes and len(feedback_items) > 1:
            # Code-bearing prompts are the largest and have shown truncation risk, so only
            # include the latest epoch when prior code is embedded.
            feedback_items = feedback_items[-1:]

        parts.append("")
        parts.append("Previous epoch feedback:")
        for item in feedback_items:
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
                parts.append(
                    f"- {agent_name} code:\nBEGIN_PREVIOUS_CODE\n{truncate_text(item['codes'][agent_name])}\nEND_PREVIOUS_CODE"
                )
                if config.feedback.include_opponent_code:
                    parts.append(
                        f"- {opponent_name} code:\nBEGIN_PREVIOUS_CODE\n{truncate_text(item['codes'][opponent_name])}\nEND_PREVIOUS_CODE"
                    )

    parts.append("")
    parts.append("Output only raw Python source code.")
    return "\n".join(parts)
