from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import fmean
from typing import Any

from model_strength_factorial_common import TECHNIQUES, load_jsonish_config, write_csv_dicts, write_json


# Defaults from OpenAI model pricing pages checked on 2026-05-27. Update
# before launching if the dashboard or model docs show different prices.
PRICE_PER_MILLION_TOKENS = {
    "gpt-5-2025-08-07": {"input": 1.25, "output": 10.00},
    "gpt-5.1-2025-11-13": {"input": 1.25, "output": 10.00},
    "gpt-5.2-2025-12-11": {"input": 1.75, "output": 14.00},
    "gpt-5.4-2026-03-05": {"input": 2.50, "output": 15.00},
    "gpt-5.5-2026-04-23": {"input": 5.00, "output": 30.00},
}


def _candidate_budget(task_cfg: dict[str, Any], technique: str) -> int:
    return 1 if technique == "single_shot" else int(task_cfg["epochs"])


def _rough_tokens(text: str) -> float:
    return max(1.0, len(text or "") / 4.0)


def _reference_token_stats(
    reference_run_root: Path | None,
    *,
    max_candidates_per_task_technique: int,
) -> dict[tuple[str, str], dict[str, float]]:
    if reference_run_root is None or not reference_run_root.exists():
        return {}
    grouped_paths: dict[tuple[str, str], list[Path]] = {}
    for path in reference_run_root.glob("cell_artifacts/*/*/*/seed_*/candidates/candidate_*.json"):
        parts = path.parts
        try:
            index = parts.index("cell_artifacts")
            task_family = parts[index + 1]
            technique = parts[index + 3]
        except (ValueError, IndexError):
            continue
        key = (task_family, technique)
        grouped_paths.setdefault(key, []).append(path)

    grouped: dict[tuple[str, str], list[tuple[float, float]]] = {}
    available_counts = {key: len(paths) for key, paths in grouped_paths.items()}
    for key, paths in grouped_paths.items():
        selected_paths = _evenly_sample_paths(paths, max_candidates_per_task_technique)
        for path in selected_paths:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            generation = payload.get("generation", {})
            prompt = str(generation.get("prompt", ""))
            raw_text = str(generation.get("raw_text", ""))
            grouped.setdefault(key, []).append((_rough_tokens(prompt), _rough_tokens(raw_text)))
    output = {}
    for key, values in grouped.items():
        output[key] = {
            "mean_input_tokens": fmean(item[0] for item in values),
            "mean_output_tokens": fmean(item[1] for item in values),
            "n_reference_candidates": len(values),
            "n_available_reference_candidates": available_counts.get(key, len(values)),
        }
    return output


def _evenly_sample_paths(paths: list[Path], max_count: int) -> list[Path]:
    ordered = sorted(paths)
    if max_count <= 0 or len(ordered) <= max_count:
        return ordered
    if max_count == 1:
        return [ordered[0]]
    last_index = len(ordered) - 1
    indexes = [round(index * last_index / (max_count - 1)) for index in range(max_count)]
    return [ordered[index] for index in indexes]


