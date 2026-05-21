from __future__ import annotations

import math
from typing import Any

from llm_cvrp.benchmark import CVRPInstance, build_distance_matrix


def describe_instance(instance: CVRPInstance) -> dict[str, Any]:
    matrix = build_distance_matrix(instance)
    customers = [node for node in range(instance.dimension) if node != instance.depot_index]
    xs = [instance.coordinates[node][0] for node in customers]
    ys = [instance.coordinates[node][1] for node in customers]
    span_x = (max(xs) - min(xs)) if xs else 0.0
    span_y = (max(ys) - min(ys)) if ys else 0.0
    bbox_diag = math.sqrt((span_x * span_x) + (span_y * span_y)) or 1.0
    pair_distances = [
        float(matrix[left][right])
        for index, left in enumerate(customers)
        for right in customers[index + 1 :]
    ]
    mean_pair_distance = (sum(pair_distances) / len(pair_distances)) if pair_distances else 1.0
    nn_distances = []
    for node in customers:
        neighbors = [matrix[node][other] for other in customers if other != node]
        nn_distances.append(float(min(neighbors)) if neighbors else 0.0)
    nn_mean = (sum(nn_distances) / len(nn_distances)) if nn_distances else 0.0
    nn_std = _std(nn_distances, nn_mean)
    demand_values = [float(instance.demands[node]) for node in customers]
    demand_mean = (sum(demand_values) / len(demand_values)) if demand_values else 0.0
    demand_std = _std(demand_values, demand_mean)
    total_demand = sum(demand_values)
    vehicle_hint = max(1, int(instance.vehicle_count_hint or 1))
    demand_pressure = total_demand / max(1.0, float(vehicle_hint * instance.capacity))
    aspect_ratio = max(span_x, span_y) / max(1.0, min(span_x, span_y) or 1.0)
    corridor_score = max(0.0, min(1.0, (aspect_ratio - 1.0) / max(1.0, aspect_ratio)))
    grid_likeness = _grid_likeness([instance.coordinates[node] for node in customers])
    clusteredness = max(0.0, min(1.0, 1.0 - (nn_mean / max(1.0, mean_pair_distance))))
    bottleneck_score = max(0.0, min(1.0, 1.0 - (2.0 * nn_mean / max(1.0, mean_pair_distance))))
    trap_score = max(0.0, min(1.0, nn_std / max(1.0, mean_pair_distance)))
    structure_class = _structure_class(
        corridor_score=corridor_score,
        grid_likeness=grid_likeness,
        clusteredness=clusteredness,
        bottleneck_score=bottleneck_score,
    )
    max_coord = max([abs(value) for point in instance.coordinates for value in point] or [1.0])
    return {
        "customer_count": len(customers),
        "vehicle_count_hint": vehicle_hint,
        "capacity": int(instance.capacity),
        "route_size_hint": round(len(customers) / max(1.0, float(vehicle_hint)), 6),
        "demand_pressure": round(demand_pressure, 6),
        "demand_mean_norm": round(demand_mean / max(1.0, float(instance.capacity)), 6),
        "demand_cv": round(demand_std / max(1.0, demand_mean), 6),
        "demand_max_norm": round((max(demand_values) if demand_values else 0.0) / max(1.0, float(instance.capacity)), 6),
        "coordinate_spread_norm": round(min(1.0, bbox_diag / max(1.0, max_coord * 1.5)), 6),
        "aspect_ratio": round(aspect_ratio, 6),
        "corridor_score": round(corridor_score, 6),
        "grid_likeness": round(grid_likeness, 6),
        "clusteredness_score": round(clusteredness, 6),
        "bottleneck_score": round(bottleneck_score, 6),
        "nearest_neighbor_trap_score": round(trap_score, 6),
        "nn_distance_mean_norm": round(nn_mean / max(1.0, bbox_diag), 6),
        "nn_distance_cv": round(nn_std / max(1.0, nn_mean), 6),
        "distance_mean_norm": round(mean_pair_distance / max(1.0, bbox_diag), 6),
        "distance_cv": round(_std(pair_distances, mean_pair_distance) / max(1.0, mean_pair_distance), 6) if pair_distances else 0.0,
        "structure_class": structure_class,
        "size_bucket": _size_bucket(len(customers)),
    }


def instance_payload(instance: CVRPInstance) -> dict[str, Any]:
    matrix = build_distance_matrix(instance)
    customers = [node for node in range(instance.dimension) if node != instance.depot_index]
    nearest_neighbors = {
        str(node): [
            int(other)
            for other in sorted(customers, key=lambda candidate: (matrix[node][candidate], candidate))
            if other != node
        ][:12]
        for node in customers
    }
    return {
        "dimension": int(instance.dimension),
        "depot_index": int(instance.depot_index),
        "customer_ids": customers,
        "vehicle_count_hint": int(instance.vehicle_count_hint or 0),
        "coordinates": [[float(x), float(y)] for x, y in instance.coordinates],
        "demands": [int(value) for value in instance.demands],
        "capacity": int(instance.capacity),
        "distance_matrix": matrix,
        "nearest_neighbors": nearest_neighbors,
        "descriptors": describe_instance(instance),
    }


def _std(values: list[float], mean_value: float) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum((value - mean_value) ** 2 for value in values) / len(values))


def _grid_likeness(points: list[tuple[float, float]]) -> float:
    if len(points) < 3:
        return 0.0
    unique_x = len({round(point[0], 3) for point in points})
    unique_y = len({round(point[1], 3) for point in points})
    repetition = 1.0 - ((unique_x + unique_y) / max(2.0, 2.0 * len(points)))
    return max(0.0, min(1.0, repetition * 2.0))


def _structure_class(*, corridor_score: float, grid_likeness: float, clusteredness: float, bottleneck_score: float) -> str:
    if corridor_score >= 0.5:
        return "corridor_like"
    if grid_likeness >= 0.35:
        return "grid_like"
    if bottleneck_score >= 0.45:
        return "two_cluster_bottleneck"
    if clusteredness >= 0.45:
        return "clustered"
    return "random_like"


def _size_bucket(customer_count: int) -> str:
    if customer_count < 130:
        return "small"
    if customer_count < 180:
        return "medium"
    return "large"
