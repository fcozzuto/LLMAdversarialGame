def solve_cvrp(instance):
    # Instance is expected to be a dict-like with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id (not used in routes)
    # - 'capacity': vehicle capacity
    # For simplicity and determinism, we assume:
    # - customers are given as a list of (id, demand) pairs in 'customers'
    # - depot is located outside, and not included in routes
    #
    # We implement a simple constructive algorithm:
    # 1. Sort customers by non-increasing demand (largest first) for stability.
    # 2. Build routes by filling until capacity, then start new route.
    # 3. Apply a basic repair: if a single customer's demand exceeds capacity, split (not expected in valid instances).
    # 4. A tiny local improvement: try to swap end of one route with start of next if it reduces total load imbalance (deterministic).
    #
    # The function returns a list of routes, each a list of customer ids (not including depot).

    # Extract data from instance with robust defaults
    customers = instance.get('customers', [])
    capacity = instance.get('capacity', 0)
    # Normalize to a list of (id, demand)
    custs = []
    for c in customers:
        cid = c.get('id', None)
        demand = c.get('demand', 0)
        if cid is None:
            continue
        custs.append((cid, demand))

    # If no customers, return empty routes
    if not custs:
        return []

    # Sort by demand descending for deterministic constructive packing
    custs.sort(key=lambda x: (-x[1], x[0]))

    routes = []
    current_route = []
    current_load = 0

    # Construct routes by filling up to capacity
    for cid, demand in custs:
        if demand > capacity:
            # If a single demand exceeds capacity, split the customer (defensive; not typical)
            # Here, we create a route with no other customers and "pretend" splitting by multiple same ids.
            # Since we cannot include depot or duplicates in the problem, we treat as an error route.
            # For determinism, place the customer alone in its own route (even if over capacity) to honor visitation.
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([cid])
            continue

        if current_load + demand <= capacity:
            current_route.append(cid)
            current_load += demand
        else:
            # close current route and start new
            routes.append(current_route)
            current_route = [cid]
            current_load = demand

    if current_route:
        routes.append(current_route)

    # Simple local improvement: try to swap the end of a route with the start of the next to reduce wasted space
    for i in range(len(routes) - 1):
        r1 = routes[i]
        r2 = routes[i + 1]
        if not r1 or not r2:
            continue
        # Try moving last of r1 to front of r2 if feasible
        last_r1 = r1[-1]
        demand_last = next((d for (cid, d) in custs if cid == last_r1), None)
        if demand_last is None:
            continue
        # compute loads
        load_r1 = sum(d for (cid, d) in custs if cid in r1)
        load_r2 = sum(d for (cid, d) in custs if cid in r2)
        if load_r1 - demand_last + load_r2 + demand_last <= capacity:  # trivial check; actually always false because replaced
            pass
        # A simpler deterministic check: if moving last from r1 to r2 keeps both within capacity, perform swap
        if (sum(d for (cid, d) in custs if cid in r1) - demand_last <= capacity and
            sum(d for (cid, d) in custs if cid in r2) + demand_last <= capacity):
            # move last_r1 from r1 to front of r2
            new_r1 = r1[:-1]
            new_r2 = [last_r1] + r2
            routes[i] = new_r1
            routes[i + 1] = new_r2

    # Final normalization: remove any empty routes
    routes = [r for r in routes if r]

    return routes
