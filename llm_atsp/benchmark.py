from __future__ import annotations

from dataclasses import dataclass
import gzip
import json
import math
from pathlib import Path
from typing import Any


@dataclass
class ATSPInstance:
    name: str
    source: str
    dimension: int
    edge_weight_type: str
    distance_matrix: list[list[int]]
    best_known_cost: int
    family: str
    tags: list[str]
    coordinates: list[tuple[float, float]] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "dimension": self.dimension,
            "edge_weight_type": self.edge_weight_type,
            "distance_matrix": [list(row) for row in self.distance_matrix],
            "best_known_cost": int(self.best_known_cost),
            "family": self.family,
            "tags": list(self.tags),
            "coordinates": (
                [[float(x), float(y)] for x, y in self.coordinates]
                if self.coordinates is not None
                else None
            ),
        }


@dataclass
class BenchmarkBundle:
    train: list[ATSPInstance]
    holdout: list[ATSPInstance]
    adversarial: list[ATSPInstance]
    synthetic_holdout: list[ATSPInstance]


def instance_from_dict(payload: dict[str, Any]) -> ATSPInstance:
    coordinates_payload = payload.get("coordinates")
    return ATSPInstance(
        name=str(payload["name"]),
        source=str(payload.get("source", "")),
        dimension=int(payload["dimension"]),
        edge_weight_type=str(payload.get("edge_weight_type", "EXPLICIT")),
        distance_matrix=[list(map(int, row)) for row in payload["distance_matrix"]],
        best_known_cost=int(payload["best_known_cost"]),
        family=str(payload.get("family", payload["name"])),
        tags=list(payload.get("tags", [])),
        coordinates=(
            [(float(x), float(y)) for x, y in coordinates_payload]
            if coordinates_payload is not None
            else None
        ),
    )


def _read_text_maybe_gzip(path: Path) -> str:
    if path.suffix == ".gz":
        return gzip.decompress(path.read_bytes()).decode("utf-8")
    return path.read_text(encoding="utf-8")


def _split_keyword(line: str) -> tuple[str, str] | None:
    if ":" not in line:
        return None
    key, value = line.split(":", 1)
    return key.strip().upper(), value.strip()


def parse_tsplib_atsp(path: str | Path, *, source: str, family: str, tags: list[str]) -> ATSPInstance:
    payload = _read_text_maybe_gzip(Path(path))
    lines = [line.rstrip() for line in payload.splitlines() if line.strip()]
    header: dict[str, str] = {}
    edge_values: list[int] = []
    in_weights = False
    for raw_line in lines:
        line = raw_line.strip()
        upper = line.upper()
        if upper == "EDGE_WEIGHT_SECTION":
            in_weights = True
            continue
        if upper == "EOF":
            break
        if not in_weights:
            maybe = _split_keyword(line)
            if maybe is None:
                continue
            key, value = maybe
            header[key] = value
            continue
        edge_values.extend(int(token) for token in line.split())

    edge_weight_type = str(header.get("EDGE_WEIGHT_TYPE", "EXPLICIT")).upper()
    edge_weight_format = str(header.get("EDGE_WEIGHT_FORMAT", "FULL_MATRIX")).upper()
    if edge_weight_type != "EXPLICIT":
        raise ValueError(f"{Path(path).name} is {edge_weight_type}, expected EXPLICIT.")
    if edge_weight_format != "FULL_MATRIX":
        raise ValueError(f"{Path(path).name} uses {edge_weight_format}, expected FULL_MATRIX.")
    name = str(header.get("NAME") or Path(path).stem.replace(".atsp", ""))
    dimension = int(header["DIMENSION"])
    expected_values = dimension * dimension
    if len(edge_values) != expected_values:
        raise ValueError(f"{name} matrix mismatch: expected {expected_values} values, got {len(edge_values)}")
    matrix = [
        edge_values[(row_index * dimension) : ((row_index + 1) * dimension)]
        for row_index in range(dimension)
    ]
    return ATSPInstance(
        name=name,
        source=source,
        dimension=dimension,
        edge_weight_type=edge_weight_type,
        distance_matrix=matrix,
        best_known_cost=0,
        family=family,
        tags=tags,
        coordinates=None,
    )


