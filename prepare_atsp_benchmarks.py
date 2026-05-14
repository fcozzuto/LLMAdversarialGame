from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import urllib.request

from llm_atsp.benchmark import parse_tsplib_atsp


BASE_URL = "https://softlib.rice.edu/pub/tsplib/atsp/"
TRAIN_CANDIDATES = [
    "br17",
    "ftv33",
    "ftv35",
    "ftv38",
]
HOLDOUT_CANDIDATES = [
    "p43",
    "ft53",
    "ftv44",
    "ry48p",
]
BEST_KNOWN_COSTS = {
    "br17": 39,
    "ft53": 6905,
    "ftv33": 1286,
    "ftv35": 1473,
    "ftv38": 1530,
    "ftv44": 1613,
    "p43": 5620,
    "ry48p": 14422,
}
SYNTHETIC_ADVERSARIAL = [
    {"name": "adv_wind_clusters_16_a", "family": "wind_clusters", "dimension": 16, "seed": 3101},
    {"name": "adv_clockwise_ring_16_a", "family": "clockwise_ring", "dimension": 16, "seed": 3102},
    {"name": "adv_corridor_drift_16_a", "family": "corridor_drift", "dimension": 16, "seed": 3103},
    {"name": "adv_hub_spokes_16_a", "family": "hub_spokes", "dimension": 16, "seed": 3104},
]
SYNTHETIC_HOLDOUT = [
    {"name": "holdout_wind_clusters_18_a", "family": "wind_clusters", "dimension": 18, "seed": 4101},
    {"name": "holdout_clockwise_ring_18_a", "family": "clockwise_ring", "dimension": 18, "seed": 4102},
    {"name": "holdout_corridor_drift_18_a", "family": "corridor_drift", "dimension": 18, "seed": 4103},
    {"name": "holdout_hub_spokes_18_a", "family": "hub_spokes", "dimension": 18, "seed": 4104},
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


def _fetch_instance(name: str, atsp_dir: Path, *, force: bool) -> dict[str, object]:
    problem_path = atsp_dir / f"{name}.atsp.gz"
    _download(f"{BASE_URL}{name}.atsp.gz", problem_path, force=force)
    instance = parse_tsplib_atsp(problem_path, source="TSPLIB95", family=_family_from_name(name), tags=["tsplib95", "atsp"])
    return {
        "kind": "tsplib",
        "name": instance.name,
        "problem_path": str(problem_path.relative_to(atsp_dir.parent)).replace("\\", "/"),
        "best_known_cost": int(BEST_KNOWN_COSTS[name]),
        "source": "TSPLIB95",
        "family": _family_from_name(name),
        "tags": ["tsplib95", "atsp"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and prepare the ATSP replay-transfer benchmark subset.")
    parser.add_argument("--output-root", default="benchmarks/atsp", help="Benchmark root directory.")
    parser.add_argument("--force", action="store_true", help="Redownload files even if they already exist.")
    args = parser.parse_args()

    root = Path(args.output_root)
    atsp_dir = root / "tsplib95"
    atsp_dir.mkdir(parents=True, exist_ok=True)

    train = [_fetch_instance(name, atsp_dir, force=args.force) for name in TRAIN_CANDIDATES]
    holdout = [_fetch_instance(name, atsp_dir, force=args.force) for name in HOLDOUT_CANDIDATES]

    manifest = {
        "description": "Replay-aware ATSP benchmark subset built from official TSPLIB95 ATSP instances plus exact synthetic asymmetric holdouts.",
        "sources": [
            {
                "name": "TSPLIB95 ATSP index",
                "url": "https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/atsp.html",
                "notes": "Official ATSP instance catalog.",
            },
            {
                "name": "TSPLIB95 ATSP best known solutions",
                "url": "https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/ATSP.html",
                "notes": "Official best-known objective values for ATSP instances.",
            },
            {
                "name": "TSPLIB mirror",
                "url": "https://softlib.rice.edu/pub/tsplib/atsp/",
                "notes": "Mirror used by the preparation script for direct file retrieval.",
            },
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
