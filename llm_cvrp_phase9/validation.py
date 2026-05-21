from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from llm_cvrp.benchmark import CVRPInstance, build_distance_matrix, compute_solution_cost


@dataclass
class ValidationResult:
    feasible: bool
    routes: list[list[int]]
    route_count: int
    cost: int | None
    optimality_gap: float | None
    penalized_gap: float
    errors: list[str]
    missing_count: int
    duplicate_count: int
    over_capacity_routes: int
    route_count_excess: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "feasible": bool(self.feasible),
            "routes": [list(route) for route in self.routes],
            "route_count": int(self.route_count),
            "cost": int(self.cost) if self.cost is not None else None,
            "optimality_gap": round(float(self.optimality_gap), 6) if self.optimality_gap is not None else None,
            "penalized_gap": round(float(self.penalized_gap), 6),
            "errors": list(self.errors),
            "missing_count": int(self.missing_count),
            "duplicate_count": int(self.duplicate_count),
            "over_capacity_routes": int(self.over_capacity_routes),
            "route_count_excess": int(self.route_count_excess),
        }


def validate_solution(
    instance: CVRPInstance,
    routes: Any,
    *,
    enforce_vehicle_count: bool,
    infeasible_gap_penalty: float,
) -> ValidationResult:
    normalized_routes: list[list[int]] = []
    errors: list[str] = []
    missing_count = 0
    duplicate_count = 0
    over_capacity_routes = 0
    route_count_excess = 0

    if not isinstance(routes, list):
        errors.append("solver did not return a list of routes")
        return ValidationResult(
            feasible=False,
            routes=[],
            route_count=0,
            cost=None,
            optimality_gap=None,
            penalized_gap=float(infeasible_gap_penalty + 1.0),
            errors=errors,
            missing_count=0,
            duplicate_count=0,
            over_capacity_routes=0,
            route_count_excess=0,
        )

    customer_set = {node for node in range(instance.dimension) if node != instance.depot_index}
    seen: set[int] = set()
    for route_index, raw_route in enumerate(routes):
        if not isinstance(raw_route, list):
            errors.append(f"route {route_index} is not a list")
            continue
        route: list[int] = []
        for token in raw_route:
            if not isinstance(token, int):
                errors.append(f"route {route_index} contains a non-integer node id")
                continue
            if token == instance.depot_index:
                errors.append(f"route {route_index} explicitly includes the depot")
                continue
            if token < 0 or token >= instance.dimension:
                errors.append(f"route {route_index} contains out-of-range node id {token}")
                continue
            route.append(token)
            if token in seen:
                duplicate_count += 1
            seen.add(token)
        normalized_routes.append(route)

    missing_count = len(customer_set - seen)
    if missing_count:
        errors.append(f"missing {missing_count} customers")
    if duplicate_count:
        errors.append(f"duplicated {duplicate_count} customers")

    for route_index, route in enumerate(normalized_routes):
        load = sum(instance.demands[node] for node in route)
        if load > instance.capacity:
            over_capacity_routes += 1
            errors.append(
                f"route {route_index} exceeds capacity ({load} > {instance.capacity})"
            )

    vehicle_hint = int(instance.vehicle_count_hint or 0)
    if enforce_vehicle_count and vehicle_hint > 0 and len([route for route in normalized_routes if route]) > vehicle_hint:
        route_count_excess = len([route for route in normalized_routes if route]) - vehicle_hint
        errors.append(f"solution uses {route_count_excess} more routes than the vehicle-count hint")

    if errors:
        penalty = float(infeasible_gap_penalty)
        penalty += 0.05 * float(missing_count)
        penalty += 0.05 * float(duplicate_count)
        penalty += 0.1 * float(over_capacity_routes)
        penalty += 0.05 * float(route_count_excess)
        return ValidationResult(
            feasible=False,
            routes=normalized_routes,
            route_count=len([route for route in normalized_routes if route]),
            cost=None,
            optimality_gap=None,
            penalized_gap=round(penalty, 6),
            errors=errors,
            missing_count=missing_count,
            duplicate_count=duplicate_count,
            over_capacity_routes=over_capacity_routes,
            route_count_excess=route_count_excess,
        )

    cost = compute_solution_cost(instance, normalized_routes)
    gap = ((cost - instance.best_known_cost) / instance.best_known_cost) if instance.best_known_cost else 0.0
    return ValidationResult(
        feasible=True,
        routes=normalized_routes,
        route_count=len([route for route in normalized_routes if route]),
        cost=int(cost),
        optimality_gap=round(gap, 6),
        penalized_gap=round(gap, 6),
        errors=[],
        missing_count=0,
        duplicate_count=0,
        over_capacity_routes=0,
        route_count_excess=0,
    )


def summarize_panel(results: list[dict[str, Any]], *, panel_name: str) -> dict[str, Any]:
    if not results:
        return {
            "enabled": False,
            "panel_name": panel_name,
            "instance_count": 0,
            "feasibility_rate": 0.0,
            "mean_penalized_gap": 0.0,
            "mean_feasible_gap": None,
            "mean_runtime_ms": 0.0,
            "family_means": [],
            "worst_instances": [],
        }
    feasible = [item for item in results if bool(item["validation"]["feasible"])]
    mean_penalized_gap = sum(float(item["validation"]["penalized_gap"]) for item in results) / len(results)
    mean_feasible_gap = (
        sum(float(item["validation"]["optimality_gap"]) for item in feasible) / len(feasible)
        if feasible
        else None
    )
    mean_runtime_ms = sum(float(item["runtime_ms"]) for item in results) / len(results)
    by_family: dict[str, list[dict[str, Any]]] = {}
    for item in results:
        family = str(item["descriptors"].get("structure_class", "unknown"))
        by_family.setdefault(family, []).append(item)
    family_means = []
    for family_name, family_results in sorted(by_family.items()):
        family_feasible = [item for item in family_results if bool(item["validation"]["feasible"])]
        family_means.append(
            {
                "family": family_name,
                "count": len(family_results),
                "feasibility_rate": round(len(family_feasible) / len(family_results), 6),
                "mean_penalized_gap": round(
                    sum(float(item["validation"]["penalized_gap"]) for item in family_results) / len(family_results),
                    6,
                ),
                "mean_feasible_gap": round(
                    sum(float(item["validation"]["optimality_gap"]) for item in family_feasible) / len(family_feasible),
                    6,
                ) if family_feasible else None,
            }
        )
    worst_instances = [
        {
            "instance_name": str(item["instance_name"]),
            "family": str(item["descriptors"].get("structure_class", "unknown")),
            "feasible": bool(item["validation"]["feasible"]),
            "penalized_gap": float(item["validation"]["penalized_gap"]),
            "optimality_gap": item["validation"]["optimality_gap"],
            "runtime_ms": round(float(item["runtime_ms"]), 6),
            "errors": list(item["validation"]["errors"]),
        }
        for item in sorted(results, key=lambda record: float(record["validation"]["penalized_gap"]), reverse=True)[:5]
    ]
    return {
        "enabled": True,
        "panel_name": panel_name,
        "instance_count": len(results),
        "feasibility_rate": round(len(feasible) / len(results), 6),
        "mean_penalized_gap": round(mean_penalized_gap, 6),
        "mean_feasible_gap": round(mean_feasible_gap, 6) if mean_feasible_gap is not None else None,
        "mean_runtime_ms": round(mean_runtime_ms, 6),
        "family_means": family_means,
        "worst_instances": worst_instances,
    }
