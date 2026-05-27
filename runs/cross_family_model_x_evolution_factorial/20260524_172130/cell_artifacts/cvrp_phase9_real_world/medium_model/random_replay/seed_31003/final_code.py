def solve_cvrp(instance):
    depot = instance["depot_index"]
    customers = set(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    matrix = instance["distance_matrix"]

    # Deterministic constructive solver with repair-like and local tweaks
    # Strategy:
    # - Build routes greedily by always selecting the nearest feasible customer.
    # - If a customer cannot be added due to capacity, close the route and start a new one.
    # - After initial construction, perform a simple intra-route local improvement:
    #   try to swap the last customer with earlier ones if it reduces distance (without breaking feasibility).
    # - Do a simple inter-route merge check: if two routes can be merged by moving a prefix/suffix
    #   while respecting capacity, merge them in a deterministic way.
    routes = []

    # Precompute a deterministic ordering for customers to ensure reproducibility
    # We'll use the natural order of customer_ids as a tie-breaker when distances are equal.
    sorted_customers = sorted(list(customers))

    # Initial constructive phase: nearest-feasible greedy
    remaining = set(sorted_customers)
    while remaining:
        route = []
        load = 0
        current = depot

        while True:
            # Feasible candidates: not yet visited and capacity allows
            feasible = [node for node in remaining if load + demands[node] <= capacity]
            if not feasible:
                break

            # Pick the closest feasible candidate from current location
            nxt = min(feasible, key=lambda node: (matrix[current][node], node))
            route.append(nxt)
            remaining.remove(nxt)
            load += demands[nxt]
            current = nxt

        routes.append(route)

    # Repair-like intra-route improvement: try moving the last node of a route earlier if improvement
    for r_idx, route in enumerate(routes):
        if len(route) < 2:
            continue
        current_load = sum(demands[n] for n in route)
        # Try to insert the last node earlier in the same route if it reduces distance
        last = route[-1]
        best_pos = len(route) - 1
        best_gain = 0
        # compute baseline distance
        baseline = 0
        prev = depot
        for n in route:
            baseline += matrix[prev][n]
            prev = n
        baseline += matrix[prev][depot]

        # Try removing last and re-inserting at positions 0..len-2
        prefix = route[:-1]
        for pos in range(len(prefix) + 1):
            new_route = prefix[:pos] + [last] + prefix[pos:]
            # Check feasibility: total demand unchanged, so feasible in terms of capacity
            d = 0
            prev = depot
            dist = 0
            for n in new_route:
                dist += matrix[prev][n]
                prev = n
            dist += matrix[prev][depot]
            gain = baseline - dist
            if gain > best_gain:
                best_gain = gain
                best_pos = pos
        if best_pos != len(route) - 1:
            # Apply improvement
            routes[r_idx] = route[:-1]
            routes[r_idx].insert(best_pos, last)

    # Inter-route merge attempt: try to merge adjacent routes if feasible and improves total distance
    merged = True
    while merged:
        merged = False
        for i in range(len(routes) - 1):
            r1 = routes[i]
            r2 = routes[i + 1]
            if not r1 or not r2:
                continue
            load1 = sum(demands[n] for n in r1)
            load2 = sum(demands[n] for n in r2)
            # Try to move a suffix of r1 to start of r2
            for cut in range(1, len(r1) + 1):
                tail = r1[cut - 1:]
                head = r1[:cut - 1]
                new_r1 = head
                new_r2 = tail + r2
                if sum(demands[n] for n in new_r2) <= capacity:
                    # compute new distance
                    def route_distance(rt):
                        if not rt:
                            return 0
                        d = 0
                        prev = depot
                        for n in rt:
                            d += matrix[prev][n]
                            prev = n
                        d += matrix[prev][depot]
                        return d
                    old_dist = route_distance(r1) + route_distance(r2)
                    new_dist = route_distance(new_r1) + route_distance(new_r2)
                    if new_dist < old_dist:
                        routes[i] = new_r1
                        routes[i + 1] = new_r2
                        merged = True
                        break
            if merged:
                break

    return routes
