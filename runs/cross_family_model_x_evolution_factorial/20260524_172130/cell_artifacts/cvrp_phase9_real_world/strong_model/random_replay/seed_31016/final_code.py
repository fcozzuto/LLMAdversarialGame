def solve_cvrp(instance):
    depot = instance.get("depot", 0)
    capacity = instance.get("capacity", instance.get("vehicle_capacity", 0))

    def is_seq(x):
        return isinstance(x, (list, tuple))

    def get_demands_container():
        for k in ("demands", "demand"):
            if k in instance:
                return instance[k]
        return None

    demands = get_demands_container()

    def customer_ids():
        if "customers" in instance and instance["customers"] is not None:
            return list(instance["customers"])
        if isinstance(demands, dict):
            return [c for c in demands.keys() if c != depot]
        if "locations" in instance and is_seq(instance["locations"]):
            n = len(instance["locations"])
            if depot == 0:
                return list(range(1, n))
            return [i for i in range(n) if i != depot]
        if "coords" in instance and is_seq(instance["coords"]):
            n = len(instance["coords"])
            if depot == 0:
                return list(range(1, n))
            return [i for i in range(n) if i != depot]
        if "distance_matrix" in instance or "dist_matrix" in instance or "cost_matrix" in instance:
            m = instance.get("distance_matrix", instance.get("dist_matrix", instance.get("cost_matrix")))
            n = len(m)
            if depot == 0:
                return list(range(1, n))
            return [i for i in range(n) if i != depot]
        if "n_customers" in instance:
            n = instance["n_customers"]
            return list(range(1, n + 1)) if depot == 0 else [i for i in range(1, n + 1) if i != depot]
        if isinstance(demands, (list, tuple)):
            n = len(demands)
            if depot == 0:
                return list(range(1, n))
            return [i for i in range(n) if i != depot]
        return []

    customers = customer_ids()

    def demand(c):
        if isinstance(demands, dict):
            return demands.get(c, 1)
        if isinstance(demands, (list, tuple)):
            if 0 <= c < len(demands):
                return demands[c]
            if 1 <= c <= len(demands) - 1:
                return demands[c]
        return 1

    coords = None
    if "coordinates" in instance:
        coords = instance["coordinates"]
    elif "coords" in instance:
        coords = instance["coords"]
    elif "locations" in instance:
        coords = instance["locations"]

    matrix = None
    for k in ("distance_matrix", "dist_matrix", "cost_matrix"):
        if k in instance:
            matrix = instance[k]
            break

    def dist(a, b):
        if matrix is not None:
            if isinstance(matrix, dict):
                if (a, b) in matrix:
                    return matrix[(a, b)]
                if (b, a) in matrix:
                    return matrix[(b, a)]
            else:
                try:
                    return matrix[a][b]
                except Exception:
                    pass
        if coords is not None:
            try:
                ax, ay = coords[a]
                bx, by = coords[b]
                dx = ax - bx
                dy = ay - by
                return (dx * dx + dy * dy) ** 0.5
            except Exception:
                pass
        return abs(a - b)

    # Build initial routes greedily by nearest feasible insertion from current end.
    unserved = set(customers)
    routes = []

    def route_load(route):
        s = 0
        for c in route:
            s += demand(c)
        return s

    def route_cost(route):
        if not route:
            return 0
        c = dist(depot, route[0])
        for i in range(len(route) - 1):
            c += dist(route[i], route[i + 1])
        c += dist(route[-1], depot)
        return c

    def insertion_cost(route, pos, c):
        prev_n = depot if pos == 0 else route[pos - 1]
        next_n = depot if pos == len(route) else route[pos]
        return dist(prev_n, c) + dist(c, next_n) - dist(prev_n, next_n)

    while unserved:
        # Seed: farthest feasible customer from depot, tie by higher demand then id.
        seed = None
        seed_key = None
        for c in unserved:
            d = demand(c)
            if d <= capacity:
                key = (dist(depot, c), d, -c if isinstance(c, int) else 0)
            else:
                key = (dist(depot, c), d, 0)
            if seed is None or key > seed_key:
                seed = c
                seed_key = key
        if seed is None:
            seed = min(unserved)
        route = [seed]
        load = demand(seed)
        unserved.remove(seed)

        while True:
            best = None
            best_key = None
            for c in unserved:
                d = demand(c)
                if load + d > capacity:
                    continue
                inc = dist(route[-1], c) + dist(c, depot) - dist(route[-1], depot)
                key = (inc, dist(depot, c), d, c)
                if best is None or key < best_key:
                    best = c
                    best_key = key
            if best is None:
                break
            route.append(best)
            load += demand(best)
            unserved.remove(best)

        routes.append(route)

    # Repair: if any route exceeds capacity due to edge cases, split greedily.
    fixed = []
    for r in routes:
        cur = []
        load = 0
        for c in r:
            d = demand(c)
            if load + d > capacity and cur:
                fixed.append(cur)
                cur = [c]
                load = d
            else:
                cur.append(c)
                load += d
        if cur:
            fixed.append(cur)
    routes = fixed

    # Local search: relocate and swap between routes.
    improved = True
    iter_limit = 2000
    it = 0
    while improved and it < iter_limit:
        improved = False
        it += 1

        # Inter-route relocate
        best_move = None
        best_delta = 0
        for i in range(len(routes)):
            ri = routes[i]
            li = route_load(ri)
            for pi, c in enumerate(ri):
                dc = demand(c)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    lj = route_load(rj)
                    if lj + dc > capacity:
                        continue
                    rem_delta = 0
                    prev_i = depot if pi == 0 else ri[pi - 1]
                    next_i = depot if pi == len(ri) - 1 else ri[pi + 1]
                    rem_delta += dist(prev_i, next_i) - dist(prev_i, c) - dist(c, next_i)
                    for pj in range(len(rj) + 1):
                        add_delta = insertion_cost(rj, pj, c)
                        delta = rem_delta + add_delta
                        if delta < best_delta:
                            best_delta = delta
                            best_move = ("relocate", i, pi, j, pj)
        if best_move is not None:
            _, i, pi, j, pj = best_move
            c = routes[i].pop(pi)
            if pj > len(routes[j]):
                pj = len(routes[j])
            routes[j].insert(pj, c)
            if not routes[i]:
                routes.pop(i)
            improved = True
            continue

        # Inter-route swap
        best_swap = None
        best_delta = 0
        loads = [route_load(r) for r in routes]
        for i in range(len(routes)):
            ri = routes[i]
            for pi, a in enumerate(ri):
                da = demand(a)
                prev_ai = depot if pi == 0 else ri[pi - 1]
                next_ai = depot if pi == len(ri) - 1 else ri[pi + 1]
                rem_ai = dist(prev_ai, next_ai) - dist(prev_ai, a) - dist(a, next_ai)
                for j in range(i + 1, len(routes)):
                    rj = routes[j]
                    for pj, b in enumerate(rj):
                        db = demand(b)
                        if loads[i] - da + db > capacity or loads[j] - db + da > capacity:
                            continue
                        prev_bj = depot if pj == 0 else rj[pj - 1]
                        next_bj = depot if pj == len(rj) - 1 else rj[pj + 1]
                        rem_bj = dist(prev_bj, next_bj) - dist(prev_bj, b) - dist(b, next_bj)

                        add_ai = dist(prev_bj, a) + dist(a, next_bj) - dist(prev_bj, b) - dist(b, next_bj)
                        add_bj = dist(prev_ai, b) + dist(b, next_ai) - dist(prev_ai, a) - dist(a, next_ai)
                        delta = rem_ai + rem_bj + add_ai + add_bj
                        if delta < best_delta:
                            best_delta = delta
