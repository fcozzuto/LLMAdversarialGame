from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import urllib.request

from llm_cvrp.benchmark import compute_solution_cost, parse_cvrplib_instance, parse_cvrplib_solution


BASE_URL = "https://galgos.inf.puc-rio.br"
INSTANCE_CATALOG = {
    "A-n32-k5": {"id": 4, "upper_bound": 784},
    "B-n31-k5": {"id": 6, "upper_bound": 672},
    "E-n33-k4": {"id": 59, "upper_bound": 835},
    "P-n40-k5": {"id": 82, "upper_bound": 458},
    "A-n44-k6": {"id": 15, "upper_bound": 937},
    "B-n43-k6": {"id": 37, "upper_bound": 742},
    "A-n45-k7": {"id": 17, "upper_bound": 1146},
    "E-n51-k5": {"id": 60, "upper_bound": 521},
    "P-n50-k7": {"id": 84, "upper_bound": 554},
    "B-n50-k7": {"id": 41, "upper_bound": 741},
    "P-n50-k8": {"id": 85, "upper_bound": 631},
}
TRAIN_CANDIDATES = [
    "A-n32-k5",
    "B-n31-k5",
    "E-n33-k4",
    "P-n40-k5",
    "A-n44-k6",
]
HOLDOUT_CANDIDATES = [
    "B-n43-k6",
    "A-n45-k7",
    "E-n51-k5",
    "P-n50-k7",
    "B-n50-k7",
]
SYNTHETIC_ADVERSARIAL = [
    {"name": "adv_clustered_demand_10_a", "family": "clustered_demand", "dimension": 10, "seed": 5101},
    {"name": "adv_corridor_split_10_a", "family": "corridor_split", "dimension": 10, "seed": 5102},
    {"name": "adv_radial_heavy_10_a", "family": "radial_heavy", "dimension": 10, "seed": 5103},
    {"name": "adv_alternating_belt_10_a", "family": "alternating_belt", "dimension": 10, "seed": 5104},
]
SYNTHETIC_HOLDOUT = [
    {"name": "holdout_clustered_demand_12_a", "family": "clustered_demand", "dimension": 12, "seed": 6101},
    {"name": "holdout_corridor_split_12_a", "family": "corridor_split", "dimension": 12, "seed": 6102},
    {"name": "holdout_radial_heavy_12_a", "family": "radial_heavy", "dimension": 12, "seed": 6103},
    {"name": "holdout_alternating_belt_12_a", "family": "alternating_belt", "dimension": 12, "seed": 6104},
]


def _family_from_name(name: str) -> str:
    match = re.match(r"^[A-Za-z]+", name)
    return match.group(0) if match else name


def _download(url: str, path: Path, *, force: bool) -> None:
    if path.exists() and not force:
        return
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=60.0) as response:
            path.write_bytes(response.read())
            return
    except Exception:
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            f"Invoke-WebRequest -Uri '{url}' -OutFile '{path}' -UseBasicParsing",
        ]
        subprocess.run(command, check=True)


def _fetch_instance(name: str, cvrp_dir: Path, *, force: bool) -> dict[str, object]:
    if name not in INSTANCE_CATALOG:
        raise KeyError(f"{name} is missing from the curated CVRPLIB subset catalog.")
    record = INSTANCE_CATALOG[name]
    problem_path = cvrp_dir / f"{name}.vrp"
    solution_path = cvrp_dir / f"{name}.sol"
    _download(f"{BASE_URL}/cvrplib/en/download/instance/{record['id']}", problem_path, force=force)
    _download(f"{BASE_URL}/cvrplib/en/download/instanceSolution/{record['id']}", solution_path, force=force)

    instance = parse_cvrplib_instance(problem_path, source="CVRPLIB", family=_family_from_name(name), tags=["cvrplib", "euc_2d"])
    routes, solution_cost = parse_cvrplib_solution(solution_path)
    recomputed_cost = compute_solution_cost(instance, routes)
    if solution_cost != recomputed_cost:
        raise ValueError(f"{name} solution mismatch: file cost={solution_cost}, recomputed={recomputed_cost}")
    if int(record["upper_bound"]) != solution_cost:
        raise ValueError(f"{name} upper-bound mismatch: index={record['upper_bound']}, solution={solution_cost}")

    return {
        "kind": "cvrplib",
        "name": instance.name,
        "problem_path": str(problem_path.relative_to(cvrp_dir.parent)).replace("\\", "/"),
        "solution_path": str(solution_path.relative_to(cvrp_dir.parent)).replace("\\", "/"),
        "best_known_cost": int(solution_cost),
        "source": "CVRPLIB",
        "family": _family_from_name(name),
        "tags": ["cvrplib", "euc_2d"],
        "vehicle_count_hint": int(instance.vehicle_count_hint) if instance.vehicle_count_hint is not None else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and prepare the CVRPLIB replay-transfer benchmark subset.")
    parser.add_argument("--output-root", default="benchmarks/cvrp", help="Benchmark root directory.")
    parser.add_argument("--force", action="store_true", help="Redownload files even if they already exist.")
    args = parser.parse_args()

    root = Path(args.output_root)
    cvrp_dir = root / "cvrplib"
    cvrp_dir.mkdir(parents=True, exist_ok=True)

    train = [_fetch_instance(name, cvrp_dir, force=args.force) for name in TRAIN_CANDIDATES]
    holdout = [_fetch_instance(name, cvrp_dir, force=args.force) for name in HOLDOUT_CANDIDATES]

    manifest = {
        "description": "Replay-aware CVRP benchmark subset built from official CVRPLIB instances plus exact synthetic routing holdouts.",
        "sources": [
            {
                "name": "CVRPLIB",
                "url": "https://galgos.inf.puc-rio.br/cvrplib/en/instances",
                "notes": "Official CVRPLIB instance catalog with solution downloads and upper bounds.",
            }
        ],
        "train": train,
        "holdout": holdout,
        "adversarial": [
            {
                "kind": "synthetic",
                "source": "synthetic_adversarial_pool",
                **item,
            }
            for item in SYNTHETIC_ADVERSARIAL
        ],
        "synthetic_holdout": [
            {
                "kind": "synthetic",
                "source": "synthetic_holdout_pool",
                **item,
            }
            for item in SYNTHETIC_HOLDOUT
        ],
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote benchmark manifest to {manifest_path}")


if __name__ == "__main__":
    main()
