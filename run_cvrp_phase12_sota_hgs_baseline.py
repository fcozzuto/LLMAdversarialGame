from __future__ import annotations

import argparse
import csv
import importlib.metadata
import json
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llm_cvrp.benchmark import load_benchmark_bundle
from llm_cvrp_phase9.validation import validate_solution


def _add_optional_pydeps(path: str | None) -> None:
    if path:
        sys.path.insert(0, str(Path(path)))


def _route_lists(solution: Any) -> list[list[int]]:
    return [[int(node) for node in route.visits()] for route in solution.routes()]


def _mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else float("nan")


def _median(values: list[float]) -> float:
    return statistics.median(values) if values else float("nan")


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the phase-12 PyVRP HGS-style CVRP baseline calibration."
    )
    parser.add_argument("--manifest", default="benchmarks/cvrp_phase9/manifest.json")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--pydeps",
        default=None,
        help="Optional directory containing a local pyvrp/vrplib installation.",
    )
    parser.add_argument("--panel", choices=["holdout", "train", "all"], default="holdout")
    parser.add_argument("--runtime-seconds", type=float, default=30.0)
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    parser.add_argument("--infeasible-gap-penalty", type=float, default=2.0)
    args = parser.parse_args()

    _add_optional_pydeps(args.pydeps)

    from pyvrp import read, solve  # type: ignore
    from pyvrp.stop import MaxRuntime  # type: ignore

    started_at = datetime.now(timezone.utc).isoformat()
    manifest_path = Path(args.manifest)
    bundle = load_benchmark_bundle(manifest_path)
    if args.panel == "holdout":
        instances = bundle.holdout
    elif args.panel == "train":
        instances = bundle.train
    else:
        instances = bundle.train + bundle.holdout

    output_dir = Path(args.output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Output directory already exists and is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    best_by_instance: dict[str, dict[str, Any]] = {}

    for instance in instances:
        problem_path = manifest_path.parent / "cvrplib_x" / f"{instance.name}.vrp"
        data = read(problem_path, round_func="round")
        for seed in args.seeds:
            start = time.perf_counter()
            result = solve(data, MaxRuntime(args.runtime_seconds), seed=int(seed), display=False)
            elapsed = time.perf_counter() - start
            routes = _route_lists(result.best)
            validation = validate_solution(
                instance,
                routes,
                enforce_vehicle_count=False,
                infeasible_gap_penalty=float(args.infeasible_gap_penalty),
            )
            row = {
                "instance": instance.name,
                "seed": int(seed),
                "runtime_seconds_cap": float(args.runtime_seconds),
                "wall_seconds": round(elapsed, 6),
                "pyvrp_objective": int(result.cost()),
                "validated_cost": validation.cost,
                "feasible": bool(validation.feasible),
                "optimality_gap": validation.optimality_gap,
                "penalized_gap": validation.penalized_gap,
                "route_count": validation.route_count,
                "best_known_cost": instance.best_known_cost,
                "errors": "; ".join(validation.errors),
            }
            rows.append(row)

            current_best = best_by_instance.get(instance.name)
            if current_best is None:
                best_by_instance[instance.name] = {**row, "routes": routes}
                continue
            better_gap = float(row["penalized_gap"]) < float(current_best["penalized_gap"])
            tied_gap_better_time = (
                float(row["penalized_gap"]) == float(current_best["penalized_gap"])
                and float(row["wall_seconds"]) < float(current_best["wall_seconds"])
            )
            if better_gap or tied_gap_better_time:
                best_by_instance[instance.name] = {**row, "routes": routes}

    run_fields = [
        "instance",
        "seed",
        "runtime_seconds_cap",
        "wall_seconds",
        "pyvrp_objective",
        "validated_cost",
        "feasible",
        "optimality_gap",
        "penalized_gap",
        "route_count",
        "best_known_cost",
        "errors",
    ]
    _write_csv(output_dir / "pyvrp_hgs_runs.csv", rows, run_fields)

    best_rows = sorted(best_by_instance.values(), key=lambda row: str(row["instance"]))
    best_fields = [field for field in run_fields if field != "errors"] + ["errors"]
    _write_csv(
        output_dir / "pyvrp_hgs_best_by_instance.csv",
        [{key: value for key, value in row.items() if key != "routes"} for row in best_rows],
        best_fields,
    )

    best_gaps = [float(row["penalized_gap"]) for row in best_rows]
    all_gaps = [float(row["penalized_gap"]) for row in rows]
    best_wall_seconds = [float(row["wall_seconds"]) for row in best_rows]
    summary = {
        "baseline": "PyVRP HGS-style solver",
        "phase": "phase-12-sota-cvrp-hgs-baseline",
        "panel": args.panel,
        "manifest": str(manifest_path),
        "started_at_utc": started_at,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_seconds_per_seed": float(args.runtime_seconds),
        "seeds": [int(seed) for seed in args.seeds],
        "pyvrp_version": importlib.metadata.version("pyvrp"),
        "vrplib_version": importlib.metadata.version("vrplib"),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "instance_count": len(best_rows),
        "run_count": len(rows),
        "all_runs_mean_penalized_gap": round(_mean(all_gaps), 6),
        "all_runs_median_penalized_gap": round(_median(all_gaps), 6),
        "best_by_instance_mean_penalized_gap": round(_mean(best_gaps), 6),
        "best_by_instance_median_penalized_gap": round(_median(best_gaps), 6),
        "best_by_instance_mean_wall_seconds": round(_mean(best_wall_seconds), 6),
        "best_by_instance_feasibility_rate": round(
            sum(1 for row in best_rows if row["feasible"]) / max(1, len(best_rows)),
            6,
        ),
        "best_by_instance": best_rows,
    }

    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "best_routes.json").write_text(
        json.dumps({row["instance"]: row["routes"] for row in best_rows}, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Phase 12 PyVRP HGS-Style CVRP Baseline",
        "",
        f"- Panel: `{args.panel}`",
        f"- Runtime cap: `{args.runtime_seconds}` seconds per seed",
        f"- Seeds: `{', '.join(str(seed) for seed in args.seeds)}`",
        f"- PyVRP version: `{summary['pyvrp_version']}`",
        f"- VRPLIB version: `{summary['vrplib_version']}`",
        f"- Total runs: `{summary['run_count']}`",
        f"- Mean penalized gap, all runs: `{summary['all_runs_mean_penalized_gap']}`",
        f"- Mean penalized gap, best seed per instance: `{summary['best_by_instance_mean_penalized_gap']}`",
        f"- Feasibility rate, best seed per instance: `{summary['best_by_instance_feasibility_rate']}`",
        "",
        "| Instance | Best seed | Cost | BKS | Gap | Wall seconds |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in best_rows:
        lines.append(
            f"| {row['instance']} | {row['seed']} | {row['validated_cost']} | "
            f"{row['best_known_cost']} | {float(row['penalized_gap']):.6f} | "
            f"{float(row['wall_seconds']):.3f} |"
        )
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
