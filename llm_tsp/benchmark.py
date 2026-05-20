from __future__ import annotations

from dataclasses import dataclass
import gzip
import json
import math
from pathlib import Path
from typing import Any


def tsplib_euc_2d_distance(left: tuple[float, float], right: tuple[float, float]) -> int:
    dx = float(left[0]) - float(right[0])
    dy = float(left[1]) - float(right[1])
    return int(math.sqrt((dx * dx) + (dy * dy)) + 0.5)


@dataclass
class TSPInstance:
    name: str
    source: str
    dimension: int
    edge_weight_type: str
    coordinates: list[tuple[float, float]]
    best_known_cost: int
    family: str
    tags: list[str]
    descriptors: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "dimension": self.dimension,
            "edge_weight_type": self.edge_weight_type,
            "coordinates": [[float(x), float(y)] for x, y in self.coordinates],
            "best_known_cost": int(self.best_known_cost),
            "family": self.family,
            "tags": list(self.tags),
            "descriptors": dict(self.descriptors or {}),
        }


@dataclass
class BenchmarkBundle:
    train: list[TSPInstance]
    holdout: list[TSPInstance]
    adversarial: list[TSPInstance]
    synthetic_holdout: list[TSPInstance]


def instance_from_dict(payload: dict[str, Any]) -> TSPInstance:
    instance = TSPInstance(
        name=str(payload["name"]),
        source=str(payload.get("source", "")),
        dimension=int(payload["dimension"]),
        edge_weight_type=str(payload.get("edge_weight_type", "EUC_2D")),
        coordinates=[(float(x), float(y)) for x, y in payload["coordinates"]],
        best_known_cost=int(payload["best_known_cost"]),
        family=str(payload.get("family", payload["name"])),
        tags=list(payload.get("tags", [])),
        descriptors=dict(payload.get("descriptors", {})),
    )
    if not instance.descriptors:
        from .instance_features import ensure_instance_descriptors

        ensure_instance_descriptors(instance)
    return instance


def _read_text_maybe_gzip(path: Path) -> str:
    if path.suffix == ".gz":
        return gzip.decompress(path.read_bytes()).decode("utf-8")
    return path.read_text(encoding="utf-8")


def _split_keyword(line: str) -> tuple[str, str] | None:
    if ":" not in line:
        return None
    key, value = line.split(":", 1)
    return key.strip().upper(), value.strip()


def parse_tsplib_euc_2d(path: str | Path, *, source: str, family: str, tags: list[str]) -> TSPInstance:
    payload = _read_text_maybe_gzip(Path(path))
    lines = [line.rstrip() for line in payload.splitlines() if line.strip()]
    header: dict[str, str] = {}
    coordinates: list[tuple[float, float]] = []
    in_coords = False
    for raw_line in lines:
        line = raw_line.strip()
        if line.upper() == "NODE_COORD_SECTION":
            in_coords = True
            continue
        if line.upper() == "EOF":
            break
        if not in_coords:
            maybe = _split_keyword(line)
            if maybe is None:
                continue
            key, value = maybe
            header[key] = value
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        coordinates.append((float(parts[1]), float(parts[2])))

    edge_weight_type = str(header.get("EDGE_WEIGHT_TYPE", "")).upper()
    if edge_weight_type != "EUC_2D":
        raise ValueError(f"{Path(path).name} is {edge_weight_type}, expected EUC_2D.")
    name = str(header.get("NAME") or Path(path).stem.replace(".tsp", ""))
    dimension = int(header.get("DIMENSION", len(coordinates)))
    if dimension != len(coordinates):
        raise ValueError(f"{name} dimension mismatch: header={dimension}, coords={len(coordinates)}")
    return TSPInstance(
        name=name,
        source=source,
        dimension=dimension,
        edge_weight_type=edge_weight_type,
        coordinates=coordinates,
        best_known_cost=0,
        family=family,
        tags=tags,
    )


def parse_tsplib_tour(path: str | Path) -> list[int]:
    payload = _read_text_maybe_gzip(Path(path))
    lines = [line.strip() for line in payload.splitlines() if line.strip()]
    in_tour = False
    tour: list[int] = []
    for line in lines:
        upper = line.upper()
        if upper == "TOUR_SECTION":
            in_tour = True
            continue
        if not in_tour:
            continue
        if upper == "EOF":
            break
        for token in line.split():
            value = int(token)
            if value == -1:
                return tour
            tour.append(value - 1)
    return tour


