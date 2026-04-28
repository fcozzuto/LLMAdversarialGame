from __future__ import annotations

from dataclasses import dataclass, field
import copy
import json
from pathlib import Path
from typing import Any


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


@dataclass
class AgentConfig:
    name: str
    provider: str
    model: str
    system_prompt: str = "You write deterministic Python for a grid-game agent."
    temperature: float = 0.2
    max_tokens: int = 1200
    regenerate_each_epoch: bool = True


@dataclass
class FeedbackConfig:
    history_window: int = 1
    code_history_window: int = 1
    include_scores: bool = True
    include_paths: bool = True
    include_codes: bool = True
    include_opponent_code: bool = True
    include_grid_state: bool = True
    include_runtime_events: bool = True


@dataclass
class ObservationConfig:
    reveal_scores_each_turn: bool = True
    reveal_paths_each_turn: bool = False
    allow_stay: bool = True
    allow_diagonal: bool = True
    undocumented_fields_profile: str = "none"


@dataclass
class MapConfig:
    width: int = 10
    height: int = 10
    resource_count: int = 16
    obstacle_count: int = 0
    resample_each_epoch: bool = True


@dataclass
class GameConfig:
    epochs: int = 6
    max_turns: int = 120
    move_timeout_seconds: float = 0.25
    tie_break: str = "split"


@dataclass
class JudgeConfig:
    enabled: bool = True
    provider: str = "openai"
    model: str = "gpt-5-mini"
    temperature: float = 0.1
    max_tokens: int = 3000
    timeout_seconds: float = 300.0


@dataclass
class GenerationConfig:
    pre_execution_validation: bool = True
    repair_invalid_submissions: bool = True


@dataclass
class ConditionConfig:
    name: str
    seed: int
    output_root: str
    agents: list[AgentConfig]
    feedback: FeedbackConfig
    observation: ObservationConfig
    map: MapConfig
    game: GameConfig
    judge: JudgeConfig
    generation: GenerationConfig
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ConditionConfig":
        agents = [AgentConfig(**item) for item in data["agents"]]
        return ConditionConfig(
            name=data["name"],
            seed=int(data["seed"]),
            output_root=data.get("output_root", "runs"),
            agents=agents,
            feedback=FeedbackConfig(**data.get("feedback", {})),
            observation=ObservationConfig(**data.get("observation", {})),
            map=MapConfig(**data.get("map", {})),
            game=GameConfig(**data.get("game", {})),
            judge=JudgeConfig(**data.get("judge", {})),
            generation=GenerationConfig(**data.get("generation", {})),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "seed": self.seed,
            "output_root": self.output_root,
            "agents": [agent.__dict__ for agent in self.agents],
            "feedback": self.feedback.__dict__,
            "observation": self.observation.__dict__,
            "map": self.map.__dict__,
            "game": self.game.__dict__,
            "judge": self.judge.__dict__,
            "generation": self.generation.__dict__,
            "metadata": self.metadata,
        }


@dataclass
class SuiteConfig:
    defaults: dict[str, Any]
    conditions: list[ConditionConfig]

    @staticmethod
    def load(path: str | Path) -> "SuiteConfig":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        defaults = raw.get("defaults", {})
        conditions: list[ConditionConfig] = []
        for item in raw.get("conditions", []):
            merged = _deep_merge(defaults, item)
            if "name" not in merged:
                raise ValueError("Each condition requires a name.")
            if "seed" not in merged:
                raise ValueError(f"Condition {merged['name']} is missing a seed.")
            conditions.append(ConditionConfig.from_dict(merged))
        if not conditions:
            raise ValueError("The suite config did not contain any conditions.")
        return SuiteConfig(defaults=defaults, conditions=conditions)
