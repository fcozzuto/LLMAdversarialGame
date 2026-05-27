def solve_cvrp(instance):
    """
    Deterministic constructive + repair CVRP solver using simple rules.
    Assumes instance is a dict with:
      - 'customers': list of dicts with 'id', 'x','y','demand'
      - 'depot': dict with 'id','x','y'
      - 'vehicle_capacity': int
    Returns:
      - routes: list of routes, each route is a list of customer ids (excluding depot)
    """
    # Minimal defensive extraction
    customers = []
    depot_id = None
    capacity = None

    if isinstance(instance, dict):
        if 'customers' in instance:
            for c in instance['customers']:
                # ensure id exists
                if 'id' in c:
                    customers.append({'id': c['id'], 'demand': c.get('demand', 0), 'coords': (c.get('x', 0.0), c.get('y', 0.0))})
        if 'depot' in instance and isinstance(instance['depot'], dict):
            depot_id = instance['depot'].get('id', 0)
        capacity = instance.get('vehicle_capacity', None)
        if capacity is None:
            capacity = 10  # fallback
    else:
        return []

    # Prepare deterministic order: sort by angle around depot or by id if depot unknown
    # Compute simple deterministic route construction: greedily fill with nearest feasible customer by id order if ties
    # Since we are not allowed to import math, implement a simple manual distance
    depot = (0.0, 0.0)
    if instance and isinstance(instance, dict) and 'depot' in instance and isinstance(instance['depot'], dict):
        depot = (instance['depot'].get('x', 0.0), instance['depot'].get('y', 0.0))
    # If we lack coordinates, fall back to id order
    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx*dx + dy*dy) ** 0.5

    # Attach coordinates to customers if available
    for c in customers:
        c['coords'] = c.get('coords', (0.0, 0.0))

    # Create a mapping from id to customer for easy access
    id_to_c = {c['id']: c for c in customers}

    # Determine order: sort by id as default deterministic order
    ordered = sorted(customers, key=lambda c: c['id'])

    routes = []
    current_load = 0
    current_route = []

    # Simple constructive fill: try to add next customer if capacity allows, otherwise start new route
    for c in ordered:
        d = c['demand']
        if d > capacity:
            # skip absurd demand; can't satisfy; treat as its own route if possible (though not feasible)
            # We'll skip to avoid infinite loop
            continue
        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            # finish current route
            if current_route:
                routes.append(current_route)
            # start new route with this customer
            current_route = [c['id']]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Repair step: ensure every customer appears exactly once by construction; quick verification
    seen = set()
    for r in routes:
        for cid in r:
            if cid in seen:
                # duplicate found; remove from this route
                r.remove(cid)
            else:
                seen.add(cid)

    # If any missing customers exist due to repair, append as singletons
    all_ids = set(c['id'] for c in customers)
    missing = all_ids - seen
    for mid in sorted(missing):
        routes.append([mid])

    return routes
