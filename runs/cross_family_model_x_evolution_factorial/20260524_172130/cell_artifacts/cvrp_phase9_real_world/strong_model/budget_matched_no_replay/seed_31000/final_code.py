def solve_cvrp(instance):
    # Flexible instance parsing
    def get(obj, *keys, default=None):
        if isinstance(obj, dict):
            for k in keys:
                if k in obj:
                    return obj[k]
        return default

    depot = get(instance, "depot", default=0)
    capacity = get(instance, "capacity", "vehicle_capacity", default=None)

    # Customers and demands
    customers = get(instance, "customers", "nodes", default=None)
    demands = get(instance, "demands", default=None)
    if customers is None:
        if isinstance(instance, dict):
            if "coords" in instance:
                customers = list(range(len(instance["coords"])))
            elif "distance_matrix" in instance or "distances" in instance:
                n = len(get(instance, "distance_matrix", "distances"))
                customers = list(range(n))
            else:
                customers = []
        else:
            customers = []

    # Normalize customer list excluding depot
    if depot in customers:
        customers = [c for c in customers if c != depot]

    # Distances
    dist = get(instance, "distance_matrix", "distances", default=None)
    coords = get(instance, "coords", "coordinates", default=None)

    def d(i, j):
        if dist is not None:
            return dist[i][j]
        if coords is not None:
            xi, yi = coords[i]
            xj, yj = coords[j]
            dx = xi - xj
            dy = yi - yj
            return (dx * dx + dy * dy) ** 0.5
        return abs(i - j)

    # Demands fallback
    if demands is None:
        demands = {}
        if isinstance(instance, dict) and "demand" in instance and isinstance(instance["demand"], dict):
            demands = instance["demand"]
        else:
            for c in customers:
                demands[c] = 1

    def demand(c):
        if isinstance(demands, dict):
            return demands.get(c, 1)
        return demands[c]

    # If capacity missing, make a safe large one
    if capacity is None:
        capacity = sum(demand(c) for c in customers)

    # Feasibility guard: if some demand exceeds capacity, still assign alone
    unassigned = set(customers)

    # Deterministic seed order: farthest from depot first, tie by id
    ordered = sorted(customers, key=lambda c: (-d(depot, c), c))

    routes = []

    # Constructive phase: greedy insertion with capacity-aware nearest neighbor
    while unassigned:
        route = []
        load = 0
        current = depot

        # start with best feasible customer from depot
        candidates = [c for c in ordered if c in unassigned and demand(c) + load <= capacity]
        if not candidates:
            # isolate one customer if all remaining exceed capacity
            c = min(unassigned, key=lambda x: (d(depot, x), x))
            candidates = [c]

        # choose first by farthest from depot among feasible to encourage good packing
        first = min(candidates, key=lambda c: (d(depot, c), c))
        route.append(first)
        unassigned.remove(first)
        load += demand(first)
        current = first

        while True:
            feasible = [c for c in ordered if c in unassigned and load + demand(c) <= capacity]
            if not feasible:
                break
            # choose customer minimizing insertion cost from current, with light demand preference
            best = None
            best_key = None
            for c in feasible:
                key = (d(current, c) + 0.15 * d(depot, c), demand(c), c)
                if best_key is None or key < best_key:
                    best_key = key
                    best = c
            route.append(best)
            unassigned.remove(best)
            load += demand(best)
            current = best

        routes.append(route)

    # Local search: intra-route 2-opt for travel reduction (no depot in output)
    def route_cost(route):
        if not route:
            return 0
        total = d(depot, route[0])
        for i in range(len(route) - 1):
            total += d(route[i], route[i + 1])
        total += d(route[-1], depot)
        return total

    def improve_route(route):
        if len(route) < 4:
            return route
        improved = True
        while improved:
            improved = False
            n = len(route)
            best_delta = 0
            best_i = best_j = None
            for i in range(n - 2):
                a = depot if i == 0 else route[i - 1]
                b = route[i]
                for j in range(i + 1, n - 1):
                    c = route[j]
                    d2 = depot if j == n - 1 else route[j + 1]
                    delta = (d(a, c) + d(b, d2)) - (d(a, b) + d(c, d2))
                    if delta < best_delta - 1e-12:
                        best_delta = delta
                        best_i, best_j = i, j
            if best_i is not None:
                route = route[:best_i] + list(reversed(route[best_i:best_j + 1])) + route[best_j + 1:]
                improved = True
        return route

    routes = [improve_route(r) for r in routes]

    # Inter-route repair/local search: relocate and swap to reduce cost while keeping capacity
    route_loads = [sum(demand(c) for c in r) for r in routes]

    def total_cost(rs):
        return sum(route_cost(r) for r in rs)

    improved = True
    while improved:
        improved = False
        base_cost = total_cost(routes)

        # Relocate one customer between routes
        for i in range(len(routes)):
            if improved:
                break
            for pos in range(len(routes[i])):
                c = routes[i][pos]
                dc = demand(c)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    if route_loads[j] + dc > capacity:
                        continue
                    for ins in range(len(routes[j]) + 1):
                        new_routes = [r[:] for r in routes]
                        new_routes[i].pop(pos)
                        new_routes[j].insert(ins, c)
                        if len(new_routes[i]) == 0:
                            continue
                        # local improvements on affected routes
                        new_routes[i] = improve_route(new_routes[i])
                        new_routes[j] = improve_route(new_routes[j])
                        new_loads = route_loads[:]
                        new_loads[i] -= dc
                        new_loads[j] += dc
                        new_cost = total_cost(new_routes)
                        if new_cost + 1e-12 < base_cost:
                            routes = new_routes
                            route_loads = new_loads
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break

        if improved:
            continue

        # Pairwise swap between routes
        for i in range(len(routes)):
            if improved:
                break
            for j in range(i + 1, len(routes)):
                for pi in range(len(routes[i])):
                    for pj in range(len(routes[j])):
                        a = routes[i][pi]
                        b = routes[j][pj]
                        na = route_loads[i] - demand(a) + demand(b)
                        nb = route_loads[j] - demand(b) + demand(a)
                        if na > capacity or nb > capacity:
                            continue
                        new_routes = [r[:] for r in routes]
                        new_routes[i][pi], new_routes[j][pj] = b, a
                        new_routes[i] = improve_route(new_routes[i])
                        new_routes[j] = improve_route(new_routes[j])
                        new_cost = total_cost(new_routes)
                        if new_cost + 1e-12 < base_cost:
                            routes = new_routes
                            route_loads[i] = na
                            route_loads[j] = nb
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break

    # Final cleanup: remove any accidental depot if present
    routes = [[c for c in r if c != depot] for r in routes if r]
    return routes
