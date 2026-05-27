def solve_cvrp(instance):
    depot = 0

    def get_value(obj, keys, default=None):
        if isinstance(obj, dict):
            for k in keys:
                if k in obj:
                    return obj[k]
        return default

    def as_list(x):
        if x is None:
            return None
        return list(x)

    coords = get_value(instance, ["coords", "coordinates", "points", "locs", "locations"], None)
    dist_matrix = get_value(instance, ["dist_matrix", "distance_matrix", "matrix", "distances"], None)
    demands = get_value(instance, ["demands", "demand"], None)
    capacity = get_value(instance, ["capacity", "vehicle_capacity", "cap"], None)

    n = None
    customers = None

    if demands is not None:
        if isinstance(demands, dict):
            customers = [k for k in demands.keys() if k != depot]
        else:
            demands = list(demands)
            customers = [i for i in range(len(demands)) if i != depot]
        n = len(customers)
    elif coords is not None:
        coords = list(coords)
        customers = [i for i in range(len(coords)) if i != depot]
        n = len(customers)
        demands = [1] * len(coords)
        demands[depot] = 0
    elif dist_matrix is not None:
        dist_matrix = list(dist_matrix)
        n = len(dist_matrix) - 1
        customers = list(range(1, n + 1))
        demands = [1] * (n + 1)
        demands[depot] = 0
    else:
        return []

    if capacity is None:
        total_demand = 0
        for c in customers:
            total_demand += demands[c] if isinstance(demands, list) else demands[c]
        capacity = max(1, total_demand)

    def demand_of(c):
        return demands[c] if isinstance(demands, list) else demands.get(c, 0)

    def dist(i, j):
        if dist_matrix is not None:
            return dist_matrix[i][j]
        if coords is not None:
            a = coords[i]
            b = coords[j]
            dx = a[0] - b[0]
            dy = a[1] - b[1]
            return (dx * dx + dy * dy) ** 0.5
        return 0

    def route_load(route):
        s = 0
        for c in route:
            s += demand_of(c)
        return s

    def route_cost(route):
        if not route:
            return 0
        cst = dist(depot, route[0])
        for i in range(len(route) - 1):
            cst += dist(route[i], route[i + 1])
        cst += dist(route[-1], depot)
        return cst

    def total_cost(routes):
        return sum(route_cost(r) for r in routes)

    # Constructive phase
    routes = []
    remaining = customers[:]

    if coords is not None:
        importable = False
        try:
            _ = coords[0][0]
            importable = True
        except Exception:
            importable = False
        if importable:
            def angle(c):
                p = coords[c]
                dx = p[0] - coords[depot][0]
                dy = p[1] - coords[depot][1]
                # quadrant-safe ordering without math import
                if dx == 0 and dy == 0:
                    return (0, 0)
                half = 0 if dy >= 0 else 1
                return (half, dy / (abs(dx) + abs(dy) + 1e-12), dx / (abs(dx) + abs(dy) + 1e-12))
            remaining.sort(key=lambda c: (angle(c), dist(depot, c), c))
        else:
            remaining.sort()

    while remaining:
        route = []
        load = 0
        current = depot

        if coords is not None:
            # Start with farthest feasible customer, then greedily nearest-feasible
            best = None
            best_key = None
            for c in remaining:
                d = demand_of(c)
                if load + d <= capacity:
                    key = (dist(depot, c), -d, c)
                    if best is None or key > best_key:
                        best = c
                        best_key = key
            if best is None:
                best = remaining[0]
            route.append(best)
            load += demand_of(best)
            remaining.remove(best)
            current = best

        improved = True
        while improved:
            improved = False
            best = None
            best_key = None
            for c in remaining:
                d = demand_of(c)
                if load + d > capacity:
                    continue
                # choose best insertion by closeness to current with preference for small detour
                key = (-(dist(current, c)), -d, -dist(depot, c), -c)
                if best is None or key > best_key:
                    best = c
                    best_key = key
            if best is not None:
                route.append(best)
                load += demand_of(best)
                remaining.remove(best)
                current = best
                improved = True

        if not route and remaining:
            c = remaining.pop(0)
            route = [c]
        routes.append(route)

    # Repair phase: move customers from overloaded routes impossible due to construction if cap given
    # but we can merge/split to reduce route count
    changed = True
    while changed:
        changed = False
        # Try to merge route pairs
        i = 0
        while i < len(routes):
            j = i + 1
            while j < len(routes):
                ri = routes[i]
                rj = routes[j]
                if route_load(ri) + route_load(rj) <= capacity:
                    merged = ri + rj
                    # simple best of forward/reverse combinations
                    candidates = [merged, ri + rj[::-1], ri[::-1] + rj, ri[::-1] + rj[::-1]]
                    best_route = min(candidates, key=route_cost)
                    if route_cost(best_route) <= route_cost(ri) + route_cost(rj):
                        routes[i] = best_route
                        routes.pop(j)
                        changed = True
                        i = -1
                        break
                j += 1
            i += 1
        if changed:
            continue

        # Relocate single customer from one route to another if beneficial
        best_delta = 0
        best_move = None
        for a in range(len(routes)):
            ra = routes[a]
            for idx, c in enumerate(ra):
                dem = demand_of(c)
                for b in range(len(routes)):
                    if a == b:
                        continue
                    rb = routes[b]
                    if route_load(rb) + dem > capacity:
                        continue
                    # remove c from ra
                    ra2 = ra[:idx] + ra[idx + 1:]
                    if not ra2:
                        cost_a = 0
                    else:
                        cost_a = route_cost(ra)
                    base = route_cost(ra) + route_cost(rb)
                    # best insertion in rb
                    best_rb_cost = None
                    best_rb = None
                    for pos in range(len(rb) + 1):
                        trial = rb[:pos] + [c] + rb[pos:]
                        cc = route_cost(ra2) + route_cost(trial)
                        if best_rb_cost is None or cc < best_rb_cost:
                            best_rb_cost = cc
                            best_rb = trial
                    delta = base - best_rb_cost if best_rb_cost is not None else 0
                    if delta > best_delta:
                        best_delta = delta
                        best_move = (a, b, idx, c, ra2, best_rb)
        if best_move:
            a, b, idx, c, ra2, best_rb = best_move
            if ra2:
                routes[a] = ra2
                routes[b] = best_rb
            else:
                routes.pop(a)
                if b > a:
                    b -= 1
                routes[b] = best_rb
            changed = True

    # Local search within routes: 2-opt and reversal
    for r in range(len(routes)):
        route = routes[r]
        if len(route) >= 4:
            improved = True
            while improved:
                improved = False
                best = route
                best_cost = route_cost(route)
                m = len(route)
                for i in range(m - 1):
                    for k in range(i + 2, m):
                        if i == 0 and k == m - 1:
                            continue
                        cand = route[:i + 1] + route[i + 1:k + 1][::-1] + route[k + 1:]
                        cst = route_cost(cand)
                        if cst + 1e-12 < best_cost:
                            best_cost = cst
                            best = cand
                            improved = True
                route = best
            routes[r] = route
        elif len(route) == 2:
            rev = route[::-1]
            if route_cost(rev) < route_cost(route):
                routes[r] = rev

    # Ensure all customers exactly once and feasible
    seen = {}
    for ri, route in enumerate(routes):
        for c in route:
            seen[c] = seen.get(c, 0) + 1

    missing = [c for c in customers if seen.get(c, 0) == 0]
    dupes = [c for c, cnt in seen.items() if cnt > 1]

    if missing or dupes:
        # rebuild deterministically from scratch using simple greedy insertion
        routes = []
        unassigned = customers[:]
        if coords is not None:
            unassigned.sort(key=lambda c: (dist(depot, c), c))
        else:
            unassigned.sort()
        while unassigned:
            route = []
            load = 0
            current = depot
            while True:
                best = None
                best_key = None
                for c in unassigned:
                    d = demand_of(c)
