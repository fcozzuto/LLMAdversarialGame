from __future__ import annotations

from dataclasses import dataclass
import math
import statistics
from typing import Any, Iterable, Sequence, TYPE_CHECKING


if TYPE_CHECKING:
    from .benchmark import TSPInstance


PRIMARY_DESCRIPTOR_KEYS = [
    "city_count_norm",
    "coordinate_spread_norm",
    "aspect_ratio_norm",
    "nn_distance_mean_norm",
    "nn_distance_cv",
    "mst_length_norm",
    "convex_hull_ratio",
    "convex_hull_point_ratio",
    "clusteredness_score",
    "cluster_separation_norm",
    "grid_likeness",
    "bottleneck_score",
    "nearest_neighbor_trap_score",
]


@dataclass(frozen=True)
class ArchiveCompositionSummary:
    entry_count: int
    descriptor_diversity: float
    archive_hardness: float
    archive_residual_hardness: float
    size_bias: float
    replay_failure_concentration: float
    structure_histogram: dict[str, int]
    size_histogram: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_count": int(self.entry_count),
            "descriptor_diversity": round(self.descriptor_diversity, 6),
            "archive_hardness": round(self.archive_hardness, 6),
            "archive_residual_hardness": round(self.archive_residual_hardness, 6),
            "size_bias": round(self.size_bias, 6),
            "replay_failure_concentration": round(self.replay_failure_concentration, 6),
            "structure_histogram": dict(self.structure_histogram),
            "size_histogram": dict(self.size_histogram),
        }


def ensure_instance_descriptors(instance: TSPInstance) -> TSPInstance:
    if getattr(instance, "descriptors", None):
        return instance
    instance.descriptors = compute_instance_descriptors(instance)
    return instance


