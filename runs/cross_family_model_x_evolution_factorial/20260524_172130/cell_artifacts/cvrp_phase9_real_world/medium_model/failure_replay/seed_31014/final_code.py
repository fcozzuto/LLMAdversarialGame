def solve_cvrp(instance):
    depot = instance["depot_index"]
    customers = set(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    matrix = instance["distance_matrix"]

    # Heuristic: constructive with simple repairs and local improvement.
    # 1) Build initial routes by greedily adding nearest feasible customer
    # 2) If a route cannot accept any new customer, start a new route
    # 3) Attempt two small post-assembly improvements: swap between routes and 2-opt-like intra-route adjustments
    routes = []

    # Helper: compute total demand of a route
    def route_load(route):
        return sum(demands[n] for n in route)

    # Step 1: constructive build
    remaining = set(customers)
    while remaining:
        route = []
        load = 0
        current = depot
        while True:
            # candidates that fit
            feasible = [n for n in remaining if load + demands[n] <= capacity]
            if not feasible:
                break
            # tie-breaker: closest to current, then smaller demand, then smaller id
            nxt = min(feasible, key=lambda n: (matrix[current][n], demands[n], n))
            route.append(nxt)
            remaining.remove(nxt)
            load += demands[nxt]
            current = nxt
        if route:
            routes.append(route)
        else:
            # If no one fits (shouldn't happen if capacity >= max demand), force one
            # pick the largest-demand remaining customer
            nxt = max(remaining, key=lambda n: demands[n])
            routes.append([nxt])
            remaining.remove(nxt)

    # Step 2: repair - try to merge small routes if possible to reduce count without violating capacity
    i = 0
    while i < len(routes):
        j = i + 1
        while j < len(routes):
            ri = routes[i]
            rj = routes[j]
            if route_load(ri) + route_load(rj) <= capacity:
                # merge by appending rj to ri
                routes[i] = ri + rj
                routes.pop(j)
                # restart inner loop for this i
                j = i + 1
                continue
            j += 1
        i += 1

    # Step 3: simple local improvement
    # 3a: swap between routes to reduce total distance
    def route_distance(route):
        if not route:
            return 0
        d = 0
        prev = depot
        for n in route:
            d += matrix[prev][n]
            prev = n
        # return to depot not required by problem spec for routes, so omit
        return d

    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                ri = routes[i]
                rj = routes[j]
                if route_load(ri) + route_load(rj) <= capacity:
                    # try moving a single tail node from ri to end of rj or vice versa
                    for take_from_i in range(len(ri)):
                        node = ri[-1 - take_from_i]
                        if route_load(ri) - demands[node] + route_load(rj) <= capacity:
                            # perform transfer
                            new_ri = ri[:-1 - take_from_i] if take_from_i >= 0 else ri[:]
                            new_rj = rj + [node]
                            old_dist = route_distance(ri) + route_distance(rj)
                            new_dist = route_distance(new_ri) + route_distance(new_rj)
                            if new_dist < old_dist:
                                routes[i] = new_ri
                                routes[j] = new_rj
                                improved = True
                                break
                    if improved:
                        break
            if improved:
                break

    # 3b: intra-route improvement: try to remove unnecessary detours by local reordering (simple 2-opt style)
    for idx, route in enumerate(routes):
        if len(route) <= 2:
            continue
        best = route[:]
        best_dist = route_distance(best)
        n = len(route)
        # try all 2-opt swaps within route
        for a in range(n - 1):
            for b in range(a + 2, n):
                new_route = best[:]
                new_route[a + 1 : b + 1] = reversed(new_route[a + 1 : b + 1])
                d = route_distance(new_route)
                if d < best_dist:
                    best = new_route
                    best_dist = d
        routes[idx] = best

    return routes
