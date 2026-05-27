def solve_cvrp(instance):
    def get_capacity(inst):
        for k in ("capacity", "vehicle_capacity", "truck_capacity", "Q"):
            if isinstance(inst, dict) and k in inst:
                return inst[k]
        return None

    def get_depot(inst):
        if isinstance(inst, dict):
            for k in ("depot", "depot_location", "depot_coord", "depot_coords", "origin"):
                if k in inst:
                    return inst[k]
        return (0, 0)

    def get_customers(inst):
        if isinstance(inst, dict):
            for k in ("customers", "nodes", "points", "locations"):
                if k in inst:
                    return inst[k]
        return []

    def as_xy(x):
        if isinstance(x, dict):
            if "x" in x and "y" in x:
                return (x["x"], x["y"])
            if "coord" in x:
                return as_xy(x["coord"])
            if "location" in x:
                return as_xy(x["location"])
        if isinstance(x, (list, tuple)):
            if len(x) >= 2:
                return (x[0], x[1])
        return (0, 0)

    def customer_info(c):
        cid = None
        dem = 0
        xy = (0, 0)
        if isinstance(c, dict):
            for k in ("id", "customer_id", "node_id", "idx"):
                if k in c:
                    cid = c[k]
                    break
            for k in ("demand", "qty", "quantity", "load"):
                if k in c:
                    dem = c[k]
                    break
            for k in ("x", "y"):
                if k in c:
                    xy = as_xy(c)
                    break
            for k in ("coord", "coords", "location", "point"):
                if k in c:
                    xy = as_xy(c[k])
                    break
        elif isinstance(c, (list, tuple)):
            if len(c) >= 1:
                cid = c[0]
            if len(c) >= 2 and isinstance(c[1], (int, float)):
                dem = c[1]
            if len(c) >= 3:
                xy = as_xy(c[2])
        return cid, dem, xy

    depot = as_xy(get_depot(instance))
    capacity = get_capacity(instance)
    raw_customers = get_customers(instance)

    customers = []
    for c in raw_customers:
        cid, dem, xy = customer_info(c)
        if cid is None:
            continue
        customers.append([cid, dem, xy])

    if not customers:
        return []

    if capacity is None:
        total = 0
        for _, d, _ in customers:
            if isinstance(d, (int, float)):
                total += d
        capacity = max(1, total)

    # Deterministic ordering: angular sweep if coordinates look meaningful, else demand-desc/id
    dx0, dy0 = depot
    use_geo = True
    for _, _, (x, y) in customers:
        if x is None or y is None:
            use_geo = False
            break

    def angle_key(c):
        _, _, (x, y) = c
        dx = x - dx0
        dy = y - dy0
        ang = 0.0
        if dx != 0 or dy != 0:
            if dx >= 0 and dy >= 0:
                ang = dy / (abs(dx) + abs(dy) + 1e-9)
            elif dx < 0 and dy >= 0:
                ang = 2.0 - dy / (abs(dx) + abs(dy) + 1e-9)
            elif dx < 0 and dy < 0:
                ang = 2.0 + (-dy) / (abs(dx) + abs(dy) + 1e-9)
            else:
                ang = 4.0 - (-dy) / (abs(dx) + abs(dy) + 1e-9)
        dist = (dx * dx + dy * dy) ** 0.5
        return (ang, dist, c[0])

    if use_geo:
        customers.sort(key=angle_key)
    else:
        customers.sort(key=lambda c: (-c[1], c[0]))

    routes = []
    cur = []
    cur_load = 0
    for cid, dem, _ in customers:
        if cur and cur_load + dem > capacity:
            routes.append(cur)
            cur = []
            cur_load = 0
        cur.append(cid)
        cur_load += dem
    if cur:
        routes.append(cur)

    # Build lookup tables
    demand = {}
    coord = {}
    for cid, dem, xy in customers:
        demand[cid] = dem
        coord[cid] = xy

    def dist(a, b):
        ax, ay = depot if a == 0 else coord[a]
        bx, by = depot if b == 0 else coord[b]
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    def route_load(route):
        s = 0
        for cid in route:
            s += demand.get(cid, 0)
        return s

    def route_cost(route):
        if not route:
            return 0.0
        c = dist(0, route[0])
        for i in range(len(route) - 1):
            c += dist(route[i], route[i + 1])
        c += dist(route[-1], 0)
        return c

    # Intra-route 2-opt improvement
    if use_geo:
        improved = True
        while improved:
            improved = False
            for r_idx in range(len(routes)):
                r = routes[r_idx]
                n = len(r)
                if n < 4:
                    continue
                best_delta = 0.0
                best_i = -1
                best_j = -1
                for i in range(n - 2):
                    a = 0 if i == 0 else r[i - 1]
                    b = r[i]
                    for j in range(i + 1, n - 1):
                        c = r[j]
                        d = 0 if j == n - 1 else r[j + 1]
                        delta = (dist(a, c) + dist(b, d)) - (dist(a, b) + dist(c, d))
                        if delta < best_delta - 1e-12:
                            best_delta = delta
                            best_i = i
                            best_j = j
                if best_i != -1:
                    routes[r_idx] = r[:best_i] + list(reversed(r[best_i:best_j + 1])) + r[best_j + 1:]
                    improved = True

    # Inter-route relocate to reduce total distance, preserving feasibility
    changed = True
    while changed:
        changed = False
        best_move = None
        best_gain = 0.0
        for i in range(len(routes)):
            ri = routes[i]
            li = route_load(ri)
            for p, cid in enumerate(ri):
                dc = demand.get(cid, 0)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    lj = route_load(rj)
                    if lj + dc > capacity:
                        continue

                    # removal cost from ri
                    prev_i = 0 if p == 0 else ri[p - 1]
                    next_i = 0 if p == len(ri) - 1 else ri[p + 1]
                    remove_delta = dist(prev_i, next_i) - dist(prev_i, cid) - dist(cid, next_i)

                    # best insertion position in rj
                    best_ins_delta = None
                    best_pos = None
                    if not rj:
                        ins_delta = dist(0, cid) + dist(cid, 0)
                        best_ins_delta = ins_delta
                        best_pos = 0
                    else:
                        for pos in range(len(rj) + 1):
                            a = 0 if pos == 0 else rj[pos - 1]
                            b = 0 if pos == len(rj) else rj[pos]
                            ins_delta = dist(a, cid) + dist(cid, b) - dist(a, b)
                            if best_ins_delta is None or ins_delta < best_ins_delta - 1e-12:
                                best_ins_delta = ins_delta
                                best_pos = pos

                    gain = remove_delta - best_ins_delta
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best_move = (i, j, p, best_pos, cid)

        if best_move is not None:
            i, j, p, pos, cid = best_move
            if i < j:
                ri = routes[i]
                rj = routes[j]
            else:
                ri = routes[i]
                rj = routes[j]
            ri = routes[i]
            rj = routes[j]
            ri.pop(p)
            rj.insert(pos, cid)
            if len(ri) == 0:
                del routes[i]
            changed = True

    # Final cleanup: remove any empty routes
    routes = [r for r in routes if r]
    return routes
