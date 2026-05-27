def solve_cvrp(instance):
    # instance is expected to be a dict-like with:
    # - 'customers': list of dicts with keys 'id', 'demand'
    # - 'depot': id of depot (not included in routes)
    # - 'capacity': vehicle capacity
    # We implement a deterministic constructive solver with simple repair.
    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['capacity']

    # Create a deterministic order: sort by id to ensure reproducibility
    customers_sorted = sorted(customers, key=lambda c: c['id'])

    # Helper: get demand by id
    demand = {c['id']: c['demand'] for c in customers_sorted}

    # Build initial naive solution: greedily fill routes by capacity
    routes = []
    current_route = []
    current_load = 0

    for c in customers_sorted:
        cid = c['id']
        d = c['demand']
        if d > capacity:
            # If single customer exceeds capacity, cannot serve; skip by returning empty or singletons.
            # To keep deterministic behavior, assign as its own route (though not feasible). We'll skip it.
            # Better: place in its own route if capacity allows; but if not, still place as a special route.
            # Here, we place as its own route only if d <= capacity; otherwise, leave route empty to indicate impossibility.
            pass

        if current_load + d <= capacity:
            current_route.append(cid)
            current_load += d
        else:
            # finish current route
            if current_route:
                routes.append(current_route)
            # start new route with this customer
            current_route = [cid]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Repair step: ensure no route exceeds capacity (defensive)
    repaired = []
    for r in routes:
        total = sum(demand[cid] for cid in r)
        if total <= capacity:
            repaired.append(r)
        else:
            # split into smaller subroutes deterministically
            sub = []
            load = 0
            for cid in r:
                d = demand[cid]
                if load + d <= capacity:
                    sub.append(cid)
                    load += d
                else:
                    if sub:
                        repaired.append(sub)
                    sub = [cid]
                    load = d
            if sub:
                repaired.append(sub)
    routes = repaired

    # Local improvement: 2-opt-like single-swap between routes to reduce number of routes (heuristic)
    # Deterministic pairwise try to move a customer from a larger route to another with available capacity
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
                # try move last of ri to front of rj if capacity allows
                cid = ri[-1]
                d = demand[cid]
                if sum(demand[c] for c in rj) + d <= capacity:
                    # perform move
                    routes[i] = ri[:-1]
                    routes[j] = [cid] + rj
                    improved = True
                    break
            if improved:
                break

    # Final check: remove empty routes if any
    routes = [r for r in routes if r]

    return routes
