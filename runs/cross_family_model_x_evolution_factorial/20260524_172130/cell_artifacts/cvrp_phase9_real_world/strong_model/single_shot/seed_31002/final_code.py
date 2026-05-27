def solve_cvrp(instance):
    def get(d, *keys, default=None):
        for k in keys:
            if isinstance(d, dict) and k in d:
                return d[k]
        return default

    # --- Parse instance ---
    depot = get(instance, "depot", "depot_id", default=0)
    capacity = get(instance, "capacity", "vehicle_capacity", default=None)

    demands = get(instance, "demands", "demand", default=None)
    coords = get(instance, "coords", "coordinates", "points", default=None)
    dist = get(instance, "distance_matrix", "distances", "matrix", default=None)

    nodes = None
    if isinstance(instance, dict):
        nodes = get(instance, "nodes", "customers", default=None)

    if nodes is None:
        if isinstance(demands, dict):
            nodes = [k for k in demands.keys() if k != depot]
        elif isinstance(coords, dict):
            nodes = [k for k in coords.keys() if k != depot]
        elif isinstance(dist, list):
            nodes = list(range(len(dist)))
            if depot in nodes:
                nodes = [n for n in nodes if n != depot]
        else:
            nodes = []

    if not isinstance(nodes, list):
        nodes = list(nodes)

    if depot in nodes:
        nodes = [n for n in nodes if n != depot]

    def demand_of(c):
        if isinstance(demands, dict):
            return demands.get(c, 1)
        if isinstance(demands, (list, tuple)) and isinstance(c, int) and 0 <= c < len(demands):
            return demands[c]
        return 1

    def coord_of(n):
        if isinstance(coords, dict):
            return coords.get(n, (0.0, 0.0))
        if isinstance(coords, (list, tuple)) and isinstance(n, int) and 0 <= n < len(coords):
            return coords[n]
        return (0.0, 0.0)

    def dist_of(a, b):
        if dist is not None:
            if isinstance(dist, dict):
                if a in dist and b in dist[a]:
                    return dist[a][b]
                if (a, b) in dist:
                    return dist[(a, b)]
            elif isinstance(dist, (list, tuple)):
                if isinstance(a, int) and isinstance(b, int) and 0 <= a < len(dist) and 0 <= b < len(dist[a]):
                    return dist[a][b]
        ax, ay = coord_of(a)
        bx, by = coord_of(b)
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    # --- Feasibility helpers ---
    if capacity is None:
        total = 0
        for c in nodes:
            total += max(0, demand_of(c))
        capacity = max(total, 1)

    # --- Construct initial routes using sweep by angle from depot ---
    dx, dy = coord_of(depot)
    def angle_key(c):
        x, y = coord_of(c)
        return ((y - dy) >= 0, (y - dy) / ((abs(x - dx) + 1e-12)), dist_of(depot, c), c)

    # Fallback if coords meaningless: use demand then id
    if coords is None:
        ordered = sorted(nodes, key=lambda c: (dist_of(depot, c), demand_of(c), c))
    else:
        ordered = sorted(nodes, key=lambda c: (angle_key(c), c))

    routes = []
    current = []
    load = 0
    for c in ordered:
        d = demand_of(c)
        if d > capacity:
            # impossible under given capacity; still place alone to preserve coverage
            if current:
                routes.append(current)
                current = []
                load = 0
            routes.append([c])
            continue
        if load + d <= capacity:
            current.append(c)
            load += d
        else:
            if current:
                routes.append(current)
            current = [c]
            load = d
    if current:
        routes.append(current)

    # --- Route cost and local optimization ---
    def route_load(rt):
        s = 0
        for c in rt:
            s += demand_of(c)
        return s

    def route_cost(rt):
        if not rt:
            return 0
        cost = dist_of(depot, rt[0])
        for i in range(len(rt) - 1):
            cost += dist_of(rt[i], rt[i + 1])
        cost += dist_of(rt[-1], depot)
        return cost

    def insertion_cost(rt, pos, c):
        prev = depot if pos == 0 else rt[pos - 1]
        nxt = depot if pos == len(rt) else rt[pos]
        return dist_of(prev, c) + dist_of(c, nxt) - dist_of(prev, nxt)

    def improve_route_2opt(rt):
        if len(rt) < 4:
            return rt[:]
        best = rt[:]
        improved = True
        while improved:
            improved = False
            n = len(best)
            for i in range(n - 2):
                a = depot if i == 0 else best[i - 1]
                b = best[i]
                for j in range(i + 1, n - 1):
                    c = best[j]
                    d = depot if j == n - 1 else best[j + 1]
                    old = dist_of(a, b) + dist_of(c, d)
                    new = dist_of(a, c) + dist_of(b, d)
                    if new + 1e-12 < old:
                        best[i:j + 1] = reversed(best[i:j + 1])
                        improved = True
                        break
                if improved:
                    break
        return best

    # --- Inter-route relocate / swap improvement ---
    changed = True
    iters = 0
    while changed and iters < 50:
        changed = False
        iters += 1

        # Improve each route internally
        for i in range(len(routes)):
            nr = improve_route_2opt(routes[i])
            if nr != routes[i]:
                routes[i] = nr
                changed = True

        # Relocate single customers
        best_delta = 0
        best_move = None
        for i, rt in enumerate(routes):
            for p, c in enumerate(rt):
                dem_c = demand_of(c)
                rem = rt[:p] + rt[p + 1:]
                remove_delta = route_cost(rem) - route_cost(rt)
                for j, trt in enumerate(routes):
                    if i == j:
                        continue
                    if route_load(trt) + dem_c > capacity:
                        continue
                    for pos in range(len(trt) + 1):
                        add_delta = insertion_cost(trt, pos, c)
                        delta = remove_delta + add_delta
                        if delta < best_delta - 1e-12:
                            best_delta = delta
                            best_move = (i, j, p, pos, c)
        if best_move is not None:
            i, j, p, pos, c = best_move
            rt = routes[i]
            trt = routes[j]
            rt2 = rt[:p] + rt[p + 1:]
            trt2 = trt[:pos] + [c] + trt[pos:]
            routes[i] = rt2
            routes[j] = trt2
            changed = True

        # Swap between routes
        best_delta = 0
        best_swap = None
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                r1 = routes[i]
                r2 = routes[j]
                l1 = route_load(r1)
                l2 = route_load(r2)
                for p, a in enumerate(r1):
                    da = demand_of(a)
                    for q, b in enumerate(r2):
                        db = demand_of(b)
                        if l1 - da + db > capacity or l2 - db + da > capacity:
                            continue
                        nr1 = r1[:p] + [b] + r1[p + 1:]
                        nr2 = r2[:q] + [a] + r2[q + 1:]
                        delta = route_cost(nr1) + route_cost(nr2) - route_cost(r1) - route_cost(r2)
                        if delta < best_delta - 1e-12:
                            best_delta = delta
                            best_swap = (i, j, p, q)
        if best_swap is not None:
            i, j, p, q = best_swap
            r1 = routes[i]
            r2 = routes[j]
            a = r1[p]
            b = r2[q]
            routes[i] = r1[:p] + [b] + r1[p + 1:]
            routes[j] = r2[:q] + [a] + r2[q + 1:]
            changed = True

    # Cleanup empty routes
    routes = [r for r in routes if r]

    # Final sanity: ensure every customer appears exactly once; repair if necessary
    seen = {}
    for ri, rt in enumerate(routes):
        for c in rt:
            seen[c] = seen.get(c, 0) + 1

    missing = [c for c in nodes if seen.get(c, 0) == 0]
    duplicates = [c for c, cnt in seen.items() if cnt > 1]

    if missing or duplicates:
        # Remove duplicates while keeping first occurrence
        kept = set()
        cleaned = []
        for rt in routes:
            newrt = []
            load = 0
            for c in rt:
                if c in kept:
                    continue
                d = demand_of(c)
                if load + d <= capacity:
                    newrt.append(c)
                    kept.add(c)
                    load += d
            if newrt:
                cleaned.append(newrt)
        routes = cleaned

        # Insert missing customers greedily
        for c in missing:
            best = None
            best_delta = None
            dc = demand_of(c)
            for i, rt in enumerate(routes):
                if route_load(rt) + dc > capacity:
                    continue
                for pos in range(len(rt) + 1):
                    delta = insertion_cost(rt, pos, c)
                    if best_delta is None or delta < best_delta - 1e-12 or (abs(delta - best_delta) <= 1e-12 and (i, pos) < (best[0], best[1])):
                        best_delta = delta
                        best = (i, pos)
            if best is None:
                routes.append([c])
            else:
                i, pos = best
                routes[i] = routes[i][:pos] + [c] + routes[i][pos:]

    # One last deterministic improvement pass
    routes = [improve_route_2opt(r) for r in routes if r]
    routes.sort(key=lambda r: (r[0] if r else -1, len(r), route_cost(r)))
    return routes
