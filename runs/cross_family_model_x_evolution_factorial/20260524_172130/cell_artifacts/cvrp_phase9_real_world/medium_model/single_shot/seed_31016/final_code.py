def solve_cvrp(instance):
    # instance is expected as a dict with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': dict or id (not used directly)
    # - 'capacity': int, vehicle capacity
    # For minimal deterministic solver:
    # 1) sort customers by nondecreasing demand-to-id heuristic (stable)
    # 2) greedily assign to current route until adding next would exceed capacity, then start new route
    # 3) return list of routes as lists of customer ids (no depot)

    # Validate basic structure
    if not isinstance(instance, dict):
        raise ValueError("instance must be a dict")
    customers = instance.get('customers', [])
    capacity = instance.get('capacity', None)

    if capacity is None:
        raise ValueError("capacity must be provided in instance")

    # Build a stable list of customers with id and demand
    custs = []
    for c in customers:
        cid = c.get('id')
        d = c.get('demand', 0)
        if cid is None:
            continue
        custs.append({'id': cid, 'demand': d})

    # Sort by a deterministic key: first by demand ascending, then by id to break ties
    custs.sort(key=lambda x: (x['demand'], x['id']))

    routes = []
    current_route = []
    current_load = 0

    for c in custs:
        d = c['demand']
        if d > capacity:
            # If a single customer exceeds capacity, skip (cannot serve); to keep deterministic behavior,
            # place as its own route (though infeasible). In a strict CVRP, this should be infeasible.
            # We'll still place it alone if it doesn't break overall policy.
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([c['id']])
            continue

        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            # finish current route and start a new one
            if current_route:
                routes.append(current_route)
            current_route = [c['id']]
            current_load = d

    if current_route:
        routes.append(current_route)

    return routes
