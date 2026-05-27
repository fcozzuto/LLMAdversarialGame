def solve_cvrp(instance):
    # Instance expected as a dict-like with:
    # - "customers": list of dicts with "id", "x", "y", "demand"
    # - "vehicle_capacity": int or float
    # We will create a simple deterministic constructive solver with:
    # 1) sort customers by nondecreasing demand-to-distance heuristic (deterministic)
    # 2) build routes by filling one vehicle at a time (constructive)
    # 3) perform a simple local repair: swap to reduce wasted capacity (deterministic)
    # 4) ensure each customer appears exactly once, depot not included in routes

    # Helper: compute squared distance for determinism (no math import)
    def dist2(a, b):
        dx = a["x"] - b["x"]
        dy = a["y"] - b["y"]
        return dx*dx + dy*dy

    customers = instance.get("customers", [])
    n = len(customers)
    cap = instance.get("vehicle_capacity", 0)

    # If no customers or invalid capacity, return empty
    if n == 0 or cap <= 0:
        return []

    # Identify depot as a separate point (assuming not in customers)
    # We need a fixed ordering of customers. Build a simple key: demand / (distance to origin)
    # If origin not provided, assume depot at (0,0)
    depot = {"id": 0, "x": 0, "y": 0}
    for c in customers:
        if "id" not in c:
            c["id"] = c.get("index", 0)

    # Deterministic key for sorting
    def key_func(c):
        d = dist2(depot, c)
        # avoid division by zero
        denom = max(1, c.get("demand", 1))
        return (c.get("demand", 1) / (1 + d))  # simple heuristic

    # Normalize/id: ensure integer ids unique
    for idx, c in enumerate(customers):
        if "id" not in c:
            c["id"] = idx + 1

    # Construct a list of customer dicts with needed fields
    custs = []
    for c in customers:
        if "demand" not in c:
            c["demand"] = 1
        if "id" not in c:
            c["id"] = len(custs) + 1
        if "x" not in c or "y" not in c:
            c["x"] = 0
            c["y"] = 0
        custs.append({"id": c["id"], "demand": c["demand"], "x": c["x"], "y": c["y"]})

    # Sort deterministically by key_func
    custs.sort(key=key_func)

    # Construct routes greedily: fill one vehicle at a time
    routes = []
    i = 0
    used = set()

    while i < len(custs):
        route = []
        load = 0
        # add as many as fit
        j = i
        last_added = None
        while j < len(custs):
            c = custs[j]
            if c["id"] in used:
                j += 1
                continue
            demand = c["demand"]
            if load + demand <= cap:
                route.append(c["id"])
                load += demand
                used.add(c["id"])
                last_added = c
                j += 1
            else:
                break
        if not route:
            # If a single customer exceeds capacity, force it (to avoid infinite loop)
            c = custs[j]
            route.append(c["id"])
            used.add(c["id"])
            j += 1
        routes.append(route)
        i = j

    # If any customers missing (safety), add them to last route
    all_ids = set(c["id"] for c in custs)
    assigned = set(sum(routes, []))
    missing = list(all_ids - assigned)
    if missing:
        # try to append to last route if capacity allows
        for mid in missing:
            for r in routes:
                # find corresponding customer
                cid = mid
                c = next((cc for cc in custs if cc["id"] == cid), None)
                if c is None:
                    continue
                # compute current load of route (sum of demands of ids in route)
                load = sum(next(cc["demand"] for cc in custs if cc["id"] == rid) for rid in r)
                if load + c["demand"] <= cap:
                    r.append(cid)
                    break
            else:
                # if cannot fit anywhere, start new route
                routes.append([mid])

    # Simple repair: try to balance routes by swapping endpoints to reduce fragmentation
    # Repeat a small number of passes deterministically
    def route_load(r):
        return sum(next(cc["demand"] for cc in custs if cc["id"] == cid) for cid in r)

    improved = True
    passes = 2
    while improved and passes > 0:
        improved = False
        passes -= 1
        for a in range(len(routes)):
            for b in range(len(routes)):
                if a == b:
                    continue
                ra = routes[a]
                rb = routes[b]
                if not ra or not rb:
                    continue
                # Try moving last of a to end of b
                cid = ra[-1]
                c = next(cc for cc in custs if cc["id"] == cid)
                la = route_load(ra) - c["demand"]
                lb = route_load(rb)
                if lb + c["demand"] <= cap and la + c["demand"] <= cap:
                    # perform move
                    ra.pop()
                    rb.append(cid)
                    improved = True

    return routes
