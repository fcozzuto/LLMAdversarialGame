def solve_cvrp(instance):
    """
    Deterministic constructive + simple local-improvement CVRP solver with failure_replay style logic.
    Assumptions about instance:
    - instance is a dict-like object with keys:
        - 'customer_ids': list of customer IDs (ints), excluding depot
        - 'demands': dict id -> demand (int)
        - 'coords': dict id -> (x, y) or a function to compute distance
        - 'capacity': int, vehicle capacity
        - 'dist': function taking two ids (or ids and depot) returning distance; if not provided, will compute Euclidean using coords
        - 'depot': id of depot (commonly 0)
    We will implement a simple constructive heuristic:
    - Sort customers by nondecreasing demand-to-distance heuristic
    - Greedy insert into first feasible route
    - If a customer cannot fit any existing route, start new route
    - After construction, perform a simple 2-opt-like local improvement on each route: try to move a adjacent customer pair to reduce distance if feasible
    - Always produce deterministic output
    """
    # Basic helper: distance
    depot = instance.get('depot', 0)
    customers = list(instance.get('customer_ids', []))
    demands = instance.get('demands', {})
    capacity = instance.get('capacity', 0)
    coords = instance.get('coords', {})
    distf = instance.get('dist', None)

    def distance(a, b):
        if distf is not None:
            return distf(a, b)
        xa, ya = coords.get(a, (0, 0))
        xb, yb = coords.get(b, (0, 0))
        return ((xa - xb) ** 2 + (ya - yb) ** 2) ** 0.5

    # Ensure depot distance helper
    def route_distance(route):
        if not route:
            return 0
        d = 0
        prev = depot
        for cid in route:
            d += distance(prev, cid)
            prev = cid
        d += distance(prev, depot)
        return d

    # Heuristic key: smaller demand first or by distance to depot
    # Deterministic: sort by (demand, id)
    sorted_customers = sorted(customers, key=lambda cid: (demands.get(cid, 0), cid))

    routes = []
    # Constructive phase: greedy insert into first feasible route
    for cid in sorted_customers:
        dem = demands.get(cid, 0)
        placed = False
        # Try existing routes
        for r in routes:
            cap_used = sum(demands.get(x, 0) for x in r)
            if cap_used + dem <= capacity:
                r.append(cid)
                placed = True
                break
        if not placed:
            # create new route
            routes.append([cid])

    # Repair/improve: simple intra-route 2-opt-like local improvement
    # For each route, try to reorder locally by swapping adjacent customers if feasible and reduces distance
    improved = True
    while improved:
        improved = False
        for r in routes:
            if len(r) < 2:
                continue
            n = len(r)
            # try all adjacent swaps
            for i in range(n - 1):
                cand = r[:]
                cand[i], cand[i+1] = cand[i+1], cand[i]
                # check feasibility: still same set, capacity unaffected, so feasible
                # compute distance difference
                old = distance(depot, cand[0])
                # compute full distance more accurately
                def full_dist(seq):
                    d = 0
                    prev = depot
                    for x in seq:
                        d += distance(prev, x)
                        prev = x
                    d += distance(prev, depot)
                    return d
                if full_dist(r) > full_dist(cand):
                    r[:] = cand
                    improved = True
                    break
            if improved:
                break

    # Ensure every customer appears exactly once
    seen = set()
    for r in routes:
        for c in r:
            seen.add(c)
    # If some customer missing due to anomaly, append at end of last route if possible or create new
    missing = [c for c in customers if c not in seen]
    for c in missing:
        # place into first route if space, else new route
        placed = False
        for r in routes:
            cap_used = sum(demands.get(x, 0) for x in r)
            if cap_used + demands.get(c, 0) <= capacity:
                r.append(c)
                placed = True
                break
        if not placed:
            routes.append([c])

    # Final cleanup: remove empty routes if any
    routes = [r for r in routes if r]

    return routes
