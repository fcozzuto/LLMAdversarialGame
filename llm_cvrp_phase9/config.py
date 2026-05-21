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
class ExecutionConfig:
    mode: str = "solver_evolution"


@dataclass
class AgentConfig:
    name: str
    provider: str
    model: str
    system_prompt: str = (
        "You design deterministic CVRP solvers that build feasible routes and improve them "
        "with interpretable heuristic logic."
    )
    temperature: float = 0.2
    max_tokens: int = 3600
    regenerate_each_epoch: bool = True


@dataclass
class GenerationConfig:
    repair_invalid_submissions: bool = True
    llm_timeout_seconds: float = 120.0
    solver_timeout_seconds: float = 180.0
    max_non_empty_lines: int = 260
    max_characters: int = 12000


@dataclass
class BenchmarkConfig:
    manifest_path: str
    train_instance_limit: int = 0
    holdout_instance_limit: int = 0
    enforce_vehicle_count: bool = False
    infeasible_gap_penalty: float = 2.0


@dataclass
class OptimizationConfig:
    epochs: int = 8
    acceptance_tolerance: float = 0.0


@dataclass
class JudgeConfig:
    enabled: bool = True
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    temperature: float = 0.1
    max_tokens: int = 3200
    timeout_seconds: float = 300.0


@dataclass
class Phase9ConditionConfig:
    name: str
    seed: int
    output_root: str
    execution: ExecutionConfig
    agent: AgentConfig
    generation: GenerationConfig
    benchmark: BenchmarkConfig
    optimization: OptimizationConfig
    judge: JudgeConfig
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Phase9ConditionConfig":
        generation_data = dict(data.get("generation", {}))
        legacy_timeout = generation_data.pop("timeout_seconds", None)
        if legacy_timeout is not None:
            generation_data.setdefault("llm_timeout_seconds", legacy_timeout)
            generation_data.setdefault("solver_timeout_seconds", legacy_timeout)
        return Phase9ConditionConfig(
            name=str(data["name"]),
            seed=int(data["seed"]),
            output_root=str(data.get("output_root", "runs/cvrp_phase9_suite")),
            execution=ExecutionConfig(**data.get("execution", {})),
            agent=AgentConfig(**data["agent"]),
            generation=GenerationConfig(**generation_data),
            benchmark=BenchmarkConfig(**data["benchmark"]),
            optimization=OptimizationConfig(**data.get("optimization", {})),
            judge=JudgeConfig(**data.get("judge", {})),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class Phase9SuiteConfig:
    defaults: dict[str, Any]
    conditions: list[Phase9ConditionConfig]

    @staticmethod
    def load(path: str | Path) -> "Phase9SuiteConfig":
        raw = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        defaults = raw.get("defaults", {})
        conditions: list[Phase9ConditionConfig] = []
        for item in raw.get("conditions", []):
            merged = _deep_merge(defaults, item)
            conditions.append(Phase9ConditionConfig.from_dict(merged))
        if not conditions:
            raise ValueError("The phase-9 suite config did not contain any conditions.")
        return Phase9SuiteConfig(defaults=defaults, conditions=conditions)
