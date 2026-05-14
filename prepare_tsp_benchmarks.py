from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import urllib.request

from llm_tsp.benchmark import compute_tour_cost, parse_tsplib_euc_2d, parse_tsplib_tour


BASE_URL = "https://softlib.rice.edu/pub/tsplib/tsp/"
TRAIN_CANDIDATES = [
    "berlin52",
    "eil101",
    "kroA100",
    "kroC100",
    "lin105",
    "a280",
]
HOLDOUT_CANDIDATES = [
    "ch130",
    "ch150",
    "kroD100",
    "pcb442",
    "pr76",
    "rd100",
    "st70",
]
SYNTHETIC_ADVERSARIAL = [
    {"name": "adv_clustered_16_a", "family": "clustered_gaussian", "dimension": 16, "seed": 1101},
    {"name": "adv_ring_bridge_16_a", "family": "ring_bridge", "dimension": 16, "seed": 1102},
    {"name": "adv_grid_outliers_16_a", "family": "grid_outliers", "dimension": 16, "seed": 1103},
    {"name": "adv_two_corridors_16_a", "family": "two_corridors", "dimension": 16, "seed": 1104},
]
SYNTHETIC_HOLDOUT = [
    {"name": "holdout_clustered_18_a", "family": "clustered_gaussian", "dimension": 18, "seed": 2101},
    {"name": "holdout_ring_bridge_18_a", "family": "ring_bridge", "dimension": 18, "seed": 2102},
    {"name": "holdout_grid_outliers_18_a", "family": "grid_outliers", "dimension": 18, "seed": 2103},
    {"name": "holdout_two_corridors_18_a", "family": "two_corridors", "dimension": 18, "seed": 2104},
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


def _fetch_instance(name: str, tsplib_dir: Path, *, force: bool) -> dict[str, object] | None:
    problem_path = tsplib_dir / f"{name}.tsp.gz"
    tour_candidates = [tsplib_dir / f"{name}.opt.tour.gz", tsplib_dir / f"{name}.opt.tour"]
    _download(f"{BASE_URL}{name}.tsp.gz", problem_path, force=force)
    tour_path = None
    for candidate in tour_candidates:
        suffix = candidate.name
        try:
            _download(f"{BASE_URL}{suffix}", candidate, force=force)
            tour_path = candidate
            break
        except Exception:
            if candidate.exists():
                candidate.unlink()
    if tour_path is None or not tour_path.exists():
        return None

    instance = parse_tsplib_euc_2d(problem_path, source="TSPLIB95", family=_family_from_name(name), tags=["tsplib95"])
    tour = parse_tsplib_tour(tour_path)
    best_cost = compute_tour_cost(instance, tour)
    return {
        "kind": "tsplib",
        "name": instance.name,
        "problem_path": str(problem_path.relative_to(tsplib_dir.parent)).replace("\\", "/"),
        "tour_path": str(tour_path.relative_to(tsplib_dir.parent)).replace("\\", "/"),
        "best_known_cost": int(best_cost),
        "source": "TSPLIB95",
        "family": _family_from_name(name),
        "tags": ["tsplib95", "euc_2d"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and prepare the phase-5 TSP benchmark subset.")
    parser.add_argument("--output-root", default="benchmarks/tsp", help="Benchmark root directory.")
    parser.add_argument("--force", action="store_true", help="Redownload files even if they already exist.")
    args = parser.parse_args()

    root = Path(args.output_root)
    tsplib_dir = root / "tsplib95"
    tsplib_dir.mkdir(parents=True, exist_ok=True)

    train: list[dict[str, object]] = []
    holdout: list[dict[str, object]] = []
    skipped: list[str] = []

    for name in TRAIN_CANDIDATES:
        record = _fetch_instance(name, tsplib_dir, force=args.force)
        if record is None:
            skipped.append(name)
            continue
        train.append(record)
    for name in HOLDOUT_CANDIDATES:
        record = _fetch_instance(name, tsplib_dir, force=args.force)
        if record is None:
            skipped.append(name)
            continue
        holdout.append(record)

    if len(train) < 4 or len(holdout) < 4:
        raise SystemExit(
            f"Prepared too few benchmark instances after EUC_2D filtering: train={len(train)}, holdout={len(holdout)}, skipped={skipped}"
        )

    manifest = {
        "description": "Phase-5 replay-aware TSP benchmark subset built from official TSPLIB95 EUC_2D instances plus exact synthetic holdouts.",
        "sources": [
            {
                "name": "TSPLIB95",
                "url": "https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp.html",
                "notes": "Official TSPLIB95 TSP instance and opt tour index.",
            },
            {
                "name": "TSPLIB mirror",
                "url": "https://softlib.rice.edu/pub/tsplib/tsp/",
                "notes": "Mirror used by the preparation script for direct file retrieval.",
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
        "skipped_candidates": skipped,
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote benchmark manifest to {manifest_path}")


if __name__ == "__main__":
    main()