def compute_instance_descriptors(instance: TSPInstance) -> dict[str, Any]:
    from .benchmark import build_distance_matrix

    coords = list(instance.coordinates)
    n = int(instance.dimension)
    if n <= 1 or not coords:
        return {
            "city_count": n,
            "city_count_norm": 0.0,
            "coordinate_spread_norm": 0.0,
            "bbox_width_norm": 0.0,
            "bbox_height_norm": 0.0,
            "aspect_ratio": 1.0,
            "aspect_ratio_norm": 0.0,
            "nn_distance_mean_norm": 0.0,
            "nn_distance_std_norm": 0.0,
            "nn_distance_cv": 0.0,
            "nn_distance_min_norm": 0.0,
            "nn_distance_max_norm": 0.0,
            "mst_length": 0.0,
            "mst_length_norm": 0.0,
            "convex_hull_ratio": 0.0,
            "convex_hull_point_ratio": 0.0,
            "clusteredness_score": 0.0,
            "cluster_separation_score": 0.0,
            "cluster_separation_norm": 0.0,
            "grid_likeness": 0.0,
            "random_likeness": 1.0,
            "bottleneck_score": 0.0,
            "nearest_neighbor_trap_score": 0.0,
            "structure_class": "degenerate",
            "size_bucket": "tiny",
        }

    xs = [point[0] for point in coords]
    ys = [point[1] for point in coords]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    bbox_area = max(1.0, width * height)
    bbox_diag = max(1.0, math.hypot(width, height))
    centroid = (sum(xs) / n, sum(ys) / n)
    radial_distances = [math.hypot(x - centroid[0], y - centroid[1]) for x, y in coords]
    coordinate_spread_norm = _safe_mean(radial_distances) / bbox_diag
    aspect_ratio = max(width, height, 1.0) / max(1.0, min(width, height) if min(width, height) > 0.0 else 1.0)
    aspect_ratio_norm = min(1.0, math.log1p(aspect_ratio - 1.0) / math.log(8.0))

    matrix = build_distance_matrix(instance)
    nearest_neighbor_distances = [min(matrix[node][other] for other in range(n) if other != node) for node in range(n)]
    nn_mean = _safe_mean(nearest_neighbor_distances)
    nn_std = statistics.pstdev(nearest_neighbor_distances) if len(nearest_neighbor_distances) >= 2 else 0.0
    nn_cv = nn_std / max(1e-9, nn_mean)

    mst_edges = _mst_edge_lengths(matrix)
    mst_length = float(sum(mst_edges))
    mst_scale = math.sqrt(max(1.0, bbox_area) * max(1.0, float(n)))
    mst_length_norm = mst_length / max(1.0, mst_scale)

    hull = _convex_hull(coords)
    hull_area = _polygon_area(hull)
    convex_hull_ratio = min(1.0, hull_area / bbox_area) if bbox_area > 0.0 else 0.0
    convex_hull_point_ratio = len(hull) / max(1, n)

    cluster_metrics = _cluster_metrics(coords, bbox_diag)
    clusteredness_score = cluster_metrics.clusteredness_score
    cluster_separation_score = cluster_metrics.cluster_separation_score
    cluster_separation_norm = cluster_metrics.cluster_separation_norm

    grid_likeness = _grid_likeness(coords)
    random_likeness = max(0.0, min(1.0, 0.65 * (1.0 - grid_likeness) + 0.35 * (1.0 - clusteredness_score)))
    bottleneck_score = _bottleneck_score(mst_edges, cluster_metrics.cluster_separation_score)
    nearest_neighbor_trap_score = _nearest_neighbor_trap_score(instance, matrix)

    structure_class = _structure_class(
        aspect_ratio=aspect_ratio,
        grid_likeness=grid_likeness,
        clusteredness_score=clusteredness_score,
        bottleneck_score=bottleneck_score,
        random_likeness=random_likeness,
    )
    size_bucket = _size_bucket(n)

    return {
        "city_count": n,
        "city_count_norm": round(min(1.0, math.log1p(float(n)) / math.log(500.0)), 6),
        "coordinate_spread_norm": round(coordinate_spread_norm, 6),
        "bbox_width_norm": round(width / bbox_diag, 6),
        "bbox_height_norm": round(height / bbox_diag, 6),
        "aspect_ratio": round(aspect_ratio, 6),
        "aspect_ratio_norm": round(aspect_ratio_norm, 6),
        "nn_distance_mean_norm": round(nn_mean / bbox_diag, 6),
        "nn_distance_std_norm": round(nn_std / bbox_diag, 6),
        "nn_distance_cv": round(nn_cv, 6),
        "nn_distance_min_norm": round(min(nearest_neighbor_distances) / bbox_diag, 6),
        "nn_distance_max_norm": round(max(nearest_neighbor_distances) / bbox_diag, 6),
        "mst_length": round(mst_length, 6),
        "mst_length_norm": round(mst_length_norm, 6),
        "convex_hull_ratio": round(convex_hull_ratio, 6),
        "convex_hull_point_ratio": round(convex_hull_point_ratio, 6),
        "clusteredness_score": round(clusteredness_score, 6),
        "cluster_separation_score": round(cluster_separation_score, 6),
        "cluster_separation_norm": round(cluster_separation_norm, 6),
        "grid_likeness": round(grid_likeness, 6),
        "random_likeness": round(random_likeness, 6),
        "bottleneck_score": round(bottleneck_score, 6),
        "nearest_neighbor_trap_score": round(nearest_neighbor_trap_score, 6),
        "structure_class": structure_class,
        "size_bucket": size_bucket,
    }


def prompt_descriptor_summary(instance: TSPInstance | dict[str, Any]) -> dict[str, Any]:
    data = _instance_payload(instance)
    descriptors = descriptor_payload(instance)
    return {
        "name": str(data.get("name", "")),
        "family": str(data.get("family", "")),
        "dimension": int(data.get("dimension", 0)),
        "best_known_cost": int(data.get("best_known_cost", 0)),
        "structure_class": descriptors.get("structure_class", "unknown"),
        "size_bucket": descriptors.get("size_bucket", "unknown"),
        "coordinate_spread_norm": descriptors.get("coordinate_spread_norm", 0.0),
        "nn_distance_mean_norm": descriptors.get("nn_distance_mean_norm", 0.0),
        "nn_distance_cv": descriptors.get("nn_distance_cv", 0.0),
        "mst_length_norm": descriptors.get("mst_length_norm", 0.0),
        "convex_hull_ratio": descriptors.get("convex_hull_ratio", 0.0),
        "clusteredness_score": descriptors.get("clusteredness_score", 0.0),
        "grid_likeness": descriptors.get("grid_likeness", 0.0),
        "bottleneck_score": descriptors.get("bottleneck_score", 0.0),
        "nearest_neighbor_trap_score": descriptors.get("nearest_neighbor_trap_score", 0.0),
        "tags": list(data.get("tags", [])),
    }


