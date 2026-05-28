from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path
from statistics import fmean, stdev
from typing import Any


TASK_FAMILIES = ["simple_games", "tsp", "cvrp_phase9_real_world"]
TECHNIQUES = [
    "single_shot",
    "budget_matched_no_replay",
    "random_replay",
    "failure_replay",
    "failure_replay_compression",
]
MODEL_TIERS = [
    "gpt5_2025_08_07",
    "gpt5_1_2025_11_13",
    "gpt5_2_2025_12_11",
    "gpt5_4_2026_03_05",
    "gpt5_5_2026_04_23",
]


def load_jsonish_config(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8-sig")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{path} must be JSON-compatible YAML. This project avoids a PyYAML dependency; "
            "write the config as valid JSON, which is also valid YAML."
        ) from exc


def write_json(path: str | Path, payload: Any) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv_dicts(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_dicts(path: str | Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key)) for key in fieldnames})


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return round(value, 10)
    return value


def safe_float(value: Any, default: float | None = None) -> float | None:
    if value in (None, ""):
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(parsed) or math.isinf(parsed):
        return default
    return parsed


def mean_or_none(values: list[float]) -> float | None:
    clean = [float(value) for value in values if value is not None and not math.isnan(float(value))]
    return fmean(clean) if clean else None


def std_or_zero(values: list[float]) -> float:
    clean = [float(value) for value in values if value is not None and not math.isnan(float(value))]
    return stdev(clean) if len(clean) >= 2 else 0.0


def sem_or_zero(values: list[float]) -> float:
    clean = [float(value) for value in values if value is not None and not math.isnan(float(value))]
    if len(clean) < 2:
        return 0.0
    return stdev(clean) / math.sqrt(len(clean))


def bootstrap_ci(values: list[float], *, seed: int, draws: int = 1000) -> tuple[float | None, float | None]:
    clean = [float(value) for value in values if value is not None and not math.isnan(float(value))]
    if not clean:
        return None, None
    if len(clean) == 1:
        return clean[0], clean[0]
    rng = random.Random(seed)
    estimates = []
    for _ in range(draws):
        sample = [clean[rng.randrange(len(clean))] for _item in clean]
        estimates.append(fmean(sample))
    estimates.sort()
    low_index = max(0, int(0.025 * len(estimates)) - 1)
    high_index = min(len(estimates) - 1, int(0.975 * len(estimates)))
    return estimates[low_index], estimates[high_index]


def code_novelty(previous_code: str | None, code: str) -> float:
    if not previous_code:
        return 0.0
    previous_tokens = _tokens(previous_code)
    current_tokens = _tokens(code)
    if not previous_tokens and not current_tokens:
        return 0.0
    previous_counts: dict[str, int] = {}
    current_counts: dict[str, int] = {}
    for token in previous_tokens:
        previous_counts[token] = previous_counts.get(token, 0) + 1
    for token in current_tokens:
        current_counts[token] = current_counts.get(token, 0) + 1
    keys = set(previous_counts) | set(current_counts)
    intersection = sum(min(previous_counts.get(key, 0), current_counts.get(key, 0)) for key in keys)
    union = sum(max(previous_counts.get(key, 0), current_counts.get(key, 0)) for key in keys)
    return round(1.0 - (intersection / union if union else 1.0), 6)


def _tokens(code: str) -> list[str]:
    token = ""
    tokens: list[str] = []
    for char in code:
        if char.isalnum() or char == "_":
            token += char
        elif token:
            tokens.append(token)
            token = ""
    if token:
        tokens.append(token)
    return tokens


def performance_columns() -> list[str]:
    return [
        "task_family",
        "model_tier",
        "model_name",
        "benchmark_strength_score",
        "benchmark_score_source",
        "reasoning_effort",
        "allow_reasoning_effort_fallback",
        "evolution_technique",
        "seed",
        "epochs_budget",
        "candidate_budget",
        "performance_raw",
        "performance_z",
        "secondary_performance_raw",
        "feasibility_rate",
        "runtime_ms",
        "generation_success_rate",
        "successful_generations",
        "generation_error_count",
        "fallback_generation_count",
        "repair_attempt_count",
        "salvage_attempt_count",
        "executable_candidate_count",
        "materialization_fallback_count",
        "materialization_timeout_count",
        "accepted_fallback_epochs",
        "accepted_executable_epochs",
        "accepted_epochs",
        "acceptance_rate",
        "mean_code_novelty",
        "primary_holdout_win_rate",
        "primary_holdout_score_margin",
        "tsp_primary_metric",
        "final_tsplib_gap",
        "final_transfer_gap",
        "final_synthetic_holdout_gap",
        "final_worst_gap",
        "final_gap_range",
        "adaptation_efficiency",
        "heldout_feasibility_rate",
        "heldout_penalized_gap",
        "heldout_feasible_gap",
        "heldout_runtime_ms",
        "artifact_path",
    ]


def model_strength_columns() -> list[str]:
    return [
        "model_tier",
        "provider",
        "model_name",
        "benchmark_strength_score",
        "benchmark_score_source",
        "benchmark_name",
        "benchmark_source_url",
        "notes",
    ]
