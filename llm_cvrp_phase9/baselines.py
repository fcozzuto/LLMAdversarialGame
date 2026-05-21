from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Any, Callable

from llm_cvrp.benchmark import CVRPInstance, build_distance_matrix


def baseline_specs() -> list[dict[str, str]]:
    return [
        {
            "name": "nearest_neighbor_constructive",
            "description": "Greedy nearest-feasible-neighbor route construction with no post-optimization.",
        },
        {
            "name": "clarke_wright_savings",
            "description": "Classical Clarke-Wright savings merges with capacity feasibility.",
        },
        {
            "name": "regret_insertion_local_search",
            "description": "Regret-style insertion followed by bounded intra/inter-route local search.",
        },
    ]


def baseline_solver(name: str) -> Callable[[CVRPInstance, int], dict[str, Any]]:
    catalog = {
        "nearest_neighbor_constructive": solve_nearest_neighbor,
        "clarke_wright_savings": solve_clarke_wright,
        "regret_insertion_local_search": solve_regret_insertion_local_search,
    }
    if name not in catalog:
        raise KeyError(f"Unknown baseline solver: {name}")
    return catalog[name]


def solve_nearest_neighbor(instance: CVRPInstance, seed: int = 0) -> dict[str, Any]:
    del seed
    matrix = build_distance_matrix(instance)
    customers = {node for node in range(instance.dimension) if node != instance.depot_index}
    routes: list[list[int]] = []
    while customers:
        route: list[int] = []
        load = 0
        current = instance.depot_index
        while True:
            feasible = [
                node
                for node in customers
                if load + instance.demands[node] <= instance.capacity
            ]
            if not feasible:
                break
            next_node = min(feasible, key=lambda node: (matrix[current][node], instance.demands[node], node))
            route.append(next_node)
            customers.remove(next_node)
            load += instance.demands[next_node]
            current = next_node
        routes.append(route)
    return {"routes": routes, "solver_metadata": {"baseline_name": "nearest_neighbor_constructive"}}


def solve_clarke_wright(instance: CVRPInstance, seed: int = 0) -> dict[str, Any]:
    del seed
    matrix = build_distance_matrix(instance)
    depot = instance.depot_index
    routes = [[node] for node in range(instance.dimension) if node != depot]
    route_loads = [instance.demands[route[0]] for route in routes]
    route_of = {route[0]: index for index, route in enumerate(routes)}
    savings_pairs = []
    customers = [node for node in range(instance.dimension) if node != depot]
    for left_index, left in enumerate(customers):
        for right in customers[left_index + 1 :]:
            savings = matrix[depot][left] + matrix[depot][right] - matrix[left][right]
            savings_pairs.append((savings, left, right))
    savings_pairs.sort(reverse=True)
    for _savings, left, right in savings_pairs:
        left_route_index = route_of.get(left)
        right_route_index = route_of.get(right)
        if left_route_index is None or right_route_index is None or left_route_index == right_route_index:
            continue
        left_route = routes[left_route_index]
        right_route = routes[right_route_index]
        if not left_route or not right_route:
            continue
        if left_route[-1] == left and right_route[0] == right:
            merged = left_route + right_route
        elif right_route[-1] == right and left_route[0] == left:
            merged = right_route + left_route
        elif left_route[0] == left and right_route[0] == right:
            merged = list(reversed(left_route)) + right_route
        elif left_route[-1] == left and right_route[-1] == right:
            merged = left_route + list(reversed(right_route))
        else:
            continue
        merged_load = route_loads[left_route_index] + route_loads[right_route_index]
        if merged_load > instance.capacity:
            continue
        routes[left_route_index] = merged
        route_loads[left_route_index] = merged_load
        routes[right_route_index] = []
        route_loads[right_route_index] = 0
        for node in merged:
            route_of[node] = left_route_index
    compact = [route for route in routes if route]
    return {"routes": compact, "solver_metadata": {"baseline_name": "clarke_wright_savings"}}


def solve_regret_insertion_local_search(instance: CVRPInstance, seed: int = 0) -> dict[str, Any]:
    matrix = build_distance_matrix(instance)
    routes = _regret_insertion_routes(instance, matrix, seed=seed)
    routes = _two_opt_pass(instance, matrix, routes, passes=2)
    routes = _relocate_pass(instance, matrix, routes, passes=1)
    return {"routes": routes, "solver_metadata": {"baseline_name": "regret_insertion_local_search"}}


def optional_ortools_reference(instance: CVRPInstance, seed: int = 0) -> dict[str, Any]:
    del seed
    try:
        from ortools.constraint_solver import pywrapcp, routing_enums_pb2  # type: ignore
    except Exception as exc:  # pragma: no cover - optional baseline
        raise RuntimeError(f"OR-Tools is not available: {exc}") from exc
    matrix = build_distance_matrix(instance)
    vehicle_count = int(instance.vehicle_count_hint or max(1, len(instance.demands) // 10))
    manager = pywrapcp.RoutingIndexManager(instance.dimension, vehicle_count, instance.depot_index)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(left_index: int, right_index: int) -> int:
        left_node = manager.IndexToNode(left_index)
        right_node = manager.IndexToNode(right_index)
        return int(matrix[left_node][right_node])

    transit_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_index)

    def demand_callback(index: int) -> int:
        node = manager.IndexToNode(index)
        return int(instance.demands[node])

    demand_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_index,
        0,
        [int(instance.capacity)] * vehicle_count,
        True,
        "Capacity",
    )
    search = pywrapcp.DefaultRoutingSearchParameters()
    search.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search.time_limit.seconds = 5
    assignment = routing.SolveWithParameters(search)
    if assignment is None:
        raise RuntimeError("OR-Tools did not return a solution")
    routes: list[list[int]] = []
    for vehicle in range(vehicle_count):
        index = routing.Start(vehicle)
        route: list[int] = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != instance.depot_index:
                route.append(int(node))
            index = assignment.Value(routing.NextVar(index))
        if route:
            routes.append(route)
    return {"routes": routes, "solver_metadata": {"baseline_name": "ortools_reference"}}


