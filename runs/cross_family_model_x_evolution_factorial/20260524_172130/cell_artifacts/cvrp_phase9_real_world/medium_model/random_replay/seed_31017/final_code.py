def solve_cvrp(instance):
    """
    Deterministic constructive + repair CVRP solver.
    instance is expected as a dict-like object with:
      - 'customers': list of dicts with 'id', 'demand'
      - 'depot': id or 0 (not included in routes)
      - 'vehicle_capacity': int
      - optional 'distance' function or matrix is ignored for feasibility
    The function returns a list of routes, each a list of customer ids (excluding depot),
    partitioning all customers exactly once and not exceeding vehicle_capacity per route.
    """
    # Normalize input structure
    customers = []
    if isinstance(instance, dict):
        if 'customers' in instance:
            for c in instance['customers']:
                customers.append({'id': c['id'], 'demand': int(c['demand'])})
        else:
            raise ValueError("Instance must contain 'customers'.")
        capacity = int(instance.get('vehicle_capacity', 0))
    else:
        raise ValueError("Unsupported instance type.")
    if capacity <= 0:
        raise ValueError("Invalid vehicle_capacity.")

    # Deterministic order: sort by id to be interpretable
    customers.sort(key=lambda c: c['id'])

    # Simple greedy constructive: assign sequentially to current route until capacity would be exceeded, then start new route
    routes = []
    current_route = []
    current_load = 0

    for c in customers:
        d = c['demand']
        if d > capacity:
            # A single customer exceeds capacity; impossible to serve. To keep deterministic, create a pseudo-route with that customer alone.
            # But the constraint "Visit every customer exactly once and respect vehicle capacity" implies this is infeasible.
            # We'll still include it as its own route to maintain deterministic behavior, though it violates capacity.
            # Raise a clear error instead to indicate infeasibility.
            raise ValueError(f"Customer {c['id']} demand {d} exceeds vehicle capacity {capacity}.")

        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            routes.append(current_route)
            current_route = [c['id']]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Repair idea: ensure no route is empty and each customer appears exactly once
    seen = set()
    for r in routes:
        for cid in r:
            if cid in seen:
                raise ValueError("Duplicate customer detected in routes.")
            seen.add(cid)

    if len(seen) != len(customers):
        # In case some missing, attempt trivial fill (deterministic)
        missing = [c['id'] for c in customers if c['id'] not in seen]
        for cid in missing:
            # place in first route that can fit
            placed = False
            for r in routes:
                # retrieve demand
                d = next((c['demand'] for c in customers if c['id'] == cid), None)
                if d is None:
                    d = 0
                # compute current load
                load = sum(next((c['demand'] for c in customers if c['id'] == x), 0) for x in r)
                if load + d <= capacity:
                    r.append(cid)
                    placed = True
                    break
            if not placed:
                # create new route for this customer
                routes.append([cid])

    # Local search: pairwise swap adjacent customers across routes if improves balance without violating capacity
    # Deterministic: perform a fixed number of passes
    max_passes = max(1, len(routes))
    for _ in range(max_passes):
        improved = False
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j:
                    continue
                ri = routes[i]
                rj = routes[j]
                if not ri or not rj:
                    continue
                # Try moving last of ri to beginning of rj
                cid = ri[-1]
                # compute new loads
                di = next((c['demand'] for c in customers if c['id'] == cid), 0)
                load_i = sum(next((c['demand'] for c in customers if c['id'] == x), 0) for x in ri)
                load_j = sum(next((c['demand'] for c in customers if c['id'] == x), 0) for x in rj)
                if load_j + di <= capacity:
                    # perform move
                    ri2 = ri[:-1]
                    rj2 = [cid] + rj
                    routes[i] = ri2
                    routes[j] = rj2
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break

    # Final cleanup: remove empty routes if any
    routes = [r for r in routes if r]

    return routes