def descriptor_payload(instance: TSPInstance | dict[str, Any]) -> dict[str, Any]:
    if isinstance(instance, dict):
        descriptors = dict(instance.get("descriptors", {}))
        return descriptors
    ensure_instance_descriptors(instance)
    return dict(instance.descriptors)


def descriptor_vector(instance: TSPInstance | dict[str, Any]) -> dict[str, float]:
    descriptors = descriptor_payload(instance)
    vector: dict[str, float] = {}
    for key in PRIMARY_DESCRIPTOR_KEYS:
        vector[key] = float(descriptors.get(key, 0.0))
    return vector


def descriptor_distance(left: TSPInstance | dict[str, Any], right: TSPInstance | dict[str, Any]) -> float:
    left_vector = descriptor_vector(left)
    right_vector = descriptor_vector(right)
    if not left_vector:
        return 0.0
    squared = sum((left_vector[key] - right_vector.get(key, 0.0)) ** 2 for key in left_vector)
    return round(math.sqrt(squared / len(left_vector)), 6)


def descriptor_diversity(items: Sequence[Any]) -> float:
    if len(items) < 2:
        return 0.0
    distances: list[float] = []
    for left_index in range(len(items)):
        for right_index in range(left_index + 1, len(items)):
            distances.append(descriptor_distance(_entry_instance(items[left_index]), _entry_instance(items[right_index])))
    return round(_safe_mean(distances), 6)


def archive_hardness(items: Sequence[Any]) -> float:
    if not items:
        return 0.0
    return round(_safe_mean(_entry_gap(item) for item in items), 6)


def archive_residual_hardness(items: Sequence[Any]) -> float:
    if not items:
        return 0.0
    return round(_safe_mean(_entry_residual_gap(item) for item in items), 6)


def archive_size_bias(items: Sequence[Any], reference_instances: Sequence[TSPInstance | dict[str, Any]]) -> float:
    if not items or not reference_instances:
        return 0.0
    archive_mean = _safe_mean(float(descriptor_payload(_entry_instance(item)).get("city_count_norm", 0.0)) for item in items)
    reference_mean = _safe_mean(float(descriptor_payload(item).get("city_count_norm", 0.0)) for item in reference_instances)
    return round(archive_mean - reference_mean, 6)


def replay_failure_concentration(items: Sequence[Any]) -> float:
    total = sum(max(0, int(_entry_times_selected(item))) for item in items)
    if total <= 0:
        return 0.0
    shares = [int(_entry_times_selected(item)) / total for item in items if int(_entry_times_selected(item)) > 0]
    if not shares:
        return 0.0
    return round(sum(share * share for share in shares), 6)


def structure_histogram(items: Sequence[Any]) -> dict[str, int]:
    histogram: dict[str, int] = {}
    for item in items:
        structure = str(descriptor_payload(_entry_instance(item)).get("structure_class", "unknown"))
        histogram[structure] = histogram.get(structure, 0) + 1
    return dict(sorted(histogram.items()))


def size_histogram(items: Sequence[Any]) -> dict[str, int]:
    histogram: dict[str, int] = {}
    for item in items:
        bucket = str(descriptor_payload(_entry_instance(item)).get("size_bucket", "unknown"))
        histogram[bucket] = histogram.get(bucket, 0) + 1
    return dict(sorted(histogram.items()))


def stratification_key(instance: TSPInstance | dict[str, Any]) -> str:
    descriptors = descriptor_payload(instance)
    return f"{descriptors.get('size_bucket', 'unknown')}::{descriptors.get('structure_class', 'unknown')}"