def build_distance_matrix(instance: TSPInstance) -> list[list[int]]:
    coords = instance.coordinates
    matrix = [[0 for _ in coords] for _ in coords]
    for left_index, left in enumerate(coords):
        for right_index in range(left_index + 1, len(coords)):
            distance = tsplib_euc_2d_distance(left, coords[right_index])
            matrix[left_index][right_index] = distance
            matrix[right_index][left_index] = distance
    return matrix


def compute_tour_cost(instance: TSPInstance, tour: list[int]) -> int:
    if len(tour) != instance.dimension:
        raise ValueError(f"{instance.name} expected {instance.dimension} nodes, got {len(tour)}")
    matrix = build_distance_matrix(instance)
    total = 0
    for index, node in enumerate(tour):
        total += matrix[node][tour[(index + 1) % len(tour)]]
    return total


def summarize_instance(instance: TSPInstance) -> dict[str, Any]:
    from .instance_features import ensure_instance_descriptors, prompt_descriptor_summary

    ensure_instance_descriptors(instance)
    descriptor_summary = prompt_descriptor_summary(instance)
    return {
        "name": instance.name,
        "source": instance.source,
        "family": instance.family,
        "dimension": instance.dimension,
        "best_known_cost": instance.best_known_cost,
        "edge_weight_type": instance.edge_weight_type,
        "structure_class": descriptor_summary["structure_class"],
        "size_bucket": descriptor_summary["size_bucket"],
        "coordinate_spread_norm": descriptor_summary["coordinate_spread_norm"],
        "distance_mean_norm": descriptor_summary["distance_mean_norm"],
        "distance_std_norm": descriptor_summary["distance_std_norm"],
        "distance_cv": descriptor_summary["distance_cv"],
        "nn_distance_mean_norm": descriptor_summary["nn_distance_mean_norm"],
        "nn_distance_variance_norm": descriptor_summary["nn_distance_variance_norm"],
        "nn_distance_cv": descriptor_summary["nn_distance_cv"],
        "mst_length_norm": descriptor_summary["mst_length_norm"],
        "convex_hull_ratio": descriptor_summary["convex_hull_ratio"],
        "clusteredness_score": descriptor_summary["clusteredness_score"],
        "grid_likeness": descriptor_summary["grid_likeness"],
        "corridor_score": descriptor_summary["corridor_score"],
        "bottleneck_score": descriptor_summary["bottleneck_score"],
        "nearest_neighbor_trap_score": descriptor_summary["nearest_neighbor_trap_score"],
        "tags": list(instance.tags),
    }