def _regret_insertion_routes(instance: CVRPInstance, matrix: list[list[int]], *, seed: int) -> list[list[int]]:
    del seed
    customers = [node for node in range(instance.dimension) if node != instance.depot_index]
    ordered = sorted(customers, key=lambda node: (-matrix[instance.depot_index][node], -instance.demands[node], node))
    route_count = max(1, int(instance.vehicle_count_hint or max(1, len(customers) // 12)))
    seeds = ordered[: min(route_count, len(ordered))]
    routes = [[node] for node in seeds]
    route_loads = [instance.demands[node] for node in seeds]
    remaining = {node for node in customers if node not in seeds}
    while remaining:
        best_choice = None
        best_score = None
        for customer in sorted(remaining):
            insertions = []
            for route_index, route in enumerate(routes):
                if route_loads[route_index] + instance.demands[customer] > instance.capacity:
                    continue
                delta, position = _best_insertion(matrix, instance.depot_index, route, customer)
                insertions.append((delta, route_index, position))
            if not insertions:
                routes.append([customer])
                route_loads.append(instance.demands[customer])
                remaining.remove(customer)
                break
            insertions.sort(key=lambda item: item[0])
            first = insertions[0]
            second_delta = insertions[1][0] if len(insertions) > 1 else first[0] + matrix[instance.depot_index][customer]
            regret = second_delta - first[0]
            score = (regret, -first[0], -instance.demands[customer])
            if best_score is None or score > best_score:
                best_score = score
                best_choice = (customer, first[1], first[2])
        else:
            if best_choice is None:
                break
            customer, route_index, position = best_choice
            routes[route_index].insert(position, customer)
            route_loads[route_index] += instance.demands[customer]
            remaining.remove(customer)
            continue
        continue
    return [route for route in routes if route]


def _best_insertion(matrix: list[list[int]], depot: int, route: list[int], customer: int) -> tuple[int, int]:
    if not route:
        return (2 * matrix[depot][customer], 0)
    best_delta = None
    best_position = 0
    previous = depot
    for position, nxt in enumerate(route):
        delta = matrix[previous][customer] + matrix[customer][nxt] - matrix[previous][nxt]
        if best_delta is None or delta < best_delta:
            best_delta = delta
            best_position = position
        previous = nxt
    tail_delta = matrix[previous][customer] + matrix[customer][depot] - matrix[previous][depot]
    if best_delta is None or tail_delta < best_delta:
        return tail_delta, len(route)
    return int(best_delta), best_position


def _route_cost(matrix: list[list[int]], depot: int, route: list[int]) -> int:
    if not route:
        return 0
    cost = matrix[depot][route[0]]
    for left, right in zip(route, route[1:]):
        cost += matrix[left][right]
    cost += matrix[route[-1]][depot]
    return int(cost)


def _two_opt_pass(instance: CVRPInstance, matrix: list[list[int]], routes: list[list[int]], *, passes: int) -> list[list[int]]:
    improved_routes = [list(route) for route in routes]
    for _ in range(max(1, passes)):
        changed = False
        for route_index, route in enumerate(improved_routes):
            best_route = route
            best_cost = _route_cost(matrix, instance.depot_index, route)
            for left in range(len(route)):
                for right in range(left + 2, len(route)):
                    candidate = route[:left] + list(reversed(route[left:right])) + route[right:]
                    candidate_cost = _route_cost(matrix, instance.depot_index, candidate)
                    if candidate_cost < best_cost:
                        best_cost = candidate_cost
                        best_route = candidate
                        changed = True
            improved_routes[route_index] = best_route
        if not changed:
            break
    return improved_routes


def _relocate_pass(instance: CVRPInstance, matrix: list[list[int]], routes: list[list[int]], *, passes: int) -> list[list[int]]:
    current = [list(route) for route in routes]
    for _ in range(max(1, passes)):
        changed = False
        route_loads = [sum(instance.demands[node] for node in route) for route in current]
        baseline_cost = sum(_route_cost(matrix, instance.depot_index, route) for route in current)
        for source_index, source_route in enumerate(current):
            for source_pos, customer in enumerate(list(source_route)):
                for target_index, target_route in enumerate(current):
                    if source_index == target_index:
                        continue
                    if route_loads[target_index] + instance.demands[customer] > instance.capacity:
                        continue
                    for target_pos in range(len(target_route) + 1):
                        candidate_routes = [list(route) for route in current]
                        candidate_routes[source_index].pop(source_pos)
                        candidate_routes[target_index].insert(target_pos, customer)
                        candidate_routes = [route for route in candidate_routes if route]
                        candidate_cost = sum(_route_cost(matrix, instance.depot_index, route) for route in candidate_routes)
                        if candidate_cost < baseline_cost:
                            current = candidate_routes
                            changed = True
                            break
                    if changed:
                        break
                if changed:
                    break
            if changed:
                break
        if not changed:
            break
    return current
