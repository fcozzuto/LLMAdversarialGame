def solve_cvrp(instance):
    # instance is assumed as a dict-like object with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id or placeholder (not included in routes)
    # - 'vehicle_capacity': int
    # - optional: 'dist' function or matrix; if not, we'll assume Euclidean via coordinates

    # Normalize input
    customers = []
    if isinstance(instance, dict):
        if 'customers' in instance:
            customers = list(instance['customers'])
        else:
            # try to extract from common keys
            customers = []
        capacity = instance.get('vehicle_capacity', None)
        depot = instance.get('depot', None)
        dist = instance.get('dist', None)
        coords = None
        if dist is None:
            coords = instance.get('coords', None)
        # If there is no demand info, assume 1
        for c in customers:
            if 'demand' not in c:
                c['demand'] = 1
    else:
        # fallback: nothing
        return []

    if capacity is None:
        # default to sum of demands
        capacity = sum(c['demand'] for c in customers) or 1

    # If dist function not provided, create a simple Manhattan distance using coordinates if available
    def distance(a, b):
        if dist is not None:
            try:
                return dist(a, b)
            except Exception:
                pass
        # fallback: use coordinates if present
        xa = a.get('x', 0)
        ya = a.get('y', 0)
        xb = b.get('x', 0)
        yb = b.get('y', 0)
        return abs(xa - xb) + abs(ya - yb)

    # Create a small helper to get a numeric index for deterministic sorting
    def key_for(c):
        return c['id']

    # Deterministic constructive: sort customers by nondecreasing demand density proxy
    # We'll compute a simple score: distance from depot (if known) and demand
    depot_node = {'id': depot} if depot is not None else None

    # If we have coordinates for depot and customers, compute distance from depot
    depot_loc = None
    if depot is not None:
        for c in customers:
            if c['id'] == depot:
                depot_loc = c
                break

    # Build a simple sequence: sort by (distance from depot, then id)
    if depot_loc is not None:
        def dist_from_depot(c):
            return distance(depot_loc, c)
        customers_sorted = sorted(customers, key=lambda c: (dist_from_depot(c), c['id']))
    else:
        # Without depot location, sort by id then demand
        customers_sorted = sorted(customers, key=lambda c: (c['id'], c['demand']))

    # Construct routes greedily: fill a route until capacity would be exceeded, then start new
    routes = []
    current_route = []
    current_load = 0

    for c in customers_sorted:
        d = c['demand']
        if d > capacity:
            # impossible to satisfy this single customer; skip (invalid in strict sense)
            # To keep deterministic behavior, place anyway by splitting capacity-relation
            # Here, we place as many as possible by creating a separate route for this customer
            pass
        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            if current_route:
                routes.append(current_route)
            current_route = [c['id']]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Simple local repair: try to improve by swapping adjacent routes' tail/head if capacity allows
    # Iterate small number of passes deterministically
    improved = True
    while improved:
        improved = False
        for i in range(len(routes) - 1):
            A = routes[i]
            B = routes[i+1]
            if not A or not B:
                continue
            # Try move last of A to B
            lastA = A[-1]
            # find demand of lastA
            dem = None
            for c in customers:
                if c['id'] == lastA:
                    dem = c['demand']
                    break
            if dem is None:
                continue
            # compute total loads
            loadA = 0
            for cid in A:
                for c in customers:
                    if c['id'] == cid:
                        loadA += c['demand']
                        break
            loadB = 0
            for cid in B:
                for c in customers:
                    if c['id'] == cid:
                        loadB += c['demand']
                        break
            if loadB + dem <= capacity:
                # perform move
                newA = A[:-1]
                newB = B + [lastA]
                routes[i] = newA
                routes[i+1] = newB
                improved = True
                break
        if improved:
            continue

        # Try merge adjacent routes if feasible to reduce number of routes
        for i in range(len(routes) - 1):
            A = routes[i]
            B = routes[i+1]
            if not A or not B:
                continue
            # compute loads
            loadA = sum(next((c['demand'] for c in customers if c['id'] == cid), 0) for cid in A)
            loadB = sum(next((c['demand'] for c in customers if c['id'] == cid), 0) for cid in B)
            if loadA + loadB <= capacity:
                routes[i] = A + B
                routes.pop(i+1)
                improved = True
                break

    return routes