def make_synthetic_instance(
    *,
    name: str,
    family: str,
    dimension: int,
    seed: int,
    source: str,
    scale: float = 1000.0,
) -> TSPInstance:
    if dimension < 8:
        raise ValueError("Synthetic instances must contain at least 8 nodes.")
    rng = _DeterministicRng(seed)
    coords: list[tuple[float, float]] = []
    normalized_family = family
    if normalized_family in {"clustered_tsp", "clustered"}:
        normalized_family = "clustered_gaussian"
    elif normalized_family in {"grid_like_tsp", "grid_like"}:
        normalized_family = "grid_outliers"
    elif normalized_family in {"elongated_tsp", "elongated", "corridor", "elongated_corridor"}:
        normalized_family = "elongated_corridor"
    elif normalized_family in {"uniform_tsp", "uniform_euclidean"}:
        normalized_family = "uniform_random"

    if normalized_family == "clustered_gaussian":
        centers = [(0.25, 0.25), (0.72, 0.28), (0.32, 0.76), (0.74, 0.74)]
        for index in range(dimension):
            cx, cy = centers[index % len(centers)]
            coords.append(
                (
                    scale * _clip(cx + rng.normal(0.0, 0.06), 0.02, 0.98),
                    scale * _clip(cy + rng.normal(0.0, 0.06), 0.02, 0.98),
                )
            )
    elif normalized_family == "ring_bridge":
        ring_count = max(6, dimension - 4)
        for index in range(ring_count):
            angle = (2.0 * math.pi * index) / ring_count
            radius = 0.33 + (0.04 * ((index % 3) - 1))
            coords.append(
                (
                    scale * (0.5 + (radius * math.cos(angle))),
                    scale * (0.5 + (radius * math.sin(angle))),
                )
            )
        coords.extend(
            [
                (scale * 0.18, scale * 0.5),
                (scale * 0.82, scale * 0.5),
                (scale * 0.5, scale * 0.18),
                (scale * 0.5, scale * 0.82),
            ]
        )
        coords = coords[:dimension]
    elif normalized_family == "grid_outliers":
        side = max(2, int(math.sqrt(dimension - 2)))
        spacing = 0.55 / max(1, side - 1)
        for row in range(side):
            for col in range(side):
                if len(coords) >= dimension - 2:
                    break
                coords.append((scale * (0.2 + (col * spacing)), scale * (0.2 + (row * spacing))))
        coords.append((scale * 0.92, scale * 0.08))
        coords.append((scale * 0.08, scale * 0.92))
        coords = coords[:dimension]
    elif normalized_family == "two_corridors":
        split = dimension // 2
        for index in range(split):
            coords.append((scale * (0.1 + (0.8 * index / max(1, split - 1))), scale * 0.3))
        for index in range(dimension - split):
            coords.append((scale * (0.9 - (0.8 * index / max(1, dimension - split - 1))), scale * 0.7))
    elif normalized_family == "uniform_random":
        for _ in range(dimension):
            coords.append((scale * rng.uniform(0.08, 0.92), scale * rng.uniform(0.08, 0.92)))
    elif normalized_family == "two_cluster_bottleneck":
        split = dimension // 2
        left_center = (0.24, 0.46)
        right_center = (0.76, 0.54)
        for index in range(split):
            jitter = 0.045 + (0.01 * (index % 2))
            coords.append(
                (
                    scale * _clip(left_center[0] + rng.normal(0.0, jitter), 0.04, 0.48),
                    scale * _clip(left_center[1] + rng.normal(0.0, jitter), 0.16, 0.78),
                )
            )
        for index in range(dimension - split - 2):
            jitter = 0.045 + (0.01 * (index % 3))
            coords.append(
                (
                    scale * _clip(right_center[0] + rng.normal(0.0, jitter), 0.52, 0.96),
                    scale * _clip(right_center[1] + rng.normal(0.0, jitter), 0.18, 0.82),
                )
            )
        coords.extend(
            [
                (scale * 0.49, scale * 0.47),
                (scale * 0.53, scale * 0.55),
            ]
        )
        coords = coords[:dimension]
    elif normalized_family == "elongated_corridor":
        for index in range(dimension):
            x_value = 0.06 + (0.88 * index / max(1, dimension - 1))
            centerline = 0.5 + (0.08 * math.sin((2.0 * math.pi * index) / max(3, dimension - 1)))
            y_value = centerline + rng.normal(0.0, 0.03)
            coords.append((scale * x_value, scale * _clip(y_value, 0.18, 0.82)))
    elif normalized_family == "nearest_neighbor_trap":
        lane_count = max(4, dimension // 2)
        top_row = min(lane_count, dimension)
        bottom_row = max(0, dimension - top_row)
        for index in range(top_row):
            x_value = 0.1 + (0.78 * index / max(1, top_row - 1))
            y_value = 0.28 + (0.02 * ((index % 2) - 0.5))
            coords.append((scale * x_value, scale * y_value))
        for index in range(bottom_row):
            x_value = 0.88 - (0.78 * index / max(1, bottom_row - 1))
            y_value = 0.72 + (0.02 * (((index + 1) % 2) - 0.5))
            coords.append((scale * x_value, scale * y_value))
        if len(coords) >= 4:
            coords[1] = (scale * 0.22, scale * 0.44)
            coords[-2] = (scale * 0.78, scale * 0.56)
    else:
        raise ValueError(f"Unsupported synthetic family: {family}")

    instance = TSPInstance(
        name=name,
        source=source,
        dimension=len(coords),
        edge_weight_type="EUC_2D",
        coordinates=coords,
        best_known_cost=0,
        family=family,
        tags=["synthetic", family, normalized_family],
    )
    instance.best_known_cost = exact_tsp_optimum(instance)
    from .instance_features import ensure_instance_descriptors

    ensure_instance_descriptors(instance)
    return instance


def exact_tsp_optimum(instance: TSPInstance) -> int:
    if instance.dimension > 18:
        raise ValueError(f"Exact TSP optimum is only supported up to 18 nodes, got {instance.dimension}")
    matrix = build_distance_matrix(instance)
    n = instance.dimension
    table: dict[tuple[int, int], int] = {}
    for node in range(1, n):
        table[(1 << node, node)] = matrix[0][node]

    for subset_size in range(2, n):
        next_table: dict[tuple[int, int], int] = {}
        for mask in _subsets(range(1, n), subset_size):
            for last in _members(mask, n):
                previous_mask = mask ^ (1 << last)
                best = min(
                    table[(previous_mask, previous)] + matrix[previous][last]
                    for previous in _members(previous_mask, n)
                )
                next_table[(mask, last)] = best
        table = next_table

    full_mask = ((1 << n) - 1) ^ 1
    return min(table[(full_mask, last)] + matrix[last][0] for last in range(1, n))


def load_benchmark_bundle(manifest_path: str | Path) -> BenchmarkBundle:
    manifest_path = Path(manifest_path)
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent
    return BenchmarkBundle(
        train=_load_manifest_group(root, raw.get("train", [])),
        holdout=_load_manifest_group(root, raw.get("holdout", [])),
        adversarial=_load_manifest_group(root, raw.get("adversarial", [])),
        synthetic_holdout=_load_manifest_group(root, raw.get("synthetic_holdout", [])),
    )


def _load_manifest_group(root: Path, group: list[dict[str, Any]]) -> list[TSPInstance]:
    instances: list[TSPInstance] = []
    for item in group:
        kind = str(item.get("kind", "tsplib"))
        if kind == "tsplib":
            instance = parse_tsplib_euc_2d(
                root / str(item["problem_path"]),
                source=str(item.get("source", "TSPLIB95")),
                family=str(item.get("family", item["name"])),
                tags=list(item.get("tags", ["tsplib95"])),
            )
            instance.best_known_cost = int(item["best_known_cost"])
            instance.descriptors = dict(item.get("descriptors", {}))
            if not instance.descriptors:
                from .instance_features import ensure_instance_descriptors

                ensure_instance_descriptors(instance)
            instances.append(instance)
            continue
        if kind == "synthetic":
            instance = make_synthetic_instance(
                name=str(item["name"]),
                family=str(item["family"]),
                dimension=int(item["dimension"]),
                seed=int(item["seed"]),
                source=str(item.get("source", "synthetic")),
                scale=float(item.get("scale", 1000.0)),
            )
            instance.descriptors = dict(item.get("descriptors", instance.descriptors or {}))
            instances.append(instance)
            continue
        raise ValueError(f"Unsupported manifest kind: {kind}")
    return instances


def _clip(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _members(mask: int, n: int) -> list[int]:
    return [index for index in range(1, n) if mask & (1 << index)]


def _subsets(nodes: range, subset_size: int) -> list[int]:
    masks: list[int] = []
    values = list(nodes)
    stack: list[tuple[int, int, int]] = [(0, 0, 0)]
    while stack:
        index, chosen, mask = stack.pop()
        if chosen == subset_size:
            masks.append(mask)
            continue
        if index >= len(values):
            continue
        remaining = len(values) - index
        if chosen + remaining < subset_size:
            continue
        stack.append((index + 1, chosen, mask))
        stack.append((index + 1, chosen + 1, mask | (1 << values[index])))
    return masks


class _DeterministicRng:
    def __init__(self, seed: int) -> None:
        self.state = int(seed) & 0x7FFFFFFF

    def _next(self) -> float:
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state / 0x7FFFFFFF

    def uniform(self, lower: float, upper: float) -> float:
        return lower + ((upper - lower) * self._next())

    def normal(self, mean: float, sigma: float) -> float:
        left = max(1e-9, self._next())
        right = self._next()
        z = math.sqrt(-2.0 * math.log(left)) * math.cos(2.0 * math.pi * right)
        return mean + (sigma * z)
