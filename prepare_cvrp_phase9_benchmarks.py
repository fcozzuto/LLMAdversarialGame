from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request

from llm_cvrp.benchmark import compute_solution_cost, parse_cvrplib_instance, parse_cvrplib_solution
from llm_cvrp_phase9.features import describe_instance


BASE_URL = "https://galgos.inf.puc-rio.br"
INSTANCE_SET_URL = f"{BASE_URL}/cvrplib/en/instances"
TRAIN_INSTANCES = [
    "X-n101-k25",
    "X-n110-k13",
    "X-n125-k30",
    "X-n134-k13",
    "X-n148-k46",
    "X-n157-k13",
]
HOLDOUT_INSTANCES = [
    "X-n176-k26",
    "X-n190-k8",
    "X-n214-k11",
    "X-n223-k34",
]


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


def _fetch_catalog(*, force: bool, root: Path) -> dict[str, dict[str, int | float]]:
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as handle:
        catalog_path = Path(handle.name)
    if catalog_path.exists():
        catalog_path.unlink()
    try:
        _download(INSTANCE_SET_URL, catalog_path, force=force)
        payload = catalog_path.read_text(encoding="utf-8", errors="replace")
    finally:
        if catalog_path.exists():
            catalog_path.unlink()
    rows = re.findall(
        r'<tr class="collapse border-bottom" id="set-17">(.*?)</tr>',
        payload,
        flags=re.S,
    )
    catalog: dict[str, dict[str, int | float]] = {}
    for row in rows:
        name_match = re.search(r"/download/instance/(\d+)\"[^>]*>\s*(X-n\d+-k\d+)\s*<", row)
        cost_match = re.search(r"/download/instanceSolution/(\d+)\"[^>]*>.*?\$([0-9{},.]+)\$", row, flags=re.S)
        if name_match is None or cost_match is None:
            continue
        instance_id = int(name_match.group(1))
        solution_id = int(cost_match.group(1))
        if instance_id != solution_id:
            continue
        catalog[name_match.group(2)] = {
            "id": instance_id,
            "upper_bound": float(cost_match.group(2).replace(",", "").replace("{", "").replace("}", "")),
        }
    if not catalog:
        raise ValueError("Failed to parse the official CVRPLIB X-instance catalog.")
    return catalog


def _fetch_instance(name: str, catalog: dict[str, dict[str, int | float]], output_root: Path, *, force: bool) -> dict[str, object]:
    if name not in catalog:
        raise KeyError(f"{name} is missing from the scraped CVRPLIB X catalog.")
    record = catalog[name]
    instance_id = int(record["id"])
    cvrp_dir = output_root / "cvrplib_x"
    cvrp_dir.mkdir(parents=True, exist_ok=True)
    problem_path = cvrp_dir / f"{name}.vrp"
    solution_path = cvrp_dir / f"{name}.sol"
    _download(f"{BASE_URL}/cvrplib/en/download/instance/{instance_id}", problem_path, force=force)
    _download(f"{BASE_URL}/cvrplib/en/download/instanceSolution/{instance_id}", solution_path, force=force)
    instance = parse_cvrplib_instance(
        problem_path,
        source="CVRPLIB",
        family="Uchoa_X",
        tags=["cvrplib", "uchoa_x", "euc_2d"],
    )
    routes, solution_cost = parse_cvrplib_solution(solution_path)
    recomputed_cost = compute_solution_cost(instance, routes)
    if solution_cost != recomputed_cost:
        raise ValueError(f"{name} solution mismatch: file cost={solution_cost}, recomputed={recomputed_cost}")
    if int(round(float(record["upper_bound"]))) != solution_cost:
        raise ValueError(f"{name} upper-bound mismatch: index={record['upper_bound']}, solution={solution_cost}")
    return {
        "kind": "cvrplib",
        "name": instance.name,
        "problem_path": str(problem_path.relative_to(output_root)).replace("\\", "/"),
        "solution_path": str(solution_path.relative_to(output_root)).replace("\\", "/"),
        "best_known_cost": int(solution_cost),
        "source": "CVRPLIB",
        "family": "Uchoa_X",
        "tags": ["cvrplib", "uchoa_x", "euc_2d"],
        "vehicle_count_hint": int(instance.vehicle_count_hint) if instance.vehicle_count_hint is not None else None,
        "descriptors": describe_instance(instance),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and prepare the phase-9 CVRPLIB X benchmark subset.")
    parser.add_argument("--output-root", default="benchmarks/cvrp_phase9", help="Benchmark root directory.")
    parser.add_argument("--force", action="store_true", help="Redownload files even if they already exist.")
    args = parser.parse_args()

    root = Path(args.output_root)
    root.mkdir(parents=True, exist_ok=True)
    catalog = _fetch_catalog(force=args.force, root=root)
    train = [_fetch_instance(name, catalog, root, force=args.force) for name in TRAIN_INSTANCES]
    holdout = [_fetch_instance(name, catalog, root, force=args.force) for name in HOLDOUT_INSTANCES]
    manifest = {
        "description": (
            "Phase-9 bounded real-world CVRP benchmark built from the official CVRPLIB Uchoa X family. "
            "The split keeps a moderate-size training subset and a held-out subset for frozen final evaluation."
        ),
        "sources": [
            {
                "name": "CVRPLIB X Set",
                "url": "https://galgos.inf.puc-rio.br/cvrplib/en/instances",
                "notes": "Official CVRPLIB catalog page for the Uchoa X instances with downloadable instance and solution files.",
            },
            {
                "name": "Uchoa et al. 2017",
                "url": "https://doi.org/10.1016/j.ejor.2016.08.012",
                "notes": "Primary description of the X benchmark family.",
            },
        ],
        "train": train,
        "holdout": holdout,
        "adversarial": [],
        "synthetic_holdout": [],
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote phase-9 benchmark manifest to {manifest_path}")


if __name__ == "__main__":
    main()