def summarize_archive_composition(
    items: Sequence[Any],
    *,
    reference_instances: Sequence[TSPInstance | dict[str, Any]] | None = None,
) -> ArchiveCompositionSummary:
    return ArchiveCompositionSummary(
        entry_count=len(items),
        descriptor_diversity=descriptor_diversity(items),
        archive_hardness=archive_hardness(items),
        archive_residual_hardness=archive_residual_hardness(items),
        size_bias=archive_size_bias(items, list(reference_instances or [])),
        replay_failure_concentration=replay_failure_concentration(items),
        structure_histogram=structure_histogram(items),
        size_histogram=size_histogram(items),
    )


def _safe_mean(values: Iterable[float]) -> float:
    items = [float(value) for value in values]
    return sum(items) / len(items) if items else 0.0


@dataclass(frozen=True)
class _ClusterMetrics:
    clusteredness_score: float
    cluster_separation_score: float
    cluster_separation_norm: float


def _cluster_metrics(coords: list[tuple[float, float]], bbox_diag: float) -> _ClusterMetrics:
    best_clusteredness = 0.0
    best_separation_score = 0.0
    for cluster_count in range(2, min(4, len(coords)) + 1):
        centroids, assignments = _kmeans(coords, cluster_count)
        if not centroids or not assignments:
            continue
        within = 0.0
        cluster_sizes = [0 for _ in centroids]
        for point, cluster_index in zip(coords, assignments):
            cluster_sizes[cluster_index] += 1
            within += math.hypot(point[0] - centroids[cluster_index][0], point[1] - centroids[cluster_index][1])
        within /= max(1, len(coords))
        between_distances = [
            math.hypot(left[0] - right[0], left[1] - right[1])
            for left_index, left in enumerate(centroids)
            for right in centroids[left_index + 1 :]
        ]
        between = _safe_mean(between_distances)
        balance = 1.0 - (statistics.pstdev(cluster_sizes) / max(1.0, _safe_mean(cluster_sizes))) if len(cluster_sizes) > 1 else 1.0
        clusteredness = max(0.0, min(1.0, (between / max(1.0, bbox_diag)) * 0.75 + (1.0 - min(1.0, within / max(1.0, bbox_diag))) * 0.25))
        clusteredness *= max(0.3, balance)
        separation_score = between / max(1.0, within)
        if clusteredness > best_clusteredness:
            best_clusteredness = clusteredness
            best_separation_score = separation_score
    return _ClusterMetrics(
        clusteredness_score=round(max(0.0, min(1.0, best_clusteredness)), 6),
        cluster_separation_score=round(best_separation_score, 6),
        cluster_separation_norm=round(max(0.0, min(1.0, best_separation_score / 6.0)), 6),
    )


def _kmeans(coords: list[tuple[float, float]], cluster_count: int) -> tuple[list[tuple[float, float]], list[int]]:
    if cluster_count <= 0 or cluster_count > len(coords):
        return [], []
    centroids = _farthest_first_seeds(coords, cluster_count)
    assignments = [0 for _ in coords]
    for _ in range(8):
        changed = False
        for index, point in enumerate(coords):
            distances = [((point[0] - cx) ** 2) + ((point[1] - cy) ** 2) for cx, cy in centroids]
            best_index = min(range(len(distances)), key=lambda item: distances[item])
            if assignments[index] != best_index:
                assignments[index] = best_index
                changed = True
        new_centroids: list[tuple[float, float]] = []
        for cluster_index in range(cluster_count):
            members = [coords[index] for index, assignment in enumerate(assignments) if assignment == cluster_index]
            if not members:
                new_centroids.append(centroids[cluster_index])
                continue
            mean_x = sum(point[0] for point in members) / len(members)
            mean_y = sum(point[1] for point in members) / len(members)
            new_centroids.append((mean_x, mean_y))
        centroids = new_centroids
        if not changed:
            break
    return centroids, assignments


