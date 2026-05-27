def solve_cvrp(instance):
    # instance is expected to be a dict-like with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id (not included in routes)
    # - 'capacity': vehicle capacity
    # If structure differs, attempt common keys gracefully.

    # Helper: extract data
    customers = instance.get('customers') or []
    capacity = instance.get('capacity') or instance.get('vehicle_capacity') or 0

    # Normalize into lists of (id, demand)
    data = []
    for c in customers:
        cid = c.get('id')
        d = c.get('demand', 0)
        data.append((cid, d))

    # If no customers, return empty routes
    if not data:
        return []

    # Sort customers deterministically by (demand, id) to create stable initial order
    data.sort(key=lambda x: (x[1], x[0]))

    # Construct initial routes by simple greedy packing in given order
    routes = []
    current_route = []
    current_load = 0

    for cid, demand in data:
        if demand > capacity:
            # If a single customer exceeds capacity, cannot serve; skip as isolated infeasible
            # To keep deterministic behavior, place it alone in route (even if infeasible) to indicate failure handling
            # (But we avoid breaking the requirement; return empty route set for safety)
            return []

        if current_load + demand <= capacity:
            current_route.append(cid)
            current_load += demand
        else:
            # finish current route
            routes.append(current_route)
            current_route = [cid]
            current_load = demand

    if current_route:
        routes.append(current_route)

    # Local improvement: try to merge routes if any feasible improvement by simple swap-like step
    # We perform a deterministic single pass improvement: try to move smallest-demand customers to earlier routes if capacity allows.
    # Build index by route
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j or not routes[i] or not routes[j]:
                    continue
                # Try move last of routes[j] to front of routes[i] if fits
                cid = routes[j][-1]
                # find demand for cid
                dem = next((d for (cc, d) in data if cc == cid), None)
                if dem is None:
                    continue
                load_i = sum(next((d for (cc, d) in data if cc == x), 0) for x in routes[i])
                if load_i + dem <= capacity:
                    # perform move
                    routes[j].pop()
                    routes[i].insert(0, cid)
                    improved = True
                    break
            if improved:
                break

    # Return the routes as lists of customer ids (excluding depot)
    return routes
