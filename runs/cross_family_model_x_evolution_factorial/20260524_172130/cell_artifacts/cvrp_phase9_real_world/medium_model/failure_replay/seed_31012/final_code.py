def solve_cvrp(instance):
    """
    Deterministic constructive CVRP solver with simple repair/local-search ideas.
    - instance is a dict with keys:
        - 'customers': dict of id -> {'demand': int, 'x': ..., 'y': ...}
        - 'depot': id (not included in customers)
        - 'capacity': int
    - returns: list of routes, each route is a list of customer ids (no depot)
    """
    customers = instance.get('customers', {})
    capacity = instance.get('capacity', 0)
    depot_id = instance.get('depot', None)

    # Prepare a deterministic order: sort by id
    ids = sorted(customers.keys())

    # Initialize routes with one vehicle per customer in order, then merge greedily
    routes = []
    for cid in ids:
        d = customers[cid]['demand']
        if d > capacity:
            # If a single customer exceeds capacity, cannot serve (degenerate case)
            # Create an empty route for safety (will be ignored by caller)
            routes.append([cid])
            continue
        placed = False
        # Try to put into existing route if capacity allows
        for r in routes:
            load = sum(customers[c]['demand'] for c in r)
            if load + d <= capacity:
                r.append(cid)
                placed = True
                break
        if not placed:
            routes.append([cid])

    # Local repair: try to merge routes pairwise if capacity allows, in a deterministic way
    merged = True
    while merged:
        merged = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                ri = routes[i]
                rj = routes[j]
                if not ri or not rj:
                    continue
                load_i = sum(customers[c]['demand'] for c in ri)
                load_j = sum(customers[c]['demand'] for c in rj)
                # Check if concatenation is feasible
                if load_i + load_j <= capacity:
                    # Merge j into i
                    routes[i] = ri + rj
                    routes.pop(j)
                    merged = True
                    break
            if merged:
                break

    # Simple local improvement: swap within routes to reduce count of routes
    # Try to move a customer from a longer route to an earlier one if feasible
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j:
                    continue
                ri = routes[i]
                rj = routes[j]
                if not ri:
                    continue
                # Try moving last of ri to rj
                cust = ri[-1]
                d = customers[cust]['demand']
                load_j = sum(customers[c]['demand'] for c in rj)
                if load_j + d <= capacity:
                    routes[i] = ri[:-1]
                    routes[j] = rj + [cust]
                    # If any route becomes empty, remove it
                    if not routes[i]:
                        routes.pop(i)
                    improved = True
                    break
            if improved:
                break

    # Final cleanup: remove any empty routes
    routes = [r for r in routes if r]

    return routes
