from __future__ import annotations

from dataclasses import dataclass
import gzip
import json
import math
from pathlib import Path
import re
from typing import Any


def tsplib_euc_2d_distance(left: tuple[float, float], right: tuple[float, float]) -> int:
    dx = float(left[0]) - float(right[0])
    dy = float(left[1]) - float(right[1])
    return int(math.sqrt((dx * dx) + (dy * dy)) + 0.5)


@dataclass
class CVRPInstance:
    name: str
    source: str
    dimension: int
    edge_weight_type: str
    coordinates: list[tuple[float, float]]
    demands: list[int]
    capacity: int
    depot_index: int
    best_known_cost: int
    family: str
    tags: list[str]
    vehicle_count_hint: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "dimension": self.dimension,
            "edge_weight_type": self.edge_weight_type,
            "coordinates": [[float(x), float(y)] for x, y in self.coordinates],
            "demands": [int(value) for value in self.demands],
            "capacity": int(self.capacity),
            "depot_index": int(self.depot_index),
            "best_known_cost": int(self.best_known_cost),
            "family": self.family,
            "tags": list(self.tags),
            "vehicle_count_hint": int(self.vehicle_count_hint) if self.vehicle_count_hint is not None else None,
        }


@dataclass
class BenchmarkBundle:
    train: list[CVRPInstance]
    holdout: list[CVRPInstance]
    adversarial: list[CVRPInstance]
    synthetic_holdout: list[CVRPInstance]


def instance_from_dict(payload: dict[str, Any]) -> CVRPInstance:
    return CVRPInstance(
        name=str(payload["name"]),
        source=str(payload.get("source", "")),
        dimension=int(payload["dimension"]),
        edge_weight_type=str(payload.get("edge_weight_type", "EUC_2D")),
        coordinates=[(float(x), float(y)) for x, y in payload["coordinates"]],
        demands=[int(value) for value in payload["demands"]],
        capacity=int(payload["capacity"]),
        depot_index=int(payload.get("depot_index", 0)),
        best_known_cost=int(payload["best_known_cost"]),
        family=str(payload.get("family", payload["name"])),
        tags=list(payload.get("tags", [])),
        vehicle_count_hint=(
            int(payload["vehicle_count_hint"])
            if payload.get("vehicle_count_hint") is not None
            else None
        ),
    )


def _read_text_maybe_gzip(path: Path) -> str:
    if path.suffix == ".gz":
        return gzip.decompress(path.read_bytes()).decode("utf-8")
    return path.read_text(encoding="utf-8")


def parse_cvrplib_instance(
    path: str | Path,
    *,
    source: str,
    family: str,
    tags: list[str],
    vehicle_count_hint: int | None = None,
) -> CVRPInstance:
    payload = _read_text_maybe_gzip(Path(path))
    name = _extract_header_value(payload, "NAME") or Path(path).stem.replace(".vrp", "")
    edge_weight_type = (_extract_header_value(payload, "EDGE_WEIGHT_TYPE") or "EUC_2D").upper()
    if edge_weight_type != "EUC_2D":
        raise ValueError(f"{Path(path).name} is {edge_weight_type}, expected EUC_2D.")
    dimension = int(_extract_header_value(payload, "DIMENSION") or "0")
    capacity = int(_extract_header_value(payload, "CAPACITY") or "0")
    coord_tokens = _section_tokens(payload, "NODE_COORD_SECTION", "DEMAND_SECTION")
    demand_tokens = _section_tokens(payload, "DEMAND_SECTION", "DEPOT_SECTION")
    depot_tokens = _section_tokens(payload, "DEPOT_SECTION", "EOF")

    if len(coord_tokens) < 3 * dimension:
        raise ValueError(f"{name} coordinate section is incomplete.")
    coordinates = [(0.0, 0.0) for _ in range(dimension)]
    for index in range(dimension):
        base = 3 * index
        node = int(coord_tokens[base]) - 1
        coordinates[node] = (float(coord_tokens[base + 1]), float(coord_tokens[base + 2]))

    if len(demand_tokens) < 2 * dimension:
        raise ValueError(f"{name} demand section is incomplete.")
    demands = [0 for _ in range(dimension)]
    for index in range(dimension):
        base = 2 * index
        node = int(demand_tokens[base]) - 1
        demands[node] = int(demand_tokens[base + 1])

    depot_values = [int(token) for token in depot_tokens if token]
    if -1 not in depot_values:
        raise ValueError(f"{name} depot section is missing the terminating -1 marker.")
    depot_candidates = [value - 1 for value in depot_values if value > 0]
    if not depot_candidates:
        raise ValueError(f"{name} depot section did not define a depot.")
    depot_index = depot_candidates[0]
    hint = vehicle_count_hint if vehicle_count_hint is not None else _vehicle_hint_from_name(name)
    return CVRPInstance(
        name=name,
        source=source,
        dimension=dimension,
        edge_weight_type=edge_weight_type,
        coordinates=coordinates,
        demands=demands,
        capacity=capacity,
        depot_index=depot_index,
        best_known_cost=0,
        family=family,
        tags=tags,
        vehicle_count_hint=hint,
    )