def compute_tour_cost(instance: ATSPInstance, tour: list[int]) -> int:
    if len(tour) != instance.dimension:
        raise ValueError(f"{instance.name} expected {instance.dimension} nodes, got {len(tour)}")
    total = 0
    matrix = instance.distance_matrix
    for index, node in enumerate(tour):
        total += matrix[node][tour[(index + 1) % len(tour)]]
    return total


def summarize_instance(instance: ATSPInstance) -> dict[str, Any]:
    asymmetry = _asymmetry_ratio(instance.distance_matrix)
    payload = {
        "name": instance.name,
        "source": instance.source,
        "family": instance.family,
        "dimension": instance.dimension,
        "best_known_cost": instance.best_known_cost,
        "edge_weight_type": instance.edge_weight_type,
        "asymmetry_ratio": round(asymmetry, 6),
        "tags": list(instance.tags),
    }
    if instance.coordinates:
        xs = [point[0] for point in instance.coordinates]
        ys = [point[1] for point in instance.coordinates]
        span_x = max(xs) - min(xs) if xs else 0.0
        span_y = max(ys) - min(ys) if ys else 0.0
        payload["aspect_ratio"] = round((max(span_x, span_y) / max(1.0, min(span_x, span_y) or 1.0)), 4)
    return payload


def make_synthetic_instance(
    *,
    name: str,
    family: str,
    dimension: int,
    seed: int,
    source: str,
    scale: float = 1000.0,
) -> ATSPInstance:
    if dimension < 8:
        raise ValueError("Synthetic ATSP instances must contain at least 8 nodes.")
    coords = _synthetic_coordinates(family, dimension, seed=seed, scale=scale)
    matrix = _directed_matrix_from_coordinates(coords, family=family, seed=seed)
    instance = ATSPInstance(
        name=name,
        source=source,
        dimension=len(coords),
        edge_weight_type="EXPLICIT",
        distance_matrix=matrix,
        best_known_cost=0,
        family=family,
        tags=["synthetic", family],
        coordinates=coords,
    )
    instance.best_known_cost = exact_atsp_optimum(instance)
    return instance


def exact_atsp_optimum(instance: ATSPInstance) -> int:
    if instance.dimension > 18:
        raise ValueError(f"Exact ATSP optimum is only supported up to 18 nodes, got {instance.dimension}")
    matrix = instance.distance_matrix
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


def _load_manifest_group(root: Path, group: list[dict[str, Any]]) -> list[ATSPInstance]:
    instances: list[ATSPInstance] = []
    for item in group:
        kind = str(item.get("kind", "tsplib"))
        if kind == "tsplib":
            instance = parse_tsplib_atsp(
                root / str(item["problem_path"]),
                source=str(item.get("source", "TSPLIB95")),
                family=str(item.get("family", item["name"])),
                tags=list(item.get("tags", ["tsplib95", "atsp"])),
            )
            instance.best_known_cost = int(item["best_known_cost"])
            instances.append(instance)
            continue
        if kind == "synthetic":
            instances.append(
                make_synthetic_instance(
                    name=str(item["name"]),
                    family=str(item["family"]),
                    dimension=int(item["dimension"]),
                    seed=int(item["seed"]),
                    source=str(item.get("source", "synthetic")),
                    scale=float(item.get("scale", 1000.0)),
                )
            )
            continue
        raise ValueError(f"Unsupported manifest kind: {kind}")
    return instances