def estimate_cost(
    config: dict[str, Any],
    *,
    techniques: list[str],
    reference_stats: dict[tuple[str, str], dict[str, float]],
    output_token_multiplier: float,
    contingency_multiplier: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in config["model_tiers"]:
        model_name = str(spec["model_name"])
        prices = PRICE_PER_MILLION_TOKENS.get(model_name)
        if prices is None:
            raise SystemExit(f"No default price is configured for model {model_name}. Update PRICE_PER_MILLION_TOKENS.")
        for task_family, task_cfg in config["task_families"].items():
            for technique in techniques:
                candidate_count = int(task_cfg["seeds"]) * _candidate_budget(task_cfg, technique)
                stats = reference_stats.get((task_family, technique)) or reference_stats.get((task_family, "single_shot"))
                mean_input = float(stats.get("mean_input_tokens", 900.0)) if stats else 900.0
                mean_output = float(stats.get("mean_output_tokens", 700.0)) if stats else 700.0
                n_reference = int(stats.get("n_reference_candidates", 0)) if stats else 0
                n_available_reference = int(stats.get("n_available_reference_candidates", 0)) if stats else 0
                adjusted_output = mean_output * output_token_multiplier
                base_cost = ((candidate_count * mean_input * prices["input"]) + (candidate_count * adjusted_output * prices["output"])) / 1_000_000
                rows.append(
                    {
                        "model_tier": spec["model_tier"],
                        "model_name": model_name,
                        "task_family": task_family,
                        "evolution_technique": technique,
                        "candidate_count": candidate_count,
                        "mean_input_tokens_per_candidate": mean_input,
                        "mean_output_tokens_per_candidate": adjusted_output,
                        "n_reference_candidates": n_reference,
                        "n_available_reference_candidates": n_available_reference,
                        "input_price_per_million": prices["input"],
                        "output_price_per_million": prices["output"],
                        "estimated_cost_usd": base_cost,
                        "estimated_cost_with_contingency_usd": base_cost * contingency_multiplier,
                    }
                )
    total = sum(float(row["estimated_cost_usd"]) for row in rows)
    total_with_contingency = sum(float(row["estimated_cost_with_contingency_usd"]) for row in rows)
    summary = {
        "candidate_count": sum(int(row["candidate_count"]) for row in rows),
        "estimated_cost_usd": total,
        "estimated_cost_with_contingency_usd": total_with_contingency,
        "output_token_multiplier": output_token_multiplier,
        "contingency_multiplier": contingency_multiplier,
    }
    return rows, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate the clean model-strength continuum campaign cost from empirical prompt/response sizes.")
    parser.add_argument("--config", default="configs/model_strength_continuum_factorial.yaml")
    parser.add_argument("--reference-run-root", default="runs/cross_family_model_x_evolution_factorial/20260524_172130")
    parser.add_argument("--output-dir", default="DO NOT COMMIT/model_strength_continuum_cost_estimate")
    parser.add_argument("--output-token-multiplier", type=float, default=1.25, help="Buffer for hidden reasoning/repair output tokens not visible in raw text.")
    parser.add_argument("--contingency-multiplier", type=float, default=1.20, help="Final balance safety buffer.")
    parser.add_argument("--technique", default=None, help="Optional comma-separated technique subset. Use single_shot for calibration.")
    parser.add_argument(
        "--max-reference-candidates-per-task-technique",
        type=int,
        default=250,
        help="Deterministic cap for old candidate JSON files scanned per task x technique. Use 0 to scan all.",
    )
    args = parser.parse_args()

    config = load_jsonish_config(args.config)
    techniques = [item.strip() for item in args.technique.split(",") if item.strip()] if args.technique else list(TECHNIQUES)
    unknown = [item for item in techniques if item not in TECHNIQUES]
    if unknown:
        raise SystemExit(f"Unknown technique(s): {', '.join(unknown)}")
    reference_stats = _reference_token_stats(
        Path(args.reference_run_root) if args.reference_run_root else None,
        max_candidates_per_task_technique=max(0, int(args.max_reference_candidates_per_task_technique)),
    )
    rows, summary = estimate_cost(
        config,
        techniques=techniques,
        reference_stats=reference_stats,
        output_token_multiplier=float(args.output_token_multiplier),
        contingency_multiplier=float(args.contingency_multiplier),
    )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv_dicts(
        output_dir / "cost_estimate_by_cell.csv",
        rows,
        [
            "model_tier",
            "model_name",
            "task_family",
            "evolution_technique",
            "candidate_count",
            "mean_input_tokens_per_candidate",
            "mean_output_tokens_per_candidate",
            "n_reference_candidates",
            "n_available_reference_candidates",
            "input_price_per_million",
            "output_price_per_million",
            "estimated_cost_usd",
            "estimated_cost_with_contingency_usd",
        ],
    )
    summary["max_reference_candidates_per_task_technique"] = max(0, int(args.max_reference_candidates_per_task_technique))
    summary["reference_sampling_method"] = "evenly_spaced_by_sorted_candidate_path"
    summary["reference_groups_used"] = len(reference_stats)
    write_json(output_dir / "cost_estimate_summary.json", summary)
    print(f"candidate_count: {summary['candidate_count']}")
    print(f"estimated_cost_usd: {summary['estimated_cost_usd']:.2f}")
    print(f"estimated_cost_with_contingency_usd: {summary['estimated_cost_with_contingency_usd']:.2f}")
    print(f"cost_estimate_by_cell.csv: {output_dir / 'cost_estimate_by_cell.csv'}")


if __name__ == "__main__":
    main()