def parse_cvrplib_solution(path: str | Path) -> tuple[list[list[int]], int]:
    payload = _read_text_maybe_gzip(Path(path))
    routes = [
        [int(token) for token in match.group(1).split() if token.strip()]
        for match in re.finditer(r"Route\s*#\d+\s*:\s*([0-9 ]+)", payload, flags=re.IGNORECASE)
    ]
    cost_match = re.search(r"Cost\s+([0-9]+(?:\.[0-9]+)?)", payload, flags=re.IGNORECASE)
    if cost_match is None:
        raise ValueError(f"{Path(path).name} did not contain a final cost.")
    return routes, int(round(float(cost_match.group(1))))


def build_distance_matrix(instance: CVRPInstance) -> list[list[int]]:
    coords = instance.coordinates
    matrix = [[0 for _ in coords] for _ in coords]
    for left_index, left in enumerate(coords):
        for right_index in range(left_index + 1, len(coords)):
            distance = tsplib_euc_2d_distance(left, coords[right_index])
            matrix[left_index][right_index] = distance
            matrix[right_index][left_index] = distance
    return matrix


def compute_route_cost(instance: CVRPInstance, route: list[int]) -> int:
    matrix = build_distance_matrix(instance)
    return _route_cost_from_matrix(matrix, instance.depot_index, route)


def compute_solution_cost(instance: CVRPInstance, routes: list[list[int]]) -> int:
    matrix = build_distance_matrix(instance)
    seen: set[int] = set()
    total = 0
    for route in routes:
        load = sum(instance.demands[node] for node in route)
        if load > instance.capacity:
            raise ValueError(f"{instance.name} route exceeds capacity: {load} > {instance.capacity}")
        total += _route_cost_from_matrix(matrix, instance.depot_index, route)
        for node in route:
            if node == instance.depot_index:
                raise ValueError("Routes must not explicitly include the depot.")
            if node in seen:
                raise ValueError(f"Customer {node + 1} appears more than once in the solution.")
            seen.add(node)
    customers = {node for node in range(instance.dimension) if node != instance.depot_index}
    if seen != customers:
        missing = sorted((customers - seen))
        raise ValueError(f"Missing customers in solution: {[node + 1 for node in missing]}")
    return total


def summarize_instance(instance: CVRPInstance) -> dict[str, Any]:
    xs = [point[0] for point in instance.coordinates]
    ys = [point[1] for point in instance.coordinates]
    span_x = max(xs) - min(xs) if xs else 0.0
    span_y = max(ys) - min(ys) if ys else 0.0
    total_demand = sum(instance.demands[node] for node in range(instance.dimension) if node != instance.depot_index)
    demand_pressure = total_demand / max(1, instance.capacity)
    return {
        "name": instance.name,
        "source": instance.source,
        "family": instance.family,
        "dimension": instance.dimension,
        "customer_count": instance.dimension - 1,
        "best_known_cost": instance.best_known_cost,
        "edge_weight_type": instance.edge_weight_type,
        "capacity": instance.capacity,
        "vehicle_count_hint": instance.vehicle_count_hint,
        "demand_pressure": round(demand_pressure, 4),
        "aspect_ratio": round((max(span_x, span_y) / max(1.0, min(span_x, span_y) or 1.0)), 4),
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
) -> CVRPInstance:
    if dimension < 8:
        raise ValueError("Synthetic CVRP instances must contain at least 8 nodes including the depot.")
    depot, customers = _synthetic_customer_layout(family, dimension=dimension, seed=seed, scale=scale)
    demands = _synthetic_demands(family, customer_count=len(customers), seed=seed)
    route_hint = 3 if len(customers) <= 9 else 4
    total_demand = sum(demands)
    capacity = max(max(demands), int(math.ceil(total_demand / route_hint)))
    capacity = max(capacity, int(math.ceil(total_demand / route_hint * 1.08)))
    coordinates = [depot] + customers
    instance = CVRPInstance(
        name=name,
        source=source,
        dimension=len(coordinates),
        edge_weight_type="EUC_2D",
        coordinates=coordinates,
        demands=[0] + demands,
        capacity=capacity,
        depot_index=0,
        best_known_cost=0,
        family=family,
        tags=["synthetic", family],
        vehicle_count_hint=route_hint,
    )
    instance.best_known_cost = exact_cvrp_optimum(instance)
    return instance


