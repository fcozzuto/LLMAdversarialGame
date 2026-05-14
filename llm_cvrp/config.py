from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
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
    system_prompt: str = "You design deterministic Python heuristic configurations for a constrained CVRP scaffold."
    temperature: float = 0.2
    max_tokens: int = 1600
    regenerate_each_epoch: bool = True


@dataclass
class GenerationConfig:
    repair_invalid_submissions: bool = True


@dataclass
class ReplayPolicyConfig:
    mode: str = "none"
    archive_max_size: int = 12
    replay_instance_count: int = 0
    catastrophic_gap_threshold: float = 0.08


@dataclass
class SelectionPolicyConfig:
    mode: str = "score_only"
    novelty_threshold: float = 0.06
    score_tolerance: float = 0.0025
    replay_gap_tolerance: float = 0.004
    transfer_gap_tolerance: float = 0.006
    elite_archive_enabled: bool = True
    elite_archive_max_size: int = 12
    elite_distance_threshold: float = 0.08
    elite_score_tolerance: float = 0.003
    compression_pressure: bool = False
    max_complexity_increase: float = 0.35


@dataclass
class BenchmarkConfig:
    manifest_path: str
    curriculum_batch_size: int = 4
    transfer_probe_count: int = 4
    adversarial_probe_count: int = 3


@dataclass
class OptimizationConfig:
    epochs: int = 10


@dataclass
class JudgeConfig:
    enabled: bool = True
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    temperature: float = 0.1
    max_tokens: int = 3000
    timeout_seconds: float = 300.0


@dataclass
class CVRPConditionConfig:
    name: str
    seed: int
    output_root: str
    agent: AgentConfig
    generation: GenerationConfig
    replay: ReplayPolicyConfig
    selection: SelectionPolicyConfig
    benchmark: BenchmarkConfig
    optimization: OptimizationConfig
    judge: JudgeConfig
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "CVRPConditionConfig":
        return CVRPConditionConfig(
            name=data["name"],
            seed=int(data["seed"]),
            output_root=data.get("output_root", "runs/cvrp_suite"),
            agent=AgentConfig(**data["agent"]),
            generation=GenerationConfig(**data.get("generation", {})),
            replay=ReplayPolicyConfig(**data.get("replay", {})),
            selection=SelectionPolicyConfig(**data.get("selection", {})),
            benchmark=BenchmarkConfig(**data["benchmark"]),
            optimization=OptimizationConfig(**data.get("optimization", {})),
            judge=JudgeConfig(**data.get("judge", {})),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "seed": self.seed,
            "output_root": self.output_root,
            "agent": self.agent.__dict__,
            "generation": self.generation.__dict__,
            "replay": self.replay.__dict__,
            "selection": self.selection.__dict__,
            "benchmark": self.benchmark.__dict__,
            "optimization": self.optimization.__dict__,
            "judge": self.judge.__dict__,
            "metadata": dict(self.metadata),
        }


@dataclass
class CVRPSuiteConfig:
    defaults: dict[str, Any]
    conditions: list[CVRPConditionConfig]

    @staticmethod
    def load(path: str | Path) -> "CVRPSuiteConfig":
        raw = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        defaults = raw.get("defaults", {})
        conditions: list[CVRPConditionConfig] = []
        for item in raw.get("conditions", []):
            merged = _deep_merge(defaults, item)
            conditions.append(CVRPConditionConfig.from_dict(merged))
        if not conditions:
            raise ValueError("The CVRP suite config did not contain any conditions.")
        return CVRPSuiteConfig(defaults=defaults, conditions=conditions)
