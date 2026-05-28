from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import fmean, stdev
from typing import Any

from model_strength_factorial_common import load_jsonish_config, read_csv_dicts, write_csv_dicts, write_json


def _safe_float(value: Any, default: float | None = None) -> float | None:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _z_scores(values: list[float]) -> list[float]:
    if not values:
        return []
    if len(values) == 1:
        return [0.0]
    sd = stdev(values)
    if sd <= 1e-12:
        return [0.0 for _ in values]
    mean_value = fmean(values)
    return [(value - mean_value) / sd for value in values]


def _train_oriented_score(candidate_path: Path, task_family: str) -> float | None:
    try:
        payload = json.loads(candidate_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    train = payload.get("train_summary", {})
    if task_family == "simple_games":
        return _safe_float(train.get("mean_score_margin"))
    if task_family == "tsp":
        value = _safe_float(train.get("mean_optimality_gap"))
        return -value if value is not None else None
    if task_family == "cvrp_phase9_real_world":
        summary = train.get("summary", {})
        value = _safe_float(summary.get("mean_penalized_gap"))
        return -value if value is not None else None
    return None


def _generation_quality(candidate_path: Path, task_family: str) -> float:
    try:
        payload = json.loads(candidate_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0.0
    generation = payload.get("generation", {})
    if generation.get("used_fallback") or generation.get("error"):
        return 0.0
    train = payload.get("train_summary", {})
    if task_family == "tsp" and train.get("materialization_used_fallback"):
        return 0.0
    return 1.0


def _load_rows(run_root: Path) -> list[dict[str, Any]]:
    path = run_root / "all_runs_long.raw.csv"
    if not path.exists():
        path = run_root / "all_runs_long.csv"
    if not path.exists():
        raise SystemExit(f"No all_runs_long.raw.csv or all_runs_long.csv found under {run_root}")
    return list(read_csv_dicts(path))


def derive_scores(run_root: Path) -> list[dict[str, Any]]:
    rows = _load_rows(run_root)
    records: list[dict[str, Any]] = []
    for row in rows:
        artifact_path = Path(str(row.get("artifact_path", "")))
        candidate_path = artifact_path / "candidates" / "candidate_001.json"
        task_family = str(row.get("task_family", ""))
        train_score = _train_oriented_score(candidate_path, task_family)
        generation_quality = _generation_quality(candidate_path, task_family)
        records.append(
            {
                "model_tier": row.get("model_tier", ""),
                "model_name": row.get("model_name", ""),
                "task_family": task_family,
                "seed": row.get("seed", ""),
                "train_oriented_score": train_score,
                "generation_quality": generation_quality,
                "candidate_path": str(candidate_path),
            }
        )

    by_task: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        if record["train_oriented_score"] is not None:
            by_task.setdefault(str(record["task_family"]), []).append(record)
    for task_records in by_task.values():
        z_values = _z_scores([float(record["train_oriented_score"]) for record in task_records])
        for record, z_value in zip(task_records, z_values):
            record["task_train_z"] = z_value
    by_model: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_model.setdefault(str(record["model_tier"]), []).append(record)

    model_rows = []
    raw_scores = []
    for model_tier, model_records in sorted(by_model.items()):
        z_values = [float(record.get("task_train_z")) for record in model_records if record.get("task_train_z") is not None]
        generation_values = [float(record.get("generation_quality") or 0.0) for record in model_records]
        mean_task_z = fmean(z_values) if z_values else 0.0
        mean_generation_quality = fmean(generation_values) if generation_values else 0.0
        raw_score = mean_task_z + (0.25 * mean_generation_quality)
        raw_scores.append(raw_score)
        model_rows.append(
            {
                "model_tier": model_tier,
                "model_name": model_records[0].get("model_name", ""),
                "calibration_rows": len(model_records),
                "mean_task_train_z": mean_task_z,
                "mean_generation_quality": mean_generation_quality,
                "raw_calibration_score": raw_score,
            }
        )

    if model_rows:
        min_score = min(raw_scores)
        max_score = max(raw_scores)
        span = max_score - min_score
        for row in model_rows:
            raw_score = float(row["raw_calibration_score"])
            row["benchmark_strength_score"] = 3.0 if span <= 1e-12 else 1.0 + (4.0 * (raw_score - min_score) / span)
            row["benchmark_score_source"] = "empirical_project_calibration_train_validators"
            row["benchmark_name"] = "small project calibration suite: train-validator z-score plus generation validity"
            row["benchmark_source_url"] = str(run_root)
    return model_rows


def _write_calibrated_config(base_config_path: Path, output_config_path: Path, score_rows: list[dict[str, Any]], calibration_root: Path) -> None:
    config = load_jsonish_config(base_config_path)
    by_tier = {str(row["model_tier"]): row for row in score_rows}
    for spec in config.get("model_tiers", []):
        tier = str(spec.get("model_tier"))
        if tier not in by_tier:
            continue
        score = by_tier[tier]
        spec["benchmark_strength_score"] = score["benchmark_strength_score"]
        spec["benchmark_score_source"] = score["benchmark_score_source"]
        spec["benchmark_name"] = score["benchmark_name"]
        spec["benchmark_source_url"] = score["benchmark_source_url"]
        spec["notes"] = (
            f"Calibration-derived from {calibration_root}; raw_score={float(score['raw_calibration_score']):.6f}; "
            f"mean_task_train_z={float(score['mean_task_train_z']):.6f}; "
            f"mean_generation_quality={float(score['mean_generation_quality']):.6f}."
        )
    config["require_empirical_model_strength_scores"] = True
    output_config_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_config_path, config)


def main() -> None:
    parser = argparse.ArgumentParser(description="Derive empirical model-strength scores from the small calibration suite.")
    parser.add_argument("--calibration-run-root", required=True)
    parser.add_argument("--base-config", default="configs/model_strength_continuum_factorial.yaml")
    parser.add_argument("--output-config", required=True)
    args = parser.parse_args()

    run_root = Path(args.calibration_run_root)
    score_rows = derive_scores(run_root)
    if not score_rows:
        raise SystemExit("No calibration scores could be derived.")
    write_csv_dicts(
        run_root / "empirical_model_strength_scores.csv",
        score_rows,
        [
            "model_tier",
            "model_name",
            "calibration_rows",
            "mean_task_train_z",
            "mean_generation_quality",
            "raw_calibration_score",
            "benchmark_strength_score",
            "benchmark_score_source",
            "benchmark_name",
            "benchmark_source_url",
        ],
    )
    _write_calibrated_config(Path(args.base_config), Path(args.output_config), score_rows, run_root)
    print(f"empirical_model_strength_scores.csv: {run_root / 'empirical_model_strength_scores.csv'}")
    print(f"calibrated_config: {args.output_config}")


if __name__ == "__main__":
    main()
