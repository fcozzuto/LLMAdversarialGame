def solve_cvrp(instance):
    depot = instance["depot_index"]
    customer_ids = list(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    dist = instance["distance_matrix"]

    # Phase 0: helper to compute route cost
    def route_cost(order):
        cost = 0
        cur = depot
        for n in order:
            cost += dist[cur][n]
            cur = n
        return cost

    # Phase 1: constructive: build routes greedily by nearest-feasible extension
    remaining = set(customer_ids)
    routes = []
    while remaining:
        route = []
        load = 0
        current = depot
        while True:
            candidates = [c for c in remaining if load + demands[c] <= capacity]
            if not candidates:
                break
            nxt = min(candidates, key=lambda n: (dist[current][n], demands[n], n))
            route.append(nxt)
            remaining.remove(nxt)
            load += demands[nxt]
            current = nxt
        routes.append(route)

    # Phase 2: deterministic repair: try to merge small routes if beneficial and feasible
    merged = True
    while merged:
        merged = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                if not routes[i] or not routes[j]:
                    continue
                load_i = sum(demands[c] for c in routes[i])
                load_j = sum(demands[c] for c in routes[j])
                if load_i + load_j <= capacity:
                    new_order = routes[i] + routes[j]
                    cost_old = route_cost(routes[i]) + route_cost(routes[j])
                    cost_new = route_cost(new_order)
                    if cost_new <= cost_old:
                        routes[i] = new_order
                        routes.pop(j)
                        merged = True
                        break
            if merged:
                break

    # Phase 3: local improvement: intra-route 2-opt-like swaps and small inter-route moves
    improved = True
    while improved:
        improved = False
        # intra-route improvements
        for r_idx, route in enumerate(routes):
            if len(route) < 3:
                continue
            n = len(route)
            best_route = route
            best_cost = route_cost(route)
            for a in range(n - 1):
                for b in range(a + 1, n):
                    new_route = route[:]
                    new_route[a], new_route[b] = new_route[b], new_route[a]
                    c = route_cost(new_route)
                    if c < best_cost:
                        best_cost = c
                        best_route = new_route
                        improved = True
                        break
                if improved:
                    break
            if improved:
                routes[r_idx] = best_route
        # inter-route move: try moving one tail from a route to another if feasible and beneficial
        if not improved:
            for i in range(len(routes)):
                if not routes[i]:
                    continue
                node = routes[i][-1]
                w = demands[node]
                for j in range(len(routes)):
                    if i == j or not routes[j]:
                        continue
                    load_j = sum(demands[c] for c in routes[j])
                    if load_j + w <= capacity:
                        new_routes = [r[:] for r in routes]
                        new_routes[i] = new_routes[i][:-1]
                        new_routes[j] = new_routes[j] + [node]
                        def total_cost(rs):
                            c = 0
                            for r in rs:
                                cur = depot
                                for x in r:
                                    c += dist[cur][x]
                                    cur = x
                            return c
                        if total_cost(new_routes) < total_cost(routes):
                            routes = new_routes
                            improved = True
                            break
                if improved:
                    break

    # Phase 4: ensure all customers covered exactly once (defensive)
    seen = set()
    for r in routes:
        for c in r:
            seen.add(c)
    missing = set(customer_ids) - seen
    if missing:
        # attach missing as singleton routes (shouldn't normally happen in constructive steps)
        for m in sorted(missing):
            routes.append([m])

    # Final cleanup: remove empty routes if any
    routes = [r for r in routes if r]

    return routes