def _farthest_first_seeds(coords: list[tuple[float, float]], cluster_count: int) -> list[tuple[float, float]]:
    centroid = (
        sum(point[0] for point in coords) / len(coords),
        sum(point[1] for point in coords) / len(coords),
    )
    ordered = sorted(coords, key=lambda point: math.hypot(point[0] - centroid[0], point[1] - centroid[1]), reverse=True)
    seeds = [ordered[0]]
    while len(seeds) < cluster_count:
        best_point = max(
            coords,
            key=lambda point: min(math.hypot(point[0] - seed[0], point[1] - seed[1]) for seed in seeds),
        )
        if best_point in seeds:
            break
        seeds.append(best_point)
    return seeds[:cluster_count]


def _grid_likeness(coords: list[tuple[float, float]]) -> float:
    if len(coords) < 4:
        return 0.0
    xs = sorted(round(point[0], 3) for point in coords)
    ys = sorted(round(point[1], 3) for point in coords)
    unique_x = len(set(xs))
    unique_y = len(set(ys))
    repeated_axis_fraction = 1.0 - ((_safe_mean([unique_x, unique_y]) - 1.0) / max(1.0, len(coords) - 1.0))
    x_gap_cv = _gap_cv(sorted(set(xs)))
    y_gap_cv = _gap_cv(sorted(set(ys)))
    regularity = 1.0 - min(1.0, _safe_mean([x_gap_cv, y_gap_cv]))
    return round(max(0.0, min(1.0, (0.45 * repeated_axis_fraction) + (0.55 * regularity))), 6)


def _gap_cv(values: list[float]) -> float:
    if len(values) < 3:
        return 1.0
    gaps = [values[index + 1] - values[index] for index in range(len(values) - 1) if values[index + 1] - values[index] > 1e-9]
    if len(gaps) < 2:
        return 1.0
    mean_gap = _safe_mean(gaps)
    if mean_gap <= 0.0:
        return 1.0
    return statistics.pstdev(gaps) / mean_gap


def _bottleneck_score(mst_edges: list[int], cluster_separation_score: float) -> float:
    if not mst_edges:
        return 0.0
    median_edge = statistics.median(float(edge) for edge in mst_edges)
    longest_edge = float(max(mst_edges))
    mst_jump = longest_edge / max(1.0, median_edge)
    return round(max(0.0, min(1.0, (0.5 * min(1.0, (mst_jump - 1.0) / 4.0)) + (0.5 * min(1.0, cluster_separation_score / 6.0)))), 6)


def _nearest_neighbor_trap_score(instance: TSPInstance, matrix: list[list[int]]) -> float:
    tour = _greedy_nearest_neighbor_tour(instance, matrix)
    if not tour or instance.best_known_cost <= 0:
        return 0.0
    cost = _tour_cost(matrix, tour)
    gap = (cost - instance.best_known_cost) / max(1, instance.best_known_cost)
    return max(0.0, min(1.0, gap))


def _greedy_nearest_neighbor_tour(instance: TSPInstance, matrix: list[list[int]]) -> list[int]:
    coords = list(instance.coordinates)
    centroid = (
        sum(point[0] for point in coords) / len(coords),
        sum(point[1] for point in coords) / len(coords),
    )
    candidate_starts = {
        min(range(len(coords)), key=lambda idx: math.hypot(coords[idx][0] - centroid[0], coords[idx][1] - centroid[1])),
        max(range(len(coords)), key=lambda idx: math.hypot(coords[idx][0] - centroid[0], coords[idx][1] - centroid[1])),
        min(range(len(coords)), key=lambda idx: (coords[idx][0], coords[idx][1])),
        max(range(len(coords)), key=lambda idx: (coords[idx][1], coords[idx][0])),
    }
    best_cost = None
    best_tour: list[int] = []
    for start in candidate_starts:
        unvisited = set(range(instance.dimension))
        unvisited.remove(start)
        tour = [start]
        while unvisited:
            current = tour[-1]
            next_node = min(
                unvisited,
                key=lambda node: (
                    matrix[current][node],
                    math.hypot(coords[node][0] - centroid[0], coords[node][1] - centroid[1]),
                    node,
                ),
            )
            tour.append(next_node)
            unvisited.remove(next_node)
        cost = _tour_cost(matrix, tour)
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_tour = tour
    return best_tour


