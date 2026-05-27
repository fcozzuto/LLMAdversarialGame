def solve_cvrp(instance):
    """
    Deterministic constructive + simple repair local-search CVRP solver.
    - instance: dict with keys:
        - 'customers': list of dicts with 'id', 'demand', 'x', 'y'
        - 'depot': dict with 'id', 'x', 'y'
        - 'vehicle_capacity': int
    Returns:
        list of routes, each a list of customer ids (excluding depot)
    """
    # Extract data
    customers = instance.get('customers', [])
    depot = instance.get('depot', {'id': 0, 'x': 0, 'y': 0})
    C = instance.get('vehicle_capacity', 0)

    # Helper: distance (Euclidean)
    def dist(a, b):
        dx = a['x'] - b['x']
        dy = a['y'] - b['y']
        return (dx*dx + dy*dy) ** 0.5

    # Build a simple list of customers with id and demand
    elems = []
    for c in customers:
        cid = c.get('id')
        dmd = c.get('demand', 0)
        x = c.get('x', 0)
        y = c.get('y', 0)
        elems.append({'id': cid, 'demand': dmd, 'x': x, 'y': y})

    # Sort customers by a simple heuristic: increasing angle around depot for determinism
    # Compute angle using arctan2; avoid import by using math; but imports not allowed.
    # Implement a simple quadrant-based angle proxy to keep deterministic ordering.
    def quadrant(p):
        dx = p['x'] - depot['x']
        dy = p['y'] - depot['y']
        # Normalize to avoid division; return tuple (q, dy, dx) for stable sort
        if dx >= 0 and dy >= 0:
            q = 0
        elif dx < 0 <= dy:
            q = 1
        elif dx <= 0 and dy < 0:
            q = 2
        else:
            q = 3
        # Basic distance as tie-breaker
        d = (dx*dx + dy*dy)
        return (q, d)
    elems.sort(key=lambda p: quadrant(p))

    # Construct routes greedily: fill until capacity, then start new route
    routes = []
    current_route = []
    current_load = 0

    # Process in deterministic order
    for c in elems:
        if c['demand'] > C:
            # Impossible to satisfy; skip (or could split, but we skip to keep deterministic)
            continue
        if current_load + c['demand'] > C:
            if current_route:
                routes.append(current_route)
            current_route = [c['id']]
            current_load = c['demand']
        else:
            current_route.append(c['id'])
            current_load += c['demand']

    if current_route:
        routes.append(current_route)

    # Simple repair: ensure every customer appears exactly once (no duplicates in this construction)
    seen = set()
    for r in routes:
        newr = []
        for cid in r:
            if cid not in seen:
                newr.append(cid)
                seen.add(cid)
        r[:] = newr

    # If any route became empty due to repair, remove
    routes = [r for r in routes if r]

    # Local improvement: try to merge adjacent routes if total <= capacity
    i = 0
    while i < len(routes) - 1:
        r1 = routes[i]
        r2 = routes[i+1]
        # Check combined demand
        # Build quick demand map from ids by scanning original customers
        demand_map = {c['id']: c['demand'] for c in customers}
        d1 = sum(demand_map.get(cid, 0) for cid in r1)
        d2 = sum(demand_map.get(cid, 0) for cid in r2)
        if d1 + d2 <= C:
            # Merge
            routes[i] = r1 + r2
            del routes[i+1]
            # stay at same i to attempt further merges
        else:
            i += 1

    return routes
