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
class OpponentSpec:
    label: str = ""
    library_key: str = ""
    provider: str = ""
    model: str = ""
    system_prompt: str = ""
    temperature: float = 0.0
    max_tokens: int = 0
    regenerate_each_epoch: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


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
    model: str = "gpt-4.1-mini"
    temperature: float = 0.1
    max_tokens: int = 3000
    timeout_seconds: float = 300.0


@dataclass
class GenerationConfig:
    pre_execution_validation: bool = True
    repair_invalid_submissions: bool = True


@dataclass
class ArchivePolicyConfig:
    enabled: bool = False
    reintroduce_every: int = 0
    min_score_margin: float = 1.0
    max_size: int = 8


@dataclass
class PressurePolicyConfig:
    enabled: bool = False
    loss_streak_trigger: int = 2
    score_margin_trigger: float = 1.5
    stagnation_epoch_trigger: int = 3
    cooldown_epochs: int = 1
    require_substantial_change: bool = True
    custom_instruction: str = (
        "Your last approach failed. Propose a substantially different algorithmic strategy."
    )


@dataclass
class SelectionPolicyConfig:
    mode: str = "accept_all"
    novelty_metric: str = "behavioral_distance"
    novelty_threshold: float = 0.2
    score_tolerance: float = 0.5
    replay_opponent_count: int = 0
    replay_games_per_opponent: int = 1
    replay_score_tolerance: float = 0.5
    holdout_opponent_count: int = 0
    holdout_games_per_opponent: int = 1
    holdout_score_tolerance: float = 0.75
    elite_archive_enabled: bool = False
    elite_archive_max_size: int = 12
    elite_distance_threshold: float = 0.18
    elite_score_tolerance: float = 0.5


@dataclass
class EvaluationConfig:
    enabled: bool = False
    games_per_opponent: int = 5
    holdout_opponents: list[OpponentSpec] = field(default_factory=list)


@dataclass
class CurriculumConfig:
    enabled: bool = False
    focal_agent: str = ""
    opponent_agent: str = ""
    mode: str = "none"
    opponent_pool: list[OpponentSpec] = field(default_factory=list)
    rotation_policy: str = "cyclic"
    rotation_stride: int = 1
    archive: ArchivePolicyConfig = field(default_factory=ArchivePolicyConfig)
    pressure: PressurePolicyConfig = field(default_factory=PressurePolicyConfig)
    selection: SelectionPolicyConfig = field(default_factory=SelectionPolicyConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)


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
    curriculum: CurriculumConfig
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ConditionConfig":
        agents = [AgentConfig(**item) for item in data["agents"]]
        curriculum_raw = data.get("curriculum", {})
        evaluation_raw = curriculum_raw.get("evaluation", {})
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
            curriculum=CurriculumConfig(
                enabled=bool(curriculum_raw.get("enabled", False)),
                focal_agent=str(curriculum_raw.get("focal_agent", "")),
                opponent_agent=str(curriculum_raw.get("opponent_agent", "")),
                mode=str(curriculum_raw.get("mode", "none")),
                opponent_pool=[OpponentSpec(**item) for item in curriculum_raw.get("opponent_pool", [])],
                rotation_policy=str(curriculum_raw.get("rotation_policy", "cyclic")),
                rotation_stride=int(curriculum_raw.get("rotation_stride", 1)),
                archive=ArchivePolicyConfig(**curriculum_raw.get("archive", {})),
                pressure=PressurePolicyConfig(**curriculum_raw.get("pressure", {})),
                selection=SelectionPolicyConfig(**curriculum_raw.get("selection", {})),
                evaluation=EvaluationConfig(
                    enabled=bool(evaluation_raw.get("enabled", False)),
                    games_per_opponent=int(evaluation_raw.get("games_per_opponent", 3)),
                    holdout_opponents=[OpponentSpec(**item) for item in evaluation_raw.get("holdout_opponents", [])],
                ),
            ),
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
            "curriculum": {
                "enabled": self.curriculum.enabled,
                "focal_agent": self.curriculum.focal_agent,
                "opponent_agent": self.curriculum.opponent_agent,
                "mode": self.curriculum.mode,
                "opponent_pool": [opponent.__dict__ for opponent in self.curriculum.opponent_pool],
                "rotation_policy": self.curriculum.rotation_policy,
                "rotation_stride": self.curriculum.rotation_stride,
                "archive": self.curriculum.archive.__dict__,
                "pressure": self.curriculum.pressure.__dict__,
                "selection": self.curriculum.selection.__dict__,
                "evaluation": {
                    "enabled": self.curriculum.evaluation.enabled,
                    "games_per_opponent": self.curriculum.evaluation.games_per_opponent,
                    "holdout_opponents": [
                        opponent.__dict__ for opponent in self.curriculum.evaluation.holdout_opponents
                    ],
                },
            },
            "metadata": self.metadata,
        }


@dataclass
class SuiteConfig:
    defaults: dict[str, Any]
    conditions: list[ConditionConfig]

    @staticmethod
    def load(path: str | Path) -> "SuiteConfig":
        raw = json.loads(Path(path).read_text(encoding="utf-8-sig"))
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
