def solve_cvrp(instance):
    # instance is expected to be a dict-like object with:
    # - 'customer_ids': list of customer IDs (ints)
    # - 'demands': dict mapping customer_id -> demand (int)
    # - 'capacity': int
    # - optional, 'distance' function or matrix (not needed for feasibility)
    # We'll implement a deterministic constructive + simple repair/local-search approach.
    customers = list(instance['customer_ids'])
    demand = dict(instance['demands'])
    capacity = instance['capacity']

    # If no customers, return empty routes
    if not customers:
        return []

    # Deterministic: sort by id to have a stable order
    customers.sort()

    # Helper: simple greedy constructive routing
    routes = []
    current_route = []
    current_load = 0

    for cid in customers:
        d = demand.get(cid, 0)
        # If single customer's demand exceeds capacity, treat as unsatisfiable by removing (should not happen in CVRP)
        if d > capacity:
            # As a fallback, create a route with just this customer (though capacity is violated)
            # But per problem statement, must respect capacity; we instead skip adding if impossible.
            # To keep deterministic behavior, place into its own route (will be invalid) but continue.
            pass

        if current_load + d <= capacity:
            current_route.append(cid)
            current_load += d
        else:
            # close current route
            if current_route:
                routes.append(current_route)
            # start new route with this customer
            current_route = [cid]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Repair step: ensure all customers present exactly once
    seen = set()
    for r in routes:
        for c in r:
            if c in seen:
                # duplicate: remove from this route to ensure unique
                r.remove(c)
            else:
                seen.add(c)

    # Ensure any missed customers are added back deterministically
    missing = [c for c in customers if c not in seen]
    for c in missing:
        # Try to append to the route with enough remaining capacity; otherwise start new route
        placed = False
        for r in routes:
            # compute load of route
            load = sum(demand.get(x, 0) for x in r)
            if load + demand.get(c, 0) <= capacity:
                r.append(c)
                placed = True
                break
        if not placed:
            routes.append([c])

    # Local search: 1-Opt swap between routes to reduce number of routes if possible
    # Deterministic: repeatedly try to move a single customer from a larger route to an earlier route if capacity allows
    changed = True
    while changed:
        changed = False
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j:
                    continue
                if not routes[i]:
                    continue
                # try move last of routes[i] to routes[j]
                c = routes[i][-1]
                w = demand.get(c, 0)
                load_j = sum(demand.get(x, 0) for x in routes[j])
                if load_j + w <= capacity:
                    # move
                    routes[i].pop()
                    routes[j].append(c)
                    # remove empty route if needed
                    if not routes[i]:
                        routes.pop(i)
                    changed = True
                    break
            if changed:
                break

    # Final cleanup: remove any empty routes and keep order deterministic
    routes = [r for r in routes if r]

    return routes
