def solve_cvrp(instance):
    def get_value(keys, default=None):
        if isinstance(instance, dict):
            for k in keys:
                if k in instance:
                    return instance[k]
        return default

    # --- Parse instance ---
    capacity = get_value(("capacity", "vehicle_capacity", "cap"), 0)

    depot = get_value(("depot", "depot_id"), 0)
    coords = get_value(("coords", "coordinates", "points"), None)
    dist_matrix = get_value(("distance_matrix", "dist_matrix", "distances"), None)
    demands_raw = get_value(("demands", "demand"), None)
    customer_ids = get_value(("customer_ids", "customers", "nodes"), None)

    if customer_ids is None:
        if isinstance(demands_raw, dict):
            customer_ids = [k for k in demands_raw.keys() if k != depot]
        elif coords is not None and isinstance(coords, dict):
            customer_ids = [k for k in coords.keys() if k != depot]
        elif isinstance(dist_matrix, list):
            customer_ids = [i for i in range(len(dist_matrix)) if i != depot]
        else:
            customer_ids = []

    # Normalize ids
    customer_ids = [c for c in customer_ids if c != depot]
    customer_ids = list(dict.fromkeys(customer_ids))

    # Demands lookup
    demands = {}
    if isinstance(demands_raw, dict):
        demands = demands_raw.copy()
    elif isinstance(demands_raw, list):
        for i, d in enumerate(demands_raw):
            demands[i] = d

    def demand_of(c):
        return demands.get(c, 1)

    # Coordinate lookup
    xy = {}
    if isinstance(coords, dict):
        xy = coords.copy()
    elif isinstance(coords, list):
        for i, p in enumerate(coords):
            xy[i] = p

    def dist(a, b):
        if dist_matrix is not None:
            try:
                return dist_matrix[a][b]
            except Exception:
                pass
        if a in xy and b in xy:
            ax, ay = xy[a][0], xy[a][1]
            bx, by = xy[b][0], xy[b][1]
            dx = ax - bx
            dy = ay - by
            return (dx * dx + dy * dy) ** 0.5
        return abs(a - b)

    # --- Deterministic ordering ---
    if depot in xy:
        dx, dy = xy[depot][0], xy[depot][1]
        def angle_key(c):
            x, y = xy.get(c, (0, 0))
            return ((y - dy), (x - dx), c)
        customer_ids.sort(key=angle_key)
    else:
        customer_ids.sort(key=lambda c: (-demand_of(c), c))

    # --- Construct initial routes ---
    unassigned = customer_ids[:]
    routes = []

    while unassigned:
        route = []
        load = 0
        current = depot

        # seed: choose a customer that fits, preferring farthest from depot to form compact routes
        best = None
        best_score = None
        for c in unassigned:
            d = demand_of(c)
            if load + d <= capacity or not route:
                score = (dist(depot, c), -d, c)
                if best is None or score < best_score:
                    best = c
                    best_score = score

        if best is None:
            # If capacity is zero/invalid or demands exceed capacity, still place one customer per route.
            best = unassigned[0]

        route.append(best)
        load += demand_of(best)
        unassigned.remove(best)
        current = best

        # Grow route by nearest feasible insertion
        while True:
            cand = None
            cand_score = None
            for c in unassigned:
                d = demand_of(c)
                if load + d > capacity and capacity > 0:
                    continue
                score = (dist(current, c), dist(depot, c), c)
                if cand is None or score < cand_score:
                    cand = c
                    cand_score = score
            if cand is None:
                break
            route.append(cand)
            load += demand_of(cand)
            unassigned.remove(cand)
            current = cand

        routes.append(route)

    # --- Local search: 2-opt within routes ---
    def route_cost(rt):
        if not rt:
            return 0
        total = dist(depot, rt[0])
        for i in range(len(rt) - 1):
            total += dist(rt[i], rt[i + 1])
        total += dist(rt[-1], depot)
        return total

    def two_opt(route):
        n = len(route)
        if n < 4:
            return route
        improved = True
        while improved:
            improved = False
            best_delta = 0
            best_i = best_j = None
            for i in range(n - 2):
                a = depot if i == 0 else route[i - 1]
                b = route[i]
                for j in range(i + 2, n):
                    c = route[j]
                    d = depot if j == n - 1 else route[j + 1]
                    delta = (dist(a, c) + dist(b, d)) - (dist(a, b) + dist(c, d))
                    if delta < best_delta:
                        best_delta = delta
                        best_i, best_j = i, j
            if best_i is not None:
                route = route[:best_i] + route[best_i:best_j + 1][::-1] + route[best_j + 1:]
                improved = True
                n = len(route)
        return route

    routes = [two_opt(r) for r in routes]

    # --- Repair / relocate between routes for feasibility and mild improvement ---
    def load_of(rt):
        s = 0
        for c in rt:
            s += demand_of(c)
        return s

    changed = True
    while changed:
        changed = False
        loads = [load_of(r) for r in routes]
        for i in range(len(routes)):
            for pos in range(len(routes[i])):
                c = routes[i][pos]
                dc = demand_of(c)
                best_move = None
                best_gain = 0
                for j in range(len(routes)):
                    if i == j:
                        continue
                    if capacity > 0 and loads[j] + dc > capacity:
                        continue
                    r1 = routes[i]
                    r2 = routes[j]
                    # cost delta removing c from r1
                    prev1 = depot if pos == 0 else r1[pos - 1]
                    next1 = depot if pos == len(r1) - 1 else r1[pos + 1]
                    delta_remove = (dist(prev1, next1) - dist(prev1, c) - dist(c, next1))
                    # best insertion position in r2
                    best_ins_delta = None
                    best_k = None
                    for k in range(len(r2) + 1):
                        prev2 = depot if k == 0 else r2[k - 1]
                        next2 = depot if k == len(r2) else r2[k]
                        delta_ins = dist(prev2, c) + dist(c, next2) - dist(prev2, next2)
                        if best_ins_delta is None or delta_ins < best_ins_delta:
                            best_ins_delta = delta_ins
                            best_k = k
                    gain = delta_remove - best_ins_delta
                    if gain > best_gain:
                        best_gain = gain
                        best_move = (j, best_k)
                if best_move is not None and best_gain > 1e-12:
                    j, k = best_move
                    routes[j].insert(k, c)
                    del routes[i][pos]
                    changed = True
                    break
            if changed:
                break

    # Clean empty routes and finalize
    routes = [r for r in routes if r]
    return routes
