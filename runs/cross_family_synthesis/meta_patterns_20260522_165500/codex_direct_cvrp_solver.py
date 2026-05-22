def _route_cost(matrix, depot, route):
    if not route:
        return 0
    total = matrix[depot][route[0]]
    for left, right in zip(route, route[1:]):
        total += matrix[left][right]
    total += matrix[route[-1]][depot]
    return total


def _route_load(route, demands):
    total = 0
    for node in route:
        total += demands[node]
    return total


def _two_opt_route(route, matrix, depot):
    if len(route) < 4:
        return list(route)
    best = list(route)
    best_cost = _route_cost(matrix, depot, best)
    changed = True
    passes = 0
    while changed and passes < 2:
        changed = False
        passes += 1
        for left in range(0, len(best) - 2):
            for right in range(left + 2, len(best)):
                if right - left <= 1:
                    continue
                candidate = best[:left] + list(reversed(best[left:right])) + best[right:]
                cost = _route_cost(matrix, depot, candidate)
                if cost < best_cost:
                    best = candidate
                    best_cost = cost
                    changed = True
                    break
            if changed:
                break
    return best


def _try_insert_customer(routes, loads, source_index, source_pos, target_index, target_pos, demands, capacity):
    customer = routes[source_index][source_pos]
    if source_index != target_index and loads[target_index] + demands[customer] > capacity:
        return None
    candidate = [list(route) for route in routes]
    candidate[source_index].pop(source_pos)
    if source_index == target_index and target_pos > source_pos:
        target_pos -= 1
    candidate[target_index].insert(target_pos, customer)
    return [route for route in candidate if route]


def _local_relocate(routes, matrix, demands, capacity, depot):
    current = [list(route) for route in routes if route]
    current_cost = sum(_route_cost(matrix, depot, route) for route in current)
    for _pass_index in range(2):
        improved = False
        route_loads = [_route_load(route, demands) for route in current]
        for source_index, source in enumerate(list(current)):
            for source_pos, customer in enumerate(list(source)):
                for target_index in range(len(current)):
                    target = current[target_index]
                    positions = range(len(target) + 1)
                    for target_pos in positions:
                        candidate = _try_insert_customer(
                            current,
                            route_loads,
                            source_index,
                            source_pos,
                            target_index,
                            target_pos,
                            demands,
                            capacity,
                        )
                        if candidate is None:
                            continue
                        candidate_cost = sum(_route_cost(matrix, depot, route) for route in candidate)
                        if candidate_cost + 1 < current_cost:
                            current = candidate
                            current_cost = candidate_cost
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break
        if not improved:
            break
    return current


def _clarke_wright(instance):
    matrix = instance["distance_matrix"]
    demands = instance["demands"]
    capacity = instance["capacity"]
    depot = instance["depot_index"]
    customers = list(instance["customer_ids"])
    routes = [[node] for node in customers]
    loads = [demands[node] for node in customers]
    route_of = {}
    for index, node in enumerate(customers):
        route_of[node] = index
    savings = []
    for i, left in enumerate(customers):
        for right in customers[i + 1:]:
            saving = matrix[depot][left] + matrix[depot][right] - matrix[left][right]
            savings.append((saving, -abs(demands[left] - demands[right]), left, right))
    savings.sort(reverse=True)
    for _saving, _demand_balance, left, right in savings:
        left_index = route_of.get(left)
        right_index = route_of.get(right)
        if left_index is None or right_index is None or left_index == right_index:
            continue
        left_route = routes[left_index]
        right_route = routes[right_index]
        if not left_route or not right_route:
            continue
        if loads[left_index] + loads[right_index] > capacity:
            continue
        merged = None
        if left_route[-1] == left and right_route[0] == right:
            merged = left_route + right_route
        elif right_route[-1] == right and left_route[0] == left:
            merged = right_route + left_route
        elif left_route[0] == left and right_route[0] == right:
            merged = list(reversed(left_route)) + right_route
        elif left_route[-1] == left and right_route[-1] == right:
            merged = left_route + list(reversed(right_route))
        if merged is None:
            continue
        routes[left_index] = merged
        loads[left_index] += loads[right_index]
        routes[right_index] = []
        loads[right_index] = 0
        for node in merged:
            route_of[node] = left_index
    return [route for route in routes if route]


def solve_cvrp(instance):
    matrix = instance["distance_matrix"]
    depot = instance["depot_index"]
    demands = instance["demands"]
    capacity = instance["capacity"]
    routes = _clarke_wright(instance)
    routes = [_two_opt_route(route, matrix, depot) for route in routes]
    routes = _local_relocate(routes, matrix, demands, capacity, depot)
    routes = [_two_opt_route(route, matrix, depot) for route in routes]
    return [route for route in routes if route]
