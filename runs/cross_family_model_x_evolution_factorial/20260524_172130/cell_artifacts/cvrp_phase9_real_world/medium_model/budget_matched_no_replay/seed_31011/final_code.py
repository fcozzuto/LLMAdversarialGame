def solve_cvrp(instance):
    """
    Deterministic constructive and local-improvement CVRP solver.
    Assumptions about instance:
    - instance is a dict with keys:
        - 'customers': list of customer dicts, each with 'id', 'demand'
        - 'depot': dict with 'id' (not used in route lists)
        - 'vehicle_capacity': int
        - optionally 'distances': function(did1, did2) -> distance or a 2D array
    - We rely only on the provided fields; we do not import modules.
    The solver:
    - sorts customers by non-increasing demand (largest first)
    - builds routes by filling vehicles up to capacity in that order (constructive)
    - then performs a simple intra-route 2-opt style local improvement by swapping adjacent customers if it reduces distance
    - uses a consistent deterministic distance function if distances are provided, else a simple surrogate: distance = abs(a_id - b_id)
    - returns a list of routes; each route is a list of customer ids (excluding depot)
    """
    # Helpers (no imports)
    # Get customers
    customers = instance.get('customers', [])
    depot_id = instance.get('depot', {}).get('id', 0)
    capacity = instance.get('vehicle_capacity', 0)

    # Distance function
    dist_func = None
    distances = instance.get('distances', None)
    if distances:
        # distances may be a dict of tuples or a 2D container
        if callable(distances):
            dist_func = distances
        else:
            # assume 2D dict-like with keys (a,b) or ids
            def dist_func(a, b, _dist=distances):
                # try mapping
                try:
                    return _dist[(a, b)]
                except Exception:
                    try:
                        return _dist[a][b]
                    except Exception:
                        return abs(a - b)
    else:
        # simple surrogate distance by id difference
        def dist_func(a, b):
            return abs(a - b)

    # If no customers, return empty
    if not customers:
        return []

    # Prepare list of (id, demand)
    custs = [(c['id'], c.get('demand', 0)) for c in customers]

    # Sort by decreasing demand for determinism
    custs.sort(key=lambda x: (-x[1], x[0]))

    # Construct routes: fill vehicles sequentially
    routes = []
    current_route = []
    current_load = 0

    for cid, dem in custs:
        if dem > capacity:
            # single customer exceeds capacity; cannot serve -- skip (degenerate)
            # To keep deterministic behavior, place as its own route if possible; else skip
            if dem <= capacity:
                pass
            # We skip impossible customer
            continue
        if current_load + dem <= capacity:
            current_route.append(cid)
            current_load += dem
        else:
            # close current route
            if current_route:
                routes.append(current_route)
            # start new route
            current_route = [cid]
            current_load = dem

    if current_route:
        routes.append(current_route)

    # If any customer missing due to edge case, ensure each customer appears exactly once:
    # Build a set of served ids from routes
    served = set()
    for r in routes:
        for cid in r:
            served.add(cid)

    all_ids = set(cid for cid, _ in custs)
    missing = sorted(list(all_ids - served), key=lambda x: x)

    # Try to append missing customers to last route if capacity allows, deterministically
    for cid in missing:
        # need its demand; find from input
        dem = next((d for (i, d) in custs if i == cid), 0)
        if routes:
            last = routes[-1]
            # find its total demand
            load = 0
            for x in last:
                dx = next((d for (i, d) in custs if i == x), 0)
                load += dx
            if load + dem <= capacity:
                last.append(cid)
                served.add(cid)
                continue
        # else start new route
        routes.append([cid])
        served.add(cid)

    # Local improvement: intra-route 2-opt-like swap of adjacent customers
    # Define helper to compute route distance (assuming depot at start/end but not included in route)
    def route_distance(route):
        if not route:
            return 0
        total = 0
        prev = depot_id
        for cid in route:
            total += dist_func(prev, cid)
            prev = cid
        total += dist_func(prev, depot_id)
        return total

    def swap_improvement(route):
        improved = True
        route = route[:]
        best_dist = route_distance(route)
        n = len(route)
        while improved and n >= 2:
            improved = False
            for i in range(n - 1):
                # swap i and i+1
                new_r = route[:]
                new_r[i], new_r[i+1] = new_r[i+1], new_r[i]
                d = route_distance(new_r)
                if d < best_dist:
                    route = new_r
                    best_dist = d
                    improved = True
                    break
        return route

    for idx in range(len(routes)):
        routes[idx] = swap_improvement(routes[idx])

    return routes
