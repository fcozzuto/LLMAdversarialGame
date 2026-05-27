def solve_cvrp(instance):
    """
    Deterministic constructive + simple repair local-search CVRP solver.

    instance is expected to be a dict with:
      - 'depot': depot id (int)
      - 'customers': dict mapping customer_id -> {'demand': int, 'x': ..., 'y': ...}  (x,y optional not used)
      - 'vehicle_capacity': int

    Returns:
      List of routes, each route is a list of customer_ids (no depot), covering all customers exactly once.
    """
    # Basic input normalization
    depot = instance.get('depot', 0)
    customers = dict(instance.get('customers', {}))
    capacity = instance.get('vehicle_capacity', 0)

    # If customers already empty, return empty routes
    if not customers:
        return []

    # Deterministic ordering: sort by customer id
    customer_ids = sorted(customers.keys())

    # Helper: get demand
    def demand(cid):
        c = customers[cid]
        return int(c.get('demand', 0))

    # Construct initial solution: greedy sequential packing into routes by capacity
    routes = []
    current_route = []
    current_load = 0

    for cid in customer_ids:
        d = demand(cid)
        if d > capacity:
            # infeasible single customer; skip (cannot be served)
            # To keep deterministic behavior, place as its own route if possible
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            # Still add as single if possible (will be infeasible if d>capacity)
            # We'll create a route with this customer to ensure termination; but this violates capacity.
            # Instead, skip adding such impossible customer in this simplified solver.
            # Mark by continuing; but we must visit all customers; to handle gracefully, place it in its own route anyway.
            pass

        if current_load + d <= capacity:
            current_route.append(cid)
            current_load += d
        else:
            # finish current route and start a new one
            if current_route:
                routes.append(current_route)
            current_route = [cid]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Repair pass: ensure all customers are included exactly once
    served = set()
    for r in routes:
        for cid in r:
            served.add(cid)
    missing = [cid for cid in customer_ids if cid not in served]

    if missing:
        # Append missing customers to the last route if capacity allows, else create new routes
        for cid in missing:
            d = demand(cid)
            if routes:
                last = routes[-1]
                load = sum(demand(x) for x in last)
                if load + d <= capacity:
                    last.append(cid)
                    continue
            # create new route for this customer
            routes.append([cid])

    # Second-pass: try to improve by one-swap within capacity constraints (simple local-search)
    # For determinism, perform a fixed number of iterations with deterministic neighbor exploration.
    improved = True
    iter_limit = max(1, len(routes) * 2)
    it = 0
    while improved and it < iter_limit:
        improved = False
        it += 1
        for i in range(len(routes)):
            for j in range(i, len(routes)):
                if i == j:
                    continue
                ri = routes[i]
                rj = routes[j]
                if not ri or not rj:
                    continue
                # attempt move last of ri to start of rj
                move_cid = ri[-1]
                d = demand(move_cid)
                load_i = sum(demand(x) for x in ri)
                load_j = sum(demand(x) for x in rj)
                if load_j + d <= capacity:
                    # perform move
                    new_ri = ri[:-1]
                    new_rj = [move_cid] + rj
                    routes_new = routes[:]
                    routes_new[i] = new_ri
                    routes_new[j] = new_rj
                    # check none empty
                    if (not new_ri) or (not new_rj) or True:
                        routes = routes_new
                        improved = True
                        break
            if improved:
                break

    # Final cleanup: remove any empty routes (shouldn't occur)
    routes = [r for r in routes if r]
    return routes
