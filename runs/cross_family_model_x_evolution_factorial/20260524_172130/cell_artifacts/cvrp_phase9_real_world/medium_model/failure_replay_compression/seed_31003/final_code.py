def solve_cvrp(instance):
    # instance is assumed to be a dict-like with:
    # - 'depot': depot_id
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'dist': function taking two ids and returning distance
    #
    # We implement a deterministic constructive solver with simple repair
    # and local-improvement steps, using a simple nearest-eligible heuristic
    # and a capacity-based bin packing into routes.

    depot = instance['depot']
    customers = [c for c in instance['customers']]
    dist = instance['dist']
    capacity = instance['capacity']
    # If not provided, set defaults
    if capacity is None:
        capacity = max(c['demand'] for c in customers) * 2

    # Build a simple clustering by sorting by id (deterministic order)
    # and greedily fill routes by nearest-following within capacity
    remaining = {c['id']: c['demand'] for c in customers}
    by_id = {c['id']: c for c in customers}

    # Precompute a simple linear order: sort by id to be deterministic
    order = sorted(remaining.keys())

    # Helper: build one route by starting from depot, add best next eligible customer deterministically
    routes = []
    while True:
        # start a new route
        route = []
        load = 0
        current = depot
        # Build a candidate set: since we don't track visits globally here, we use remaining
        # Choose next by the smallest distance from current to an eligible customer
        candidates = [cid for cid in order if remaining[cid] > 0]
        if not candidates:
            break
        # Determine next customer deterministically: pick the closest in terms of distance
        next_id = None
        best_d = None
        for cid in candidates:
            d = dist(current, cid)
            if best_d is None or d < best_d:
                best_d = d
                next_id = cid
        if next_id is None:
            break
        # Check capacity
        if remaining[next_id] > capacity - load:
            # cannot fit, end route if it has any customers
            if route:
                routes.append(route)
                continue
            else:
                # Single customer exceeds capacity (shouldn't happen in valid instances)
                # skip it
                remaining[next_id] = 0
                continue
        # add next_id
        route.append(next_id)
        load += remaining[next_id]
        remaining[next_id] = 0
        current = next_id
        # Continue adding while capacity allows, selecting nearest from current
        while True:
            candidates = [cid for cid in order if remaining[cid] > 0]
            if not candidates:
                break
            next_id = None
            best_d = None
            for cid in candidates:
                d = dist(current, cid)
                if best_d is None or d < best_d:
                    best_d = d
                    next_id = cid
            if next_id is None:
                break
            if remaining[next_id] > capacity - load:
                break
            route.append(next_id)
            load += remaining[next_id]
            remaining[next_id] = 0
            current = next_id
        routes.append(route)

    # Repair pass: ensure all customers covered exactly once; if any missing, assign to first route with space
    covered = set(cid for r in routes for cid in r)
    missing = [cid for cid in order if cid not in covered]
    if missing:
        # Try to insert missing into existing routes if capacity permits
        for cid in missing:
            demand = by_id[cid]['demand']
            # find a route with available capacity
            best_route_idx = None
            best_pos = None
            best_extra = None
            for idx, r in enumerate(routes):
                # compute load
                load = sum( by_id[c]['demand'] for c in r )
                if load + demand <= capacity:
                    # place at end (simple deterministic)
                    best_route_idx = idx
                    best_pos = len(r)
                    best_extra = 0
                    break
            if best_route_idx is not None:
                routes[best_route_idx].append(cid)
            else:
                # create a new route for this single customer
                routes.append([cid])

    # Local improvement: try to swap adjacent in same route to reduce total distance (greedy)
    def route_distance(r):
        if not r:
            return 0
        d = dist(depot, r[0])
        for i in range(len(r)-1):
            d += dist(r[i], r[i+1])
        d += dist(r[-1], depot)
        return d

    improved = True
    while improved:
        improved = False
        for r_idx, r in enumerate(routes):
            if len(r) < 2:
                continue
            # try swapping each adjacent pair
            for i in range(len(r)-1):
                new_r = r[:]
                new_r[i], new_r[i+1] = new_r[i+1], new_r[i]
                if route_distance(new_r) < route_distance(r):
                    routes[r_idx] = new_r
                    improved = True

    # Remove any empty routes (in case)
    routes = [r for r in routes if r]

    return routes