def exact_cvrp_optimum(instance: CVRPInstance) -> int:
    customer_count = instance.dimension - 1
    if customer_count > 11:
        raise ValueError(f"Exact CVRP optimum is only supported up to 11 customers, got {customer_count}")
    matrix = build_distance_matrix(instance)
    customers = [node for node in range(instance.dimension) if node != instance.depot_index]
    customer_to_bit = {node: bit for bit, node in enumerate(customers)}
    route_costs: dict[int, int] = {}
    subset_demands: dict[int, int] = {}
    for mask in range(1, 1 << customer_count):
        demand = sum(instance.demands[customers[bit]] for bit in range(customer_count) if mask & (1 << bit))
        subset_demands[mask] = demand
        if demand <= instance.capacity:
            route_costs[mask] = _exact_subset_route_cost(matrix, instance.depot_index, customers, mask)

    memo: dict[int, int] = {0: 0}

    def solve(mask: int) -> int:
        if mask in memo:
            return memo[mask]
        best = 10**18
        first_bit = mask & -mask
        submask = mask
        while submask:
            if submask & first_bit and submask in route_costs:
                best = min(best, route_costs[submask] + solve(mask ^ submask))
            submask = (submask - 1) & mask
        memo[mask] = int(best)
        return memo[mask]

    full_mask = (1 << customer_count) - 1
    return solve(full_mask)


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


