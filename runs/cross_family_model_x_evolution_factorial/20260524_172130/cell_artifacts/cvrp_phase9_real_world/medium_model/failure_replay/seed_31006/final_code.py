def solve_cvrp(instance):
    """
    Deterministic constructive CVRP solver with simple repair/local-search.
    - instance is a dict with keys:
        'customers': list of dicts with 'id', 'demand', 'x','y'
        'depot': {'id':0, 'x':..., 'y':...}
        'vehicle_capacity': int
    Returns:
        routes: list of lists of customer ids (excluding depot)
    """
    # Basic checks and extraction
    customers = instance.get('customers', [])
    depot = instance.get('depot', {'id': 0, 'x': 0, 'y': 0})
    capacity = instance.get('vehicle_capacity', 0)

    # Normalize data: map id to data
    cust = {c['id']: {'demand': c.get('demand', 0), 'x': c.get('x', 0), 'y': c.get('y', 0)} for c in customers}
    # Ensure deterministic order: sort by id
    ids = sorted(cust.keys())

    # Helper: simple Euclidean distance between two points
    def dist(a_id, b_id):
        if a_id == 0:
            ax, ay = depot['x'], depot['y']
        else:
            ax, ay = cust[a_id]['x'], cust[a_id]['y']
        if b_id == 0:
            bx, by = depot['x'], depot['y']
        else:
            bx, by = cust[b_id]['x'], cust[b_id]['y']
        dx = ax - bx
        dy = ay - by
        return (dx*dx + dy*dy) ** 0.5

    # Start with a simple constructive heuristic: repeatedly take the nearest unassigned customer
    # to the current route's last customer, respecting capacity. Start each route from depot.
    unserved = set(ids)
    routes = []

    # Precompute a simple nearest-neighbor order per start to keep deterministic
    # We'll implement a deterministic greedy: for each route, pick the nearest unserved to the depot to start,
    # then continue with nearest to last until capacity would be exceeded; if no one fits, start new route.
    while unserved:
        # start a new route from depot
        route = []
        load = 0
        current = 0  # depot id
        # choose first customer: the one with smallest distance from depot (deterministic by id tie-break)
        candidates = sorted(list(unserved), key=lambda cid: (dist(0, cid), cid))
        if not candidates:
            break
        first = candidates[0]
        demand = cust[first]['demand']
        if demand > capacity:
            # cannot serve this single customer; skip to avoid infinite loop
            unserved.remove(first)
            # Infeasible case; skip
            continue
        route.append(first)
        load += demand
        unserved.remove(first)
        current = first

        # extend route
        while True:
            # among remaining unserved, find nearest to current that fits remaining capacity
            remaining = [cid for cid in unserved if cust[cid]['demand'] <= (capacity - load)]
            if not remaining:
                break
            # deterministic: pick nearest to current, tie-break by smaller id
            next_c = min(remaining, key=lambda cid: ( (dist(current, cid)), cid ))
            route.append(next_c)
            load += cust[next_c]['demand']
            unserved.remove(next_c)
            current = next_c

        routes.append(route)

    # Repair step: ensure every customer appears exactly once (safety)
    seen = set()
    for r in routes:
        for c in r:
            seen.add(c)
    # If any missing due to capacity issues, append them as singletons (worst-case)
    missing = [c for c in ids if c not in seen]
    for m in missing:
        # start a new route for this single customer
        routes.append([m])

    # Local-improvement: try to swap adjacent customers between routes to reduce distance
    # Simple 1-opt like: attempt to move a customer to another route if capacity allows and distance improves
    improved = True
    while improved:
        improved = False
        for i, r1 in enumerate(routes):
            for j, r2 in enumerate(routes):
                if i == j or not r1 or not r2:
                    continue
                # try moving last of r1 to front of r2 if capacity allows
                c1 = r1[-1]
                d1 = cust[c1]['demand']
                cap2 = capacity - sum(cust[c]['demand'] for c in r2)
                if d1 <= cap2:
                    # compute distance delta: remove c1 from end of r1 and insert at start of r2
                    def route_distance(rs):
                        if not rs:
                            return 0
                        total = 0.0
                        prev = 0
                        for cid in rs:
                            total += dist(prev, cid)
                            prev = cid
                        total += dist(prev, 0)
                        return total
                    new_r1 = r1[:-1]
                    new_r2 = [c1] + r2
                    old = route_distance(r1) + route_distance(r2)
                    new = route_distance(new_r1) + route_distance(new_r2)
                    if new < old:
                        routes[i] = new_r1
                        routes[j] = new_r2
                        improved = True
        if improved:
            continue

    return routes