def _synthetic_coordinates(family: str, dimension: int, *, seed: int, scale: float) -> list[tuple[float, float]]:
    rng = _DeterministicRng(seed)
    coords: list[tuple[float, float]] = []
    if family == "wind_clusters":
        centers = [(0.18, 0.24), (0.7, 0.2), (0.28, 0.76), (0.78, 0.72)]
        for index in range(dimension):
            cx, cy = centers[index % len(centers)]
            coords.append(
                (
                    scale * _clip(cx + rng.normal(0.0, 0.055), 0.02, 0.98),
                    scale * _clip(cy + rng.normal(0.0, 0.055), 0.02, 0.98),
                )
            )
    elif family == "clockwise_ring":
        for index in range(dimension):
            angle = (2.0 * math.pi * index) / dimension
            radius = 0.34 + (0.05 * ((index % 4) - 1.5))
            coords.append(
                (
                    scale * (0.5 + (radius * math.cos(angle))),
                    scale * (0.5 + (radius * math.sin(angle))),
                )
            )
    elif family == "corridor_drift":
        split = max(3, dimension // 2)
        for index in range(split):
            coords.append((scale * (0.1 + (0.8 * index / max(1, split - 1))), scale * 0.28))
        for index in range(dimension - split):
            coords.append((scale * (0.9 - (0.8 * index / max(1, dimension - split - 1))), scale * 0.72))
    elif family == "hub_spokes":
        hub_count = max(2, dimension // 4)
        coords.extend(
            [
                (scale * 0.5, scale * 0.5),
                (scale * 0.46, scale * 0.54),
            ][:hub_count]
        )
        remaining = dimension - len(coords)
        for index in range(remaining):
            angle = (2.0 * math.pi * index) / max(1, remaining)
            radius = 0.18 if index % 3 == 0 else 0.4
            coords.append(
                (
                    scale * (0.5 + (radius * math.cos(angle))),
                    scale * (0.5 + (radius * math.sin(angle))),
                )
            )
    else:
        raise ValueError(f"Unsupported synthetic ATSP family: {family}")
    return coords[:dimension]


def _directed_matrix_from_coordinates(
    coordinates: list[tuple[float, float]],
    *,
    family: str,
    seed: int,
) -> list[list[int]]:
    n = len(coordinates)
    center_x = sum(point[0] for point in coordinates) / max(1, n)
    center_y = sum(point[1] for point in coordinates) / max(1, n)
    rng = _DeterministicRng(seed + 17)
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    for left_index, left in enumerate(coordinates):
        for right_index, right in enumerate(coordinates):
            if left_index == right_index:
                continue
            dx = right[0] - left[0]
            dy = right[1] - left[1]
            euclidean = math.sqrt((dx * dx) + (dy * dy))
            scale = 1.0
            if family == "wind_clusters":
                wind = ((0.96 + (0.05 * rng._next())), 0.28)
                norm = math.sqrt((dx * dx) + (dy * dy)) or 1.0
                directional = max(-1.0, min(1.0, ((dx * wind[0]) + (dy * wind[1])) / norm))
                scale += 0.22 * directional
            elif family == "clockwise_ring":
                left_angle = math.atan2(left[1] - center_y, left[0] - center_x)
                right_angle = math.atan2(right[1] - center_y, right[0] - center_x)
                delta = ((right_angle - left_angle) + (2.0 * math.pi)) % (2.0 * math.pi)
                clockwise_progress = 1.0 - abs(delta - math.pi) / math.pi
                scale += 0.18 * clockwise_progress
                if delta < math.pi:
                    scale -= 0.12
            elif family == "corridor_drift":
                same_lane = abs(left[1] - right[1]) < 120.0
                if same_lane:
                    scale += 0.16 * (1.0 if dx < 0 else -0.08)
                else:
                    scale += 0.12 * (1.0 if dy > 0 else -0.05)
            elif family == "hub_spokes":
                left_radius = math.dist(left, (center_x, center_y))
                right_radius = math.dist(right, (center_x, center_y))
                if right_radius < left_radius:
                    scale -= 0.14
                else:
                    scale += 0.18
            value = max(1, int((euclidean * max(0.45, scale)) + 0.5))
            matrix[left_index][right_index] = value
    return matrix


def _asymmetry_ratio(matrix: list[list[int]]) -> float:
    if len(matrix) <= 1:
        return 0.0
    values: list[float] = []
    for left in range(len(matrix)):
        for right in range(left + 1, len(matrix)):
            forward = float(matrix[left][right])
            backward = float(matrix[right][left])
            values.append(abs(forward - backward) / max(1.0, (forward + backward) * 0.5))
    return sum(values) / max(1, len(values))


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

    def normal(self, mean: float, sigma: float) -> float:
        left = max(1e-9, self._next())
        right = self._next()
        gaussian = math.sqrt(-2.0 * math.log(left)) * math.cos(2.0 * math.pi * right)
        return mean + (sigma * gaussian)