def _load_manifest_group(root: Path, group: list[dict[str, Any]]) -> list[CVRPInstance]:
    instances: list[CVRPInstance] = []
    for item in group:
        kind = str(item.get("kind", "cvrplib"))
        if kind == "cvrplib":
            instance = parse_cvrplib_instance(
                root / str(item["problem_path"]),
                source=str(item.get("source", "CVRPLIB")),
                family=str(item.get("family", item["name"])),
                tags=list(item.get("tags", ["cvrplib", "euc_2d"])),
                vehicle_count_hint=(
                    int(item["vehicle_count_hint"])
                    if item.get("vehicle_count_hint") is not None
                    else None
                ),
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


def _extract_header_value(payload: str, key: str) -> str | None:
    match = re.search(rf"{re.escape(key)}\s*:\s*([^\n\r]+)", payload, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None


def _section_tokens(payload: str, start_marker: str, end_marker: str) -> list[str]:
    match = re.search(
        rf"{re.escape(start_marker)}\s*(.*?)\s*{re.escape(end_marker)}",
        payload,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match is None:
        return []
    return match.group(1).split()


def _vehicle_hint_from_name(name: str) -> int | None:
    match = re.search(r"-k(\d+)", name, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _synthetic_customer_layout(
    family: str,
    *,
    dimension: int,
    seed: int,
    scale: float,
) -> tuple[tuple[float, float], list[tuple[float, float]]]:
    customer_count = dimension - 1
    rng = _DeterministicRng(seed)
    depot = (scale * 0.5, scale * 0.5)
    customers: list[tuple[float, float]] = []
    if family == "clustered_demand":
        centers = [(0.18, 0.24), (0.76, 0.22), (0.24, 0.78), (0.78, 0.76)]
        for index in range(customer_count):
            cx, cy = centers[index % len(centers)]
            customers.append(
                (
                    scale * _clip(cx + rng.normal(0.0, 0.055), 0.03, 0.97),
                    scale * _clip(cy + rng.normal(0.0, 0.055), 0.03, 0.97),
                )
            )
    elif family == "corridor_split":
        split = max(3, customer_count // 2)
        for index in range(split):
            customers.append((scale * (0.12 + (0.76 * index / max(1, split - 1))), scale * 0.3))
        for index in range(customer_count - split):
            customers.append((scale * (0.88 - (0.76 * index / max(1, customer_count - split - 1))), scale * 0.72))
    elif family == "radial_heavy":
        for index in range(customer_count):
            angle = (2.0 * math.pi * index) / customer_count
            radius = 0.22 if index % 3 == 0 else 0.42
            customers.append(
                (
                    scale * (0.5 + (radius * math.cos(angle))),
                    scale * (0.5 + (radius * math.sin(angle))),
                )
            )
    elif family == "alternating_belt":
        for index in range(customer_count):
            x = 0.12 + (0.76 * index / max(1, customer_count - 1))
            y = 0.32 if index % 2 == 0 else 0.68
            customers.append((scale * x, scale * y))
    else:
        raise ValueError(f"Unsupported synthetic CVRP family: {family}")
    return depot, customers[:customer_count]


def _synthetic_demands(family: str, *, customer_count: int, seed: int) -> list[int]:
    rng = _DeterministicRng(seed + 41)
    demands: list[int] = []
    if family == "clustered_demand":
        for index in range(customer_count):
            base = 7 if index % 4 == 0 else 4
            demands.append(base + int(4 * rng._next()))
    elif family == "corridor_split":
        for index in range(customer_count):
            demands.append(3 + (index % 5) + int(2 * rng._next()))
    elif family == "radial_heavy":
        for index in range(customer_count):
            demands.append((8 if index % 3 == 0 else 3) + int(2 * rng._next()))
    else:
        for index in range(customer_count):
            demands.append((6 if index % 2 == 0 else 4) + int(2 * rng._next()))
    return demands


def _exact_subset_route_cost(
    matrix: list[list[int]],
    depot_index: int,
    customers: list[int],
    mask: int,
) -> int:
    subset_nodes = [customers[bit] for bit in range(len(customers)) if mask & (1 << bit)]
    if len(subset_nodes) == 1:
        customer = subset_nodes[0]
        return matrix[depot_index][customer] + matrix[customer][depot_index]

    local_index = {node: idx for idx, node in enumerate(subset_nodes)}
    n = len(subset_nodes)
    table: dict[tuple[int, int], int] = {}
    for idx, node in enumerate(subset_nodes):
        table[(1 << idx, idx)] = matrix[depot_index][node]

    for subset_size in range(2, n + 1):
        next_table: dict[tuple[int, int], int] = {}
        for submask in _local_subsets(n, subset_size):
            for last in range(n):
                if not (submask & (1 << last)):
                    continue
                previous_mask = submask ^ (1 << last)
                if previous_mask == 0:
                    next_table[(submask, last)] = matrix[depot_index][subset_nodes[last]]
                    continue
                next_table[(submask, last)] = min(
                    table[(previous_mask, previous)] + matrix[subset_nodes[previous]][subset_nodes[last]]
                    for previous in range(n)
                    if previous_mask & (1 << previous)
                )
        table = next_table

    full_mask = (1 << n) - 1
    return min(table[(full_mask, last)] + matrix[subset_nodes[last]][depot_index] for last in range(n))


def _local_subsets(n: int, subset_size: int) -> list[int]:
    masks: list[int] = []
    stack: list[tuple[int, int, int]] = [(0, 0, 0)]
    while stack:
        index, chosen, mask = stack.pop()
        if chosen == subset_size:
            masks.append(mask)
            continue
        if index >= n:
            continue
        remaining = n - index
        if chosen + remaining < subset_size:
            continue
        stack.append((index + 1, chosen, mask))
        stack.append((index + 1, chosen + 1, mask | (1 << index)))
    return masks


def _route_cost_from_matrix(matrix: list[list[int]], depot_index: int, route: list[int]) -> int:
    if not route:
        return 0
    total = matrix[depot_index][route[0]]
    for index in range(len(route) - 1):
        total += matrix[route[index]][route[index + 1]]
    total += matrix[route[-1]][depot_index]
    return total


def _clip(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


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
