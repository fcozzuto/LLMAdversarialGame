def solve_cvrp(instance):
    def get_any(obj, keys, default=None):
        if isinstance(obj, dict):
            for k in keys:
                if k in obj:
                    return obj[k]
        return default

    def is_num(x):
        return isinstance(x, (int, float)) and not isinstance(x, bool)

    depot = get_any(instance, ["depot", "depot_id", "start", "origin"], 0)
    capacity = get_any(instance, ["capacity", "vehicle_capacity", "cap"], None)

    customers = get_any(instance, ["customers", "nodes", "points", "locations"], None)
    coords = {}
    demand = {}

    if isinstance(customers, dict):
        for k, v in customers.items():
            coords[k] = get_any(v, ["coord", "coords", "position", "pos", "location"], None)
            demand[k] = get_any(v, ["demand", "load"], 0)
    elif isinstance(customers, list):
        for i, v in enumerate(customers):
            cid = get_any(v, ["id", "node_id", "customer_id"], i)
            coords[cid] = get_any(v, ["coord", "coords", "position", "pos", "location"], None)
            demand[cid] = get_any(v, ["demand", "load"], 0)

    if not coords:
        raw_coords = get_any(instance, ["coords", "coordinates", "xy", "points_by_id"], None)
        if isinstance(raw_coords, dict):
            for k, v in raw_coords.items():
                coords[k] = v
        elif isinstance(raw_coords, list):
            for i, v in enumerate(raw_coords):
                coords[i] = v

    if not demand:
        raw_demands = get_any(instance, ["demands", "loads"], None)
        if isinstance(raw_demands, dict):
            demand.update(raw_demands)
        elif isinstance(raw_demands, list):
            for i, v in enumerate(raw_demands):
                demand[i] = v

    if capacity is None:
        if isinstance(instance, dict):
            cap_keys = ["capacity", "vehicle_capacity", "cap"]
            for k in cap_keys:
                if k in instance and is_num(instance[k]):
                    capacity = instance[k]
                    break
    if capacity is None:
        capacity = 10**18

    all_ids = set(coords.keys()) | set(demand.keys())
    if depot in all_ids:
        all_ids.remove(depot)
    if not all_ids:
        return []

    # Fill missing demands with 0
    for cid in list(all_ids):
        if cid not in demand:
            demand[cid] = 0

    def dist(a, b):
        ca = coords.get(a, None)
        cb = coords.get(b, None)
        if ca is None or cb is None:
            return 0.0 if a == b else 1.0
        ax, ay = ca[0], ca[1]
        bx, by = cb[0], cb[1]
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    # If coordinates exist, use angle-based ordering around depot for constructive sweep.
    customers_list = list(all_ids)
    if depot in coords and all(k in coords for k in customers_list):
        dx0, dy0 = coords[depot][0], coords[depot][1]

        def angle(cid):
            x, y = coords[cid][0] - dx0, coords[cid][1] - dy0
            # deterministic quadrant + slope ordering without imports
            if x == 0 and y == 0:
                return (0, 0.0, cid)
            if x >= 0 and y >= 0:
                quad = 0
            elif x < 0 and y >= 0:
                quad = 1
            elif x < 0 and y < 0:
                quad = 2
            else:
                quad = 3
            slope = y / x if x != 0 else (10**18 if y >= 0 else -10**18)
            return (quad, slope, cid)

        customers_list.sort(key=angle)
    else:
        customers_list.sort()

    # Initial sweep/greedy construction.
    routes = []
    unserved = customers_list[:]

    # Simple capacity-aware nearest insertion from current end.
    while unserved:
        route = []
        load = 0
        current = depot

        # start with earliest feasible remaining customer, or minimum demand if all small.
        feasible = [cid for cid in unserved if demand.get(cid, 0) <= capacity]
        if not feasible:
            # force one customer to avoid infinite loop; capacity infeasible instance.
            cid = unserved.pop(0)
            routes.append([cid])
            continue

        # choose seed: nearest to depot among feasible
        seed = min(feasible, key=lambda c: (dist(depot, c), demand.get(c, 0), c))
        route.append(seed)
        load += demand.get(seed, 0)
        unserved.remove(seed)
        current = seed

        while True:
            candidates = [cid for cid in unserved if load + demand.get(cid, 0) <= capacity]
            if not candidates:
                break
            # nearest neighbor with slight bias toward filling capacity
            best = None
            best_key = None
            for cid in candidates:
                d = dist(current, cid)
                slack = capacity - (load + demand.get(cid, 0))
                key = (d, slack, demand.get(cid, 0), cid)
                if best is None or key < best_key:
                    best = cid
                    best_key = key
            route.append(best)
            load += demand.get(best, 0)
            unserved.remove(best)
            current = best

        routes.append(route)

    # Repair: move any missing customers into routes if any mismatch occurred.
    seen = set()
    for r in routes:
        for c in r:
            if c != depot:
                seen.add(c)
    missing = [c for c in customers_list if c not in seen]
    if missing:
        for cid in missing:
            placed = False
            for r in routes:
                load = 0
                for c in r:
                    load += demand.get(c, 0)
                if load + demand.get(cid, 0) <= capacity:
                    r.append(cid)
                    placed = True
                    break
            if not placed:
                routes.append([cid])

    # Local search: 2-opt within each route for geometric improvement (interpretable, deterministic).
    if depot in coords and all(k in coords for k in customers_list):
        def route_cost(r):
            if not r:
                return 0.0
            cst = dist(depot, r[0])
            for i in range(len(r) - 1):
                cst += dist(r[i], r[i + 1])
            cst += dist(r[-1], depot)
            return cst

        improved = True
        while improved:
            improved = False
            for ri in range(len(routes)):
                r = routes[ri]
                n = len(r)
                if n < 4:
                    continue
                base = route_cost(r)
                best_r = r
                best_cost = base
                for i in range(n - 2):
                    for j in range(i + 2, n):
                        cand = r[:i + 1] + r[i + 1:j + 1][::-1] + r[j + 1:]
                        cst = route_cost(cand)
                        if cst + 1e-12 < best_cost:
                            best_cost = cst
                            best_r = cand
                if best_r is not r:
                    routes[ri] = best_r
                    improved = True

    return routes