def _tour_cost(matrix: list[list[int]], tour: list[int]) -> int:
    total = 0
    for index, node in enumerate(tour):
        total += matrix[node][tour[(index + 1) % len(tour)]]
    return total


def _mst_edge_lengths(matrix: list[list[int]]) -> list[int]:
    node_count = len(matrix)
    if node_count <= 1:
        return []
    in_tree = [False for _ in range(node_count)]
    best_edge = [10**12 for _ in range(node_count)]
    parent = [-1 for _ in range(node_count)]
    best_edge[0] = 0
    edges: list[int] = []
    for _ in range(node_count):
        node = min((idx for idx in range(node_count) if not in_tree[idx]), key=lambda idx: best_edge[idx])
        in_tree[node] = True
        if parent[node] != -1:
            edges.append(int(best_edge[node]))
        for other in range(node_count):
            weight = matrix[node][other]
            if not in_tree[other] and 0 < weight < best_edge[other]:
                best_edge[other] = weight
                parent[other] = node
    return edges


def _convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    sorted_points = sorted(set(points))
    if len(sorted_points) <= 1:
        return sorted_points

    def cross(origin: tuple[float, float], left: tuple[float, float], right: tuple[float, float]) -> float:
        return (left[0] - origin[0]) * (right[1] - origin[1]) - (left[1] - origin[1]) * (right[0] - origin[0])

    lower: list[tuple[float, float]] = []
    for point in sorted_points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    upper: list[tuple[float, float]] = []
    for point in reversed(sorted_points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    return lower[:-1] + upper[:-1]


def _polygon_area(points: list[tuple[float, float]]) -> float:
    if len(points) < 3:
        return 0.0
    total = 0.0
    for index, point in enumerate(points):
        next_point = points[(index + 1) % len(points)]
        total += (point[0] * next_point[1]) - (next_point[0] * point[1])
    return abs(total) / 2.0


def _structure_class(
    *,
    aspect_ratio: float,
    grid_likeness: float,
    clusteredness_score: float,
    bottleneck_score: float,
    random_likeness: float,
) -> str:
    if aspect_ratio >= 3.0 and grid_likeness < 0.45:
        return "corridor_like"
    if bottleneck_score >= 0.58:
        return "two_cluster_bottleneck"
    if grid_likeness >= 0.58:
        return "grid_like"
    if clusteredness_score >= 0.56:
        return "clustered"
    if random_likeness >= 0.56:
        return "random_like"
    return "mixed"


def _size_bucket(city_count: int) -> str:
    if city_count <= 70:
        return "small"
    if city_count <= 130:
        return "medium"
    if city_count <= 250:
        return "large"
    return "xlarge"


def _instance_payload(instance: TSPInstance | dict[str, Any]) -> dict[str, Any]:
    if isinstance(instance, dict):
        return instance
    ensure_instance_descriptors(instance)
    return instance.to_dict()


def _entry_instance(item: Any) -> TSPInstance | dict[str, Any]:
    if hasattr(item, "instance"):
        return item.instance
    if isinstance(item, dict) and "instance" in item:
        return item["instance"]
    return item


def _entry_gap(item: Any) -> float:
    if hasattr(item, "gap"):
        return float(item.gap)
    if isinstance(item, dict):
        if "gap" in item:
            return float(item.get("gap", 0.0))
        return float(item.get("optimality_gap", 0.0))
    return 0.0


def _entry_residual_gap(item: Any) -> float:
    if hasattr(item, "residual_gap"):
        return float(getattr(item, "residual_gap", 0.0))
    if isinstance(item, dict):
        return float(item.get("residual_gap", 0.0))
    return 0.0


def _entry_times_selected(item: Any) -> int:
    if hasattr(item, "times_selected"):
        return int(getattr(item, "times_selected", 0))
    if isinstance(item, dict):
        return int(item.get("times_selected", 0))
    return 0
