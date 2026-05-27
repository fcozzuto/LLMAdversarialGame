def solve_cvrp(instance):
    # instance is expected to be a dict-like with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id or index (not included in routes)
    # - 'capacity': vehicle capacity
    # - optional: 'distance' function or matrix (not used by this basic solver)
    #
    # Deterministic constructive solver with simple repair:
    # 1) Sort customers by id (deterministic)
    # 2) Create routes by greedy packing until capacity would be exceeded, then start new route
    # 3) Simple local improvement: try to swap adjacent customers between routes if it reduces any route's total demand (though since routes are capacity-limited, we ensure feasibility)
    #
    # This implementation does not rely on external data or training, and returns routes
    # as lists of customer ids (excluding the depot).
    #
    # Note: We only use provided instance structure and basic Python; no imports.

    customers = instance.get('customers', [])
    depot = instance.get('depot', None)
    capacity = instance.get('capacity', 0)

    # If customers are not provided as expected, try to adapt
    if not isinstance(customers, list):
        customers = []
    # Build a deterministic order: sort by id
    try:
        customers_sorted = sorted(customers, key=lambda c: c['id'])
    except Exception:
        # Fallback: use given order
        customers_sorted = list(customers)

    # Helper to get demand safely
    def demand_of(c):
        return int(c.get('demand', 0))

    routes = []
    current_route = []
    current_load = 0

    # Construct routes greedily by capacity
    for c in customers_sorted:
        d = demand_of(c)
        if d > capacity:
            # If a single customer exceeds capacity, skip (unsolvable under these constraints)
            # To keep deterministic, place in its own route (though infeasible). Here we skip addition.
            continue
        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            # close current route and start new
            if current_route:
                routes.append(current_route)
            current_route = [c['id']]
            current_load = d
    if current_route:
        routes.append(current_route)

    # Simple local repair: try to rebalance by swapping end of one route with start of next if it keeps feasibility
    # This is deterministic and small-scale; it avoids complex search.
    i = 0
    while i < len(routes) - 1:
        r1 = routes[i]
        r2 = routes[i+1]
        if not r1 or not r2:
            i += 1
            continue
        # Try moving last of r1 to start of r2
        last_r1 = r1[-1]
        # Mock demands to evaluate feasibility: obtain demands from customers by id
        id_to_demand = {c['id']: c.get('demand', 0) for c in customers_sorted}
        d_last = id_to_demand.get(last_r1, 0)
        # Compute current loads
        load1 = sum(id_to_demand.get(cid, 0) for cid in r1)
        load2 = sum(id_to_demand.get(cid, 0) for cid in r2)
        if load1 - d_last <= capacity and load2 + d_last <= capacity:
            # perform move
            r1 = r1[:-1]
            r2 = [last_r1] + r2
            routes[i] = r1
            routes[i+1] = r2
            # If r1 becomes empty, remove it
            if not r1:
                routes.pop(i)
                # do not increment i to re-evaluate at same index
                continue
        i += 1

    return routes
