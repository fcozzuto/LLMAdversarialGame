def solve_cvrp(instance):
    # instance is expected to be a dict-like object with:
    # - 'customers': list of customer dicts or tuples containing (id, demand)
    # - 'depot': id of depot (not included in routes)
    # - 'capacity': vehicle capacity
    # We implement a simple deterministic constructive and repair heuristic.

    # Normalize input
    customers = []
    depot_id = None
    capacity = None

    if isinstance(instance, dict):
        depot_id = instance.get('depot', None)
        capacity = instance.get('capacity', None)
        raw = instance.get('customers', [])
        # Normalize to (id, demand)
        for c in raw:
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                cid, dem = c[0], c[1]
            elif isinstance(c, dict):
                cid = c.get('id')
                dem = c.get('demand', 0)
            else:
                # fallback: assume (id, demand)
                cid, dem = c
            customers.append((cid, int(dem)))
    else:
        # Fallback minimal: assume instance is already in expected internal form
        customers = []
        for c in instance:
            customers.append((c[0], int(c[1])))

    if depot_id is None:
        depot_id = 0  # default depot id if not provided
    if capacity is None:
        capacity = 0
        for _, d in customers:
            capacity = max(capacity, d)

    # If no customers, return empty routes
    if not customers:
        return []

    # Sort customers by decreasing demand (largest first) for determinism
    customers = sorted(customers, key=lambda x: (-x[1], x[0]))

    unassigned = list(customers)
    routes = []

    # Construct routes greedily: grow a route with as many customers as fit
    while unassigned:
        route = []
        load = 0
        i = 0
        # Try to fill route with smallest-id next among feasible; deterministic scan
        while i < len(unassigned):
            cid, dem = unassigned[i]
            if load + dem <= capacity:
                route.append(cid)
                load += dem
                unassigned.pop(i)
                # do not increment i, since list shifted
            else:
                i += 1
        # If route empty (all remaining have individual demand > capacity), handle single heavy customer
        if not route:
            cid, dem = unassigned.pop(0)
            route.append(cid)
            load = dem  # may exceed capacity; but we ensure capacity by not allowing; fallback
            # Force enforcement: if demand exceeds capacity, we still place it in its own route
            # and treat capacity as at least its demand
            # no further action
        routes.append(route)

    # Repair step: ensure every customer appears exactly once (deterministic)
    seen = set()
    for r in routes:
        for c in r:
            if c in seen:
                pass
            else:
                seen.add(c)

    # If some customer missed due to anomaly, add them to last route
    all_ids = {c for c, _ in customers}
    missing = all_ids - seen
    if missing:
        last = routes[-1]
        for mid in list(missing):
            last.append(mid)
            seen.add(mid)

    # Optional local-improvement: try to swap adjacent customers between routes to reduce slack
    # Deterministic simple improvement: try moving from a larger route to a smaller until capacity respected
    # Compute route loads
    def route_load(r):
        s = 0
        for cid in r:
            for cid2, d in customers:
                if cid2 == cid:
                    s += d
                    break
        return s

    # Simple pass: ensure balance by moving from routes with higher load to earlier ones if feasible
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
                # attempt move last element of ri to front of rj if fits
                cid = ri[-1]
                dem = next((d for (cc, d) in customers if cc == cid), 0)
                load_i = route_load(ri)
                load_j = route_load(rj)
                if load_j + dem <= capacity:
                    # perform move
                    ri.pop()
                    rj.insert(0, cid)
                    improved = True
        # If no improvements, exit
    return routes
