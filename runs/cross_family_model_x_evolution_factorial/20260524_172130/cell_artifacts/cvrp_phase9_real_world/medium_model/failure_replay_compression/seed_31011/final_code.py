def solve_cvrp(instance):
    """
    Deterministic constructive + repair CVRP solver with simple local improvements.
    - instance is expected to be a dict-like with keys:
        'customers': list of dicts with 'id','demand','x','y'
        'depot': dict with 'id','x','y'
        'vehicle_capacity': int
    Returns:
        routes: list of routes, each a list of customer ids (excluding depot)
    """
    # Extract data with safe defaults
    customers = instance.get('customers', [])
    depot = instance.get('depot', {'id': 0, 'x': 0, 'y': 0})
    capacity = instance.get('vehicle_capacity', 0)

    # Build local simple distance
    def dist(a, b):
        return ((a['x'] - b['x'])**2 + (a['y'] - b['y'])**2) ** 0.5

    # Map by id for quick access
    custs = {c['id']: c for c in customers}
    depot_id = depot.get('id', 0)

    # Start with all customers sorted by distance to depot (nearest first)
    # This is a deterministic constructive heuristic: repeatedly take nearest
    # feasible customer to current route end.
    remaining = set(custs.keys())

    routes = []

    # Precompute distances from depot and between customers
    dep = {'id': depot_id, 'x': depot.get('x', 0), 'y': depot.get('y', 0)}
    # Build simple neighbor function
    while remaining:
        route = []
        load = 0
        current = dep

        # Pick the nearest feasible customer to start the route
        candidates = sorted(list(remaining), key=lambda cid: dist(dep, custs[cid]))
        started = False
        for cid in candidates:
            d = custs[cid]['demand']
            if load + d <= capacity:
                route.append(cid)
                load += d
                remaining.remove(cid)
                current = custs[cid]
                started = True
                break
        if not started:
            # If no single customer fits (capacity issue), declare failure to proceed
            # Return empty routes to indicate infeasibility
            return []

        # Continue adding nearest feasible customers to current route
        while remaining:
            # Recompute best next among remaining
            next_candidates = sorted(list(remaining),
                                     key=lambda cid: dist(current, custs[cid]))
            added = False
            for cid in next_candidates:
                d = custs[cid]['demand']
                if load + d <= capacity:
                    route.append(cid)
                    load += d
                    remaining.remove(cid)
                    current = custs[cid]
                    added = True
                    break
            if not added:
                break  # route is full or no feasible next

        routes.append(route)

    # Optional simple local improvement: try to merge adjacent routes if possible by swap/shift
    # Deterministic, lightweight improvement: attempt moving a last customer from a route to the next route if capacity allows
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)-1):
            if not routes[i]:
                continue
            last = routes[i][-1]
            cap_i = capacity - sum(custs[c]['demand'] for c in routes[i])
            # Try move last to next route if it fits
            if routes[i+1]:
                next_load = sum(custs[c]['demand'] for c in routes[i+1])
            else:
                next_load = 0
            if next_load + custs[last]['demand'] <= capacity:
                # Move
                routes[i] = routes[i][:-1]
                routes[i+1].insert(0, last)
                improved = True
                # If route becomes empty, remove it
                if not routes[i]:
                    routes.pop(i)
                break

    return routes
