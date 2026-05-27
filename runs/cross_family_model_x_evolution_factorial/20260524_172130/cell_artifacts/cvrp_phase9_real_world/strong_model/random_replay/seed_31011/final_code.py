def solve_cvrp(instance):
    def get_any(d, keys, default=None):
        try:
            for k in keys:
                if k in d:
                    return d[k]
        except:
            pass
        return default

    def has_keys(x):
        try:
            x.keys()
            return True
        except:
            return False

    depot = 0
    if has_keys(instance):
        depot = get_any(instance, ["depot", "depot_id", "source", "origin"], 0)

    customers = get_any(instance, ["customers", "nodes", "points", "locations"], None) if has_keys(instance) else None
    demands = get_any(instance, ["demands", "demand", "loads"], None) if has_keys(instance) else None
    capacity = get_any(instance, ["capacity", "vehicle_capacity", "cap"], None) if has_keys(instance) else None
    dist_matrix = get_any(instance, ["distance_matrix", "distances", "matrix"], None) if has_keys(instance) else None
    coords = get_any(instance, ["coords", "coordinates", "xy", "pos"], None) if has_keys(instance) else None

    customer_ids = []
    if customers is not None:
        try:
            for i in range(len(customers)):
                c = customers[i]
                cid = i
                try:
                    if has_keys(c) and "id" in c:
                        cid = c["id"]
                except:
                    pass
                if cid != depot:
                    customer_ids.append(cid)
        except:
            try:
                for k in customers.keys():
                    if k != depot:
                        customer_ids.append(k)
            except:
                pass
    elif has_keys(demands):
        for k in demands.keys():
            if k != depot:
                customer_ids.append(k)
    elif has_keys(coords):
        for k in coords.keys():
            if k != depot:
                customer_ids.append(k)
    elif has_keys(instance) and "n" in instance:
        n = instance["n"]
        try:
            n = int(n)
            for i in range(n):
                if i != depot:
                    customer_ids.append(i)
        except:
            pass

    seen = {}
    uniq = []
    for cid in customer_ids:
        if cid not in seen:
            seen[cid] = 1
            uniq.append(cid)
    customer_ids = uniq

    def demand_of(cid):
        if demands is None:
            return 0
        try:
            if has_keys(demands):
                v = demands.get(cid, 0)
                return int(v)
        except:
            pass
        try:
            if len(demands) > cid and cid >= 0:
                return int(demands[cid])
        except:
            pass
        return 0

    def coord_of(cid):
        if coords is None:
            if customers is not None:
                try:
                    c = customers[cid]
                    if has_keys(c):
                        if "x" in c and "y" in c:
                            return (c["x"], c["y"])
                        if "coord" in c:
                            return tuple(c["coord"])
                    if len(c) >= 2:
                        return (c[0], c[1])
                except:
                    pass
            return None
        try:
            if has_keys(coords):
                v = coords.get(cid, None)
                if has_keys(v):
                    if "x" in v and "y" in v:
                        return (v["x"], v["y"])
                    if "coord" in v:
                        return tuple(v["coord"])
                elif len(v) >= 2:
                    return (v[0], v[1])
            else:
                v = coords[cid]
                if has_keys(v):
                    if "x" in v and "y" in v:
                        return (v["x"], v["y"])
                    if "coord" in v:
                        return tuple(v["coord"])
                elif len(v) >= 2:
                    return (v[0], v[1])
        except:
            pass
        return None

    def dist(a, b):
        if a == b:
            return 0
        if dist_matrix is not None:
            try:
                return dist_matrix[a][b]
            except:
                try:
                    return dist_matrix[b][a]
                except:
                    pass
        ca = coord_of(a)
        cb = coord_of(b)
        if ca is not None and cb is not None:
            dx = ca[0] - cb[0]
            dy = ca[1] - cb[1]
            return (dx * dx + dy * dy) ** 0.5
        try:
            return abs(a - b)
        except:
            return 1

    if capacity is None:
        total = 0
        for cid in customer_ids:
            total += demand_of(cid)
        capacity = total if total > 0 else 1
    capacity = int(capacity)

    # Order customers
    ordered = []
    depot_xy = coord_of(depot)
    if depot_xy is not None:
        for cid in customer_ids:
            c = coord_of(cid)
            if c is None:
                ang = 0
                rad = 0
            else:
                dx = c[0] - depot_xy[0]
                dy = c[1] - depot_xy[1]
                ang = 0
                if dx != 0 or dy != 0:
                    if dx >= 0 and dy >= 0:
                        ang = dy / (abs(dx) + abs(dy) + 1e-9)
                    elif dx < 0 <= dy:
                        ang = 2 + (-dx) / (abs(dx) + abs(dy) + 1e-9)
                    elif dx < 0 and dy < 0:
                        ang = 4 + (-dy) / (abs(dx) + abs(dy) + 1e-9)
                    else:
                        ang = 6 + dx / (abs(dx) + abs(dy) + 1e-9)
                rad = dx * dx + dy * dy
            ordered.append((ang, rad, cid))
        ordered.sort()
        customer_ids = [t[2] for t in ordered]
    else:
        customer_ids.sort(key=lambda x: (demand_of(x), x))

    # Greedy initial routes
    routes = []
    route_loads = []
    cur = []
    load = 0
    for cid in customer_ids:
        d = demand_of(cid)
        if cur and load + d > capacity:
            routes.append(cur)
            route_loads.append(load)
            cur = [cid]
            load = d
        else:
            cur.append(cid)
            load += d
    if cur:
        routes.append(cur)
        route_loads.append(load)

    # Repair if any route over capacity by splitting largest-demand items
    fixed = []
    fixed_loads = []
    for r in routes:
        rl = 0
        for cid in r:
            rl += demand_of(cid)
        if rl <= capacity:
            fixed.append(r)
            fixed_loads.append(rl)
        else:
            bucket = []
            bload = 0
            for cid in r:
                d = demand_of(cid)
                if bucket and bload + d > capacity:
                    fixed.append(bucket)
                    fixed_loads.append(bload)
                    bucket = [cid]
                    bload = d
                else:
                    bucket.append(cid)
                    bload += d
            if bucket:
                fixed.append(bucket)
                fixed_loads.append(bload)
    routes = fixed
    route_loads = fixed_loads

    # Local search: intra-route 2-opt improvement on geometric routes
    def route_cost(rt):
        if not rt:
            return 0
        s = dist(depot, rt[0]) + dist(rt[-1], depot)
        for i in range(len(rt) - 1):
            s += dist(rt[i], rt[i + 1])
        return s

    improved = True
    while improved:
        improved = False
        for ri in range(len(routes)):
            r = routes[ri]
            n = len(r)
            if n < 4:
                continue
            best_delta = 0
            best_i = -1
            best_j = -1
            for i in range(n - 2):
                a = depot if i == 0 else r[i - 1]
                b = r[i]
                for j in range(i + 1, n - 1):
                    c = r[j]
                    d = depot if j == n - 1 else r[j + 1]
                    delta = (dist(a, c) + dist(b, d)) - (dist(a, b) + dist(c, d))
                    if delta < best_delta:
                        best_delta = delta
                        best_i = i
                        best_j = j
            if best_i >= 0:
                r = r[:best_i] + r[best_i:best_j + 1][::-1] + r[best_j + 1:]
                routes[ri] = r
                improved = True

    # Deterministic cross-route relocate for savings
    changed = True
    while changed:
        changed = False
        best_gain = 0
        best_move = None
