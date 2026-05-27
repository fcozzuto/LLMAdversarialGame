def solve_cvrp(instance):
    def get_value(obj, name, default=None):
        try:
            return obj.get(name, default)
        except Exception:
            pass
        try:
            d = obj.__dict__
            if name in d:
                return d[name]
        except Exception:
            pass
        return default

    def to_key(x):
        try:
            return int(x)
        except Exception:
            return x

    demands_raw = get_value(instance, "demands", None)
    if demands_raw is None:
        demands_raw = get_value(instance, "customer_demands", None)

    capacity = get_value(instance, "capacity", None)
    if capacity is None:
        capacity = get_value(instance, "vehicle_capacity", None)
    if capacity is None:
        capacity = get_value(instance, "Q", None)
    if capacity is None:
        capacity = 0

    coords_raw = get_value(instance, "coords", None)
    if coords_raw is None:
        coords_raw = get_value(instance, "locations", None)
    if coords_raw is None:
        coords_raw = get_value(instance, "points", None)

    demands = {}
    if demands_raw is not None:
        try:
            for k in demands_raw:
                demands[to_key(k)] = demands_raw[k]
        except Exception:
            try:
                for i in range(len(demands_raw)):
                    demands[i] = demands_raw[i]
            except Exception:
                pass

    coords = {}
    if coords_raw is not None:
        try:
            for k in coords_raw:
                coords[to_key(k)] = coords_raw[k]
        except Exception:
            try:
                for i in range(len(coords_raw)):
                    coords[i] = coords_raw[i]
            except Exception:
                pass

    depot = 0
    if depot not in demands and 0 not in coords:
        depot = 0

    customers = [k for k in demands.keys() if k != depot]
    if not customers and coords_raw is not None:
        try:
            customers = list(range(1, len(coords_raw)))
            demands[0] = demands.get(0, 0)
        except Exception:
            customers = []

    if capacity is None:
        capacity = 0

    def dist(a, b):
        pa = coords.get(a)
        pb = coords.get(b)
        if pa is None or pb is None:
            return 0.0 if a == b else abs(a - b)
        try:
            ax, ay = pa[0], pa[1]
            bx, by = pb[0], pb[1]
            dx = ax - bx
            dy = ay - by
            return (dx * dx + dy * dy) ** 0.5
        except Exception:
            return 0.0 if a == b else abs(a - b)

    def route_load(route):
        s = 0
        for c in route:
            s += demands.get(c, 0)
        return s

    def route_cost(route):
        if not route:
            return 0.0
        total = dist(depot, route[0])
        for i in range(len(route) - 1):
            total += dist(route[i], route[i + 1])
        total += dist(route[-1], depot)
        return total

    if coords:
        depot_pt = coords.get(depot, (0, 0))
        dx0 = depot_pt[0]
        dy0 = depot_pt[1]

        def order_key(c):
            p = coords.get(c, (0, 0))
            x = p[0] - dx0
            y = p[1] - dy0
            bucket = 0 if (y > 0 or (y == 0 and x >= 0)) else 1
            return (bucket, y / (abs(x) + abs(y) + 1e-12), x * x + y * y, c)

        customers = sorted(customers, key=order_key)
    else:
        customers = sorted(customers, key=lambda c: (-demands.get(c, 0), c))

    unassigned = customers[:]
    routes = []

    while unassigned:
        seed_i = 0
        best_seed = None
        for i, c in enumerate(unassigned):
            d = demands.get(c, 0)
            if d <= capacity or capacity == 0:
                if best_seed is None or d > best_seed or (d == best_seed and c < unassigned[seed_i]):
                    best_seed = d
                    seed_i = i
        seed = unassigned.pop(seed_i)
        route = [seed]
        load = demands.get(seed, 0)

        while unassigned:
            best_i = -1
            best_score = None
            last = route[-1]
            for i, cand in enumerate(unassigned):
                dem = demands.get(cand, 0)
                if capacity > 0 and load + dem > capacity:
                    continue
                delta = dist(last, cand) + dist(cand, depot) - dist(last, depot)
                score = (delta, dem, cand)
                if best_score is None or score < best_score:
                    best_score = score
                    best_i = i
            if best_i < 0:
                break
            cand = unassigned.pop(best_i)
            route.append(cand)
            load += demands.get(cand, 0)
        routes.append(route)

    # Repair duplicates/missing
    seen = {}
    for r in routes:
        for c in r:
            seen[c] = seen.get(c, 0) + 1

    missing = [c for c in customers if seen.get(c, 0) == 0]
    if missing:
        for c in missing:
            dem = demands.get(c, 0)
            best = None
            best_ri = -1
            best_pos = -1
            for ri, r in enumerate(routes):
                if capacity > 0 and route_load(r) + dem > capacity:
                    continue
                for pos in range(len(r) + 1):
                    prev = depot if pos == 0 else r[pos - 1]
                    nxt = depot if pos == len(r) else r[pos]
                    delta = dist(prev, c) + dist(c, nxt) - dist(prev, nxt)
                    score = (delta, ri, pos)
                    if best is None or score < best:
                        best = score
                        best_ri = ri
                        best_pos = pos
            if best_ri >= 0:
                routes[best_ri].insert(best_pos, c)
            else:
                routes.append([c])

    # Remove duplicates by keeping first occurrence and repairing omissions
    first = {}
    for ri in range(len(routes)):
        r = routes[ri]
        newr = []
        for c in r:
            if c not in first:
                first[c] = True
                newr.append(c)
        routes[ri] = newr
    missing = [c for c in customers if c not in first]
    for c in missing:
        routes.append([c])

    # Split overweight routes
    fixed = []
    for r in routes:
        if not r:
            continue
        cur = []
        load = 0
        for c in r:
            dem = demands.get(c, 0)
            if cur and capacity > 0 and load + dem > capacity:
                fixed.append(cur)
                cur = [c]
                load = dem
            else:
                cur.append(c)
                load += dem
        if cur:
            fixed.append(cur)
    routes = fixed

    # Local search: relocate and 2-opt within routes
    improved = True
    iters = 0
    while improved and iters < 4:
        improved = False
        iters += 1

        # Intra-route 2-opt
        for ri in range(len(routes)):
            r = routes[ri]
            n = len(r)
            best_gain = 0
            best_i = -1
            best_j = -1
            for i in range(n - 1):
                a = depot if i == 0 else r[i - 1]
                b = r[i]
                for j in range(i + 1, n):
                    c = r[j]
                    d = depot if j == n - 1 else r[j + 1]
                    gain = (dist(a, b) + dist(c, d)) - (dist(a, c) + dist(b, d))
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best_i = i
                        best_j = j
            if best_i >= 0:
                routes[ri] = r[:best_i] + list(reversed(r[best_i:best_j + 1])) + r[best_j + 1:]
                improved = True

        # Inter-route relocate
        for a in range(len(routes)):
            for i in range(len(routes[a])):
                c = routes[a][i]
                dem = demands.get(c, 0)
                for b in range(len(routes)):
                    if a == b:
                        continue
                    if capacity > 0 and route_load(routes[b]) + dem > capacity:
                        continue
                    ra = routes[a]
                    rb = routes[b]
                    prev_a = depot if i == 0 else ra[i - 1]
                    next_a = depot if i == len(ra) - 1 else ra[i + 1]
                    rem_gain = dist(prev_a, c) + dist(c, next_a) - dist(prev_a, next_a)
                    best_pos = -1
                    best_delta = None
                    for pos in range(len(rb) + 1):
                        prev_b = depot if pos == 0 else rb[pos - 1]
                        next_b = depot if pos == len(rb) else rb[pos]
                        add_gain = dist(prev_b, c) + dist(c, next_b) - dist(prev_b, next_b)
                        delta = add_gain - rem_gain
                        if best_delta is None or delta < best_delta:
                            best_delta = delta
                            best_pos = pos
                    if best_delta is not None and best_delta < -1e-12:
                        routes[a].pop(i)
                        routes[b].insert(best_pos, c)
                        if not routes[a]:
                            routes.pop(a)
                        improved = True
                        break
                if improved:
                    break
