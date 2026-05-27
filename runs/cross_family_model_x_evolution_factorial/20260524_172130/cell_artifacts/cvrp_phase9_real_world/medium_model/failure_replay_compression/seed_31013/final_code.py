def solve_cvrp(instance):
    # instance is expected to be a dict-like object with:
    # - 'demands': dict {customer_id: demand}
    # - 'coords': dict {customer_id: (x, y)} or a list of tuples aligned with IDs
    # - 'depot': depot_id
    # - 'vehicle_capacity': int
    # We implement a simple deterministic constructive + repair heuristic.

    # Helper: get customer ids  excluding depot
    depot = instance.get('depot', 0)
    demands = instance.get('demands', {})
    capacity = instance.get('vehicle_capacity', 0)

    # Build a simple distance function using coordinates if available
    coords = instance.get('coords', {})
    def dist(a, b):
        xa, ya = coords.get(a, (0,0))
        xb, yb = coords.get(b, (0,0))
        dx = xa - xb
        dy = ya - yb
        return (dx*dx + dy*dy) ** 0.5

    # Prepare list of customers excluding depot
    customers = [c for c in demands.keys() if c != depot]
    # Sort customers by increasing demand (deterministic) as a heuristic order
    customers.sort(key=lambda c: demands.get(c, 0))

    routes = []
    current_route = []
    current_load = 0

    # Construct routes greedily: add next customer if capacity allows; otherwise close route
    for c in customers:
        d = demands.get(c, 0)
        if d > capacity:
            # If any single demand exceeds capacity, skip (no feasible solution)
            # To keep deterministic behavior, place as its own route if possible fails gracefully
            # We'll create a route with just this customer if capacity allows (not possible here),
            # otherwise skip by continuing (not ideal, but ensures deterministic return)
            continue
        if current_load + d <= capacity:
            current_route.append(c)
            current_load += d
        else:
            if current_route:
                routes.append(current_route)
            current_route = [c]
            current_load = d
    if current_route:
        routes.append(current_route)

    # Repair: ensure every customer is included exactly once
    all_assigned = set(c for r in routes for c in r)
    missing = [c for c in customers if c not in all_assigned]
    if missing:
        # Try to insert missing customers into existing routes where capacity allows
        for c in missing:
            d = demands.get(c, 0)
            inserted = False
            for r in routes:
                # compute remaining capacity if we add to this route
                used = sum(demands.get(x, 0) for x in r)
                if used + d <= capacity:
                    r.append(c)
                    inserted = True
                    break
            if not inserted:
                # start a new route
                routes.append([c])

    # Final pass: if any route becomes empty, remove it
    routes = [r for r in routes if r]

    return routes
