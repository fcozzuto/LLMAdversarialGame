def solve_cvrp(instance):
    data = instance
    if isinstance(data, dict):
        customers = data.get("customers", data.get("nodes", data.get("points", None)))
        depot = data.get("depot", 0)
        capacity = data.get("capacity", data.get("vehicle_capacity", data.get("Q", None)))
    else:
        customers = None
        depot = 0
        capacity = None

    coords = {}
    demand = {}
    ids = []

    def get_xy(v):
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return (v["x"], v["y"])
            if "coord" in v and isinstance(v["coord"], (list, tuple)) and len(v["coord"]) >= 2:
                return (v["coord"][0], v["coord"][1])
            if "position" in v and isinstance(v["position"], (list, tuple)) and len(v["position"]) >= 2:
                return (v["position"][0], v["position"][1])
        return None

    if customers is not None:
        if isinstance(customers, dict):
            for k, v in customers.items():
                ids.append(k)
                xy = get_xy(v)
                if xy is not None:
                    coords[k] = xy
                if isinstance(v, dict) and "demand" in v:
                    demand[k] = v["demand"]
        else:
            for i, v in enumerate(customers):
                ids.append(i)
                xy = get_xy(v)
                if xy is not None:
                    coords[i] = xy
                if isinstance(v, dict) and "demand" in v:
                    demand[i] = v["demand"]
    else:
        if isinstance(data, dict):
            if "coordinates" in data:
                c = data["coordinates"]
                if isinstance(c, dict):
                    for k, xy in c.items():
                        ids.append(k)
                        if isinstance(xy, (list, tuple)) and len(xy) >= 2:
                            coords[k] = (xy[0], xy[1])
                else:
                    for i, xy in enumerate(c):
                        ids.append(i)
                        if isinstance(xy, (list, tuple)) and len(xy) >= 2:
                            coords[i] = (xy[0], xy[1])
            if "demands" in data:
                d = data["demands"]
                if isinstance(d, dict):
                    for k, v in d.items():
                        demand[k] = v
                else:
                    for i, v in enumerate(d):
                        demand[i] = v
            if "customers" in data and isinstance(data["customers"], list):
                ids = list(range(len(data["customers"])))

    if not ids and isinstance(data, dict) and "n" in data:
        ids = list(range(data["n"]))

    if depot not in ids and isinstance(depot, int) and depot >= 0:
        pass

    if capacity is None:
        if isinstance(data, dict):
            capacity = data.get("vehicle_capacity", data.get("Q", 0))
    if capacity is None:
        capacity = 0

    all_ids = [i for i in ids if i != depot]
    if not all_ids and isinstance(data, dict) and "demands" in data:
        all_ids = [k for k in demand.keys() if k != depot]

    for k in all_ids:
        if k not in demand:
            demand[k] = 1

    depot_xy = coords.get(depot, (0.0, 0.0))

    def dist(a, b):
        if a in coords and b in coords:
            ax, ay = coords[a]
            bx, by = coords[b]
            dx = ax - bx
            dy = ay - by
            return dx * dx + dy * dy
        return 0.0

    def angle_of(i):
        if i in coords:
            x, y = coords[i]
            return (y - depot_xy[1], x - depot_xy[0])
        return (0.0, 0.0)

    def angle_key(i):
        if i in coords:
            x, y = coords[i]
            importless = 0  # placeholder to keep deterministic structure
            dx = x - depot_xy[0]
            dy = y - depot_xy[1]
            return (0 if dy >= 0 else 1, (dx * dx + dy * dy), dy, dx, i)
        return (0, 0, 0, 0, i)

    unassigned = all_ids[:]
    unassigned.sort(key=angle_key)

    routes = []
    route_loads = []

    current = []
    load = 0
    for cid in unassigned:
        dem = demand.get(cid, 1)
        if current and load + dem > capacity:
            routes.append(current)
            route_loads.append(load)
            current = [cid]
            load = dem
        else:
            current.append(cid)
            load += dem
    if current:
        routes.append(current)
        route_loads.append(load)

    def route_cost(route):
        if not route:
            return 0.0
        c = dist(depot, route[0]) + dist(route[-1], depot)
        for i in range(len(route) - 1):
            c += dist(route[i], route[i + 1])
        return c

    def total_cost(rs):
        s = 0.0
        for r in rs:
            s += route_cost(r)
        return s

    def load_of(route):
        s = 0
        for c in route:
            s += demand.get(c, 1)
        return s

    changed = True
    iterations = 0
    while changed and iterations < 200:
        iterations += 1
        changed = False

        # Intra-route 2-opt improvement
        for r_idx in range(len(routes)):
            r = routes[r_idx]
            n = len(r)
            improved = True
            while improved:
                improved = False
                for i in range(n - 2):
                    a = depot if i == 0 else r[i - 1]
                    b = r[i]
                    for j in range(i + 2, n):
                        c = r[j - 1]
                        d = depot if j == n else r[j]
                        before = dist(a, b) + dist(c, d)
                        after = dist(a, c) + dist(b, d)
                        if after + 1e-12 < before:
                            r[i:j] = r[i:j][::-1]
                            improved = True
                            changed = True
                            break
                    if improved:
                        break

        # Inter-route relocate
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j:
                    continue
                ri = routes[i]
                rj = routes[j]
                li = load_of(ri)
                lj = load_of(rj)
                best_move = None
                best_delta = 0.0
                for p, node in enumerate(ri):
                    dem = demand.get(node, 1)
                    if lj + dem > capacity:
                        continue
                    prev_i = depot if p == 0 else ri[p - 1]
                    next_i = depot if p == len(ri) - 1 else ri[p + 1]
                    remove_delta = dist(prev_i, next_i) - dist(prev_i, node) - dist(node, next_i)
                    for q in range(len(rj) + 1):
                        prev_j = depot if q == 0 else rj[q - 1]
                        next_j = depot if q == len(rj) else rj[q]
                        insert_delta = dist(prev_j, node) + dist(node, next_j) - dist(prev_j, next_j)
                        delta = remove_delta + insert_delta
                        if delta < best_delta - 1e-12:
                            best_delta = delta
                            best_move = (p, q, node)
                if best_move is not None:
                    p, q, node = best_move
                    rj.insert(q, node)
                    ri.pop(p)
                    changed = True

        # Remove empty routes
        routes = [r for r in routes if r]
        route_loads = [load_of(r) for r in routes]

        # Inter-route swap
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                ri = routes[i]
                rj = routes[j]
                li = load_of(ri)
                lj = load_of(rj)
                best = None
                best_delta = 0.0
                for p, a in enumerate(ri):
                    da = demand.get(a, 1)
                    for q, b in enumerate(rj):
                        db = demand.get(b, 1)
                        if li - da + db > capacity or lj - db + da > capacity:
                            continue
                        prev_ai = depot if p == 0 else ri[p - 1]
                        next_ai = depot if p == len(ri) - 1 else ri[p + 1]
                        prev_bj = depot if q == 0 else rj[q - 1]
                        next_bj = depot if q == len(rj) - 1 else rj[q + 1]
                        old = dist(prev_ai, a) + dist(a, next_ai) + dist(prev_bj, b) + dist(b, next_bj)
                        new = dist(prev_ai, b) + dist(b, next_ai) + dist(prev_bj, a) + dist(a, next_bj)
                        delta = new - old
                        if delta < best_delta - 1e-12:
                            best_delta = delta
                            best = (p, q, a, b)
                if best is not None:
                    p, q, a, b = best
                    ri[p], rj[q] = b, a
                    changed = True

    # Final repair for any accidental issues
    seen = {}
    for r in routes:
        for c in r:
            seen[c] = seen.get(c, 0) + 1
    missing = [c for c in all_ids if seen.get(c, 0) == 0]
    if missing:
        for c in missing:
            placed = False
            for r in routes:
                if load_of(r) + demand.get(c, 1) <= capacity:
                    best_pos = 0
                    best_inc = None
                    for pos in range(len(r) + 1):
                        prev = depot if pos == 0 else r[pos - 1]
                        nxt = depot if pos == len(r) else r[pos]
                        inc = dist(prev, c) + dist(c, nxt) - dist(prev, nxt)
                        if best_inc is None or inc < best_inc:
                            best_inc = inc
                            best_pos = pos
                    r.insert(best_pos, c)
                    placed = True
                    break
            if not placed:
                routes.append([c])

    return routes
