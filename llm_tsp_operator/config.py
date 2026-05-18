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
    mode: str = "modular_operator"


@dataclass
class AgentConfig:
    name: str
    provider: str
    model: str
    system_prompt: str = "You design one deterministic reusable TSP operator at a time for a constrained modular scaffold."
    temperature: float = 0.2
    max_tokens: int = 1800
    regenerate_each_epoch: bool = True


@dataclass
class GenerationConfig:
    repair_invalid_submissions: bool = True


@dataclass
class ReplayPolicyConfig:
    mode: str = "none"
    archive_max_size: int = 12
    experience_archive_max_size: int = 24
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
    pareto_gap_tolerance: float = 0.001
    pareto_runtime_tolerance: float = 0.05
    pareto_complexity_tolerance: float = 0.15


@dataclass
class BenchmarkConfig:
    manifest_path: str
    curriculum_batch_size: int = 4
    transfer_probe_count: int = 4
    adversarial_probe_count: int = 3
    validation_family_count: int = 2


@dataclass
class OperatorConfig:
    host_scaffold: str = "nearest_neighbor_2opt"
    allowed_operator_types: list[str] = field(default_factory=lambda: [
        "candidate_ranker",
        "perturbation",
        "candidate_pruner",
        "acceptance",
        "restart_controller",
        "scaffold_selector",
    ])


@dataclass
class ValidationConfig:
    enabled: bool = True
    scaffold_names: list[str] = field(default_factory=lambda: [
        "nearest_neighbor_2opt",
        "cheapest_insertion_2opt",
        "random_restart_2opt",
        "sparse_three_opt",
        "clustered_local_search",
    ])
    survivor_min_transplant_gain: float = 0.002
    survivor_min_scaffold_wins: int = 2
    survivor_max_runtime_inflation: float = 0.2
    survivor_min_family_gain: float = 0.002
    survivor_max_severe_family_regressions: int = 1
    survivor_min_disabled_ablation_drop: float = 0.001


@dataclass
class OptimizationConfig:
    epochs: int = 8


@dataclass
class JudgeConfig:
    enabled: bool = True
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    temperature: float = 0.1
    max_tokens: int = 3200
    timeout_seconds: float = 300.0


@dataclass
class Phase7ConditionConfig:
    name: str
    seed: int
    output_root: str
    execution: ExecutionConfig
    agent: AgentConfig
    generation: GenerationConfig
    replay: ReplayPolicyConfig
    selection: SelectionPolicyConfig
    benchmark: BenchmarkConfig
    operator: OperatorConfig
    validation: ValidationConfig
    optimization: OptimizationConfig
    judge: JudgeConfig
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Phase7ConditionConfig":
        return Phase7ConditionConfig(
            name=data["name"],
            seed=int(data["seed"]),
            output_root=data.get("output_root", "runs/tsp_phase7_suite"),
            execution=ExecutionConfig(**data.get("execution", {})),
            agent=AgentConfig(**data["agent"]),
            generation=GenerationConfig(**data.get("generation", {})),
            replay=ReplayPolicyConfig(**data.get("replay", {})),
            selection=SelectionPolicyConfig(**data.get("selection", {})),
            benchmark=BenchmarkConfig(**data["benchmark"]),
            operator=OperatorConfig(**data.get("operator", {})),
            validation=ValidationConfig(**data.get("validation", {})),
            optimization=OptimizationConfig(**data.get("optimization", {})),
            judge=JudgeConfig(**data.get("judge", {})),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "seed": self.seed,
            "output_root": self.output_root,
            "execution": self.execution.__dict__,
            "agent": self.agent.__dict__,
            "generation": self.generation.__dict__,
            "replay": self.replay.__dict__,
            "selection": self.selection.__dict__,
            "benchmark": self.benchmark.__dict__,
            "operator": self.operator.__dict__,
            "validation": self.validation.__dict__,
            "optimization": self.optimization.__dict__,
            "judge": self.judge.__dict__,
            "metadata": dict(self.metadata),
        }


@dataclass
class Phase7SuiteConfig:
    defaults: dict[str, Any]
    conditions: list[Phase7ConditionConfig]

    @staticmethod
    def load(path: str | Path) -> "Phase7SuiteConfig":
        raw = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        defaults = raw.get("defaults", {})
        conditions: list[Phase7ConditionConfig] = []
        for item in raw.get("conditions", []):
            merged = _deep_merge(defaults, item)
            conditions.append(Phase7ConditionConfig.from_dict(merged))
        if not conditions:
            raise ValueError("The phase-7 suite config did not contain any conditions.")
        return Phase7SuiteConfig(defaults=defaults, conditions=conditions)
