def solve_cvrp(instance):
    # Instance expected structure (deterministic, no imports):
    # instance = {
    #   'customers': {id: {'demand': int, 'x': float, 'y': float}, ...},
    #   'depot': id,  # not included in routes
    #   'vehicle_capacity': int
    # }
    # We implement a deterministic constructive method with simple repair/local-search ideas.

    # Validate basic structure
    if not isinstance(instance, dict):
        return []
    customers = instance.get('customers', {})
    depot = instance.get('depot', None)
    capacity = instance.get('vehicle_capacity', None)

    if depot is None or capacity is None:
        # If depot not specified, assume 0 and empty solution
        return []

    # Gather customer ids in deterministic order: sort by id to be reproducible
    ids = sorted(customers.keys())

    # Helper: pick next unassigned customer with smallest id
    unassigned = set(ids)
    routes = []

    # Simple constructive: repeatedly fill a route by adding smallest-id customers until capacity reached
    while unassigned:
        load = 0
        route = []
        # deterministic inner loop
        for cid in sorted(unassigned):
            demand = customers[cid].get('demand', 0)
            if load + demand <= capacity:
                route.append(cid)
                load += demand
        # If no one fits (shouldn't happen if single customer demand <= capacity), break to avoid infinite loop
        if not route:
            # force add one with smallest demand to make progress
            cid = min(unassigned, key=lambda k: customers[k].get('demand', 0))
            route.append(cid)
            load += customers[cid].get('demand', 0)

        # Commit route: remove assigned customers from unassigned
        for cid in route:
            unassigned.discard(cid)

        routes.append(route)

    # Local repair: ensure each customer appears exactly once (deterministic)
    seen = set()
    repaired = []
    for r in routes:
        new_r = []
        for cid in r:
            if cid not in seen:
                new_r.append(cid)
                seen.add(cid)
        if new_r:
            repaired.append(new_r)

    # If any customer missing due to repair, append as singleton routes in order
    for cid in ids:
        if cid not in seen:
            repaired.append([cid])
            seen.add(cid)

    return repaired
