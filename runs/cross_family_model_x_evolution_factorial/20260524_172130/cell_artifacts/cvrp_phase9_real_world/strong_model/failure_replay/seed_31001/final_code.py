def solve_cvrp(instance):
    def is_num(x):
        try:
            return (x + 0) == x and not (x is True or x is False)
        except:
            return False

    def has_key(d, k):
        try:
            return k in d
        except:
            return False

    def get_any(d, keys, default=None):
        try:
            for k in keys:
                if k in d:
                    return d[k]
        except:
            pass
        return default

    def to_point(v):
        try:
            if v is None:
                return None
            if len(v) >= 2 and is_num(v[0]) and is_num(v[1]):
                return (float(v[0]), float(v[1]))
        except:
            pass
        try:
            if has_key(v, "x") and has_key(v, "y") and is_num(v["x"]) and is_num(v["y"]):
                return (float(v["x"]), float(v["y"]))
            if has_key(v, 0) and has_key(v, 1) and is_num(v[0]) and is_num(v[1]):
                return (float(v[0]), float(v[1]))
        except:
            pass
        return None

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    def route_cost(route, coords, depot):
        if not route:
            return 0.0
        c = dist(depot, coords[route[0]])
        for i in range(len(route) - 1):
            c += dist(coords[route[i]], coords[route[i + 1]])
        c += dist(coords[route[-1]], depot)
        return c

    capacity = get_any(instance, ["capacity", "vehicle_capacity", "cap"], None)
    if capacity is None:
        try:
            fleet = get_any(instance, ["fleet", "vehicle"], None)
            capacity = get_any(fleet, ["capacity", "cap"], None) if fleet is not None else None
        except:
            capacity = None
    if capacity is None:
        capacity = 10 ** 18
    capacity = float(capacity)

    depot_id = get_any(instance, ["depot_id", "depot", "origin"], 0)
    coords = {}
    demand = {}
    depot_point = None

    try:
        dep = get_any(instance, ["depot"], None)
        if dep is not None:
            if has_key(dep, "id"):
                depot_id = dep.get("id", depot_id)
            depot_point = to_point(dep)
            if depot_point is None and has_key(dep, "coord"):
                depot_point = to_point(dep["coord"])
    except:
        pass

    try:
        cobj = get_any(instance, ["coords"], None)
        if cobj is not None:
            for k in cobj:
                p = to_point(cobj[k])
                if p is not None:
                    coords[k] = p
    except:
        pass

    try:
        dobj = get_any(instance, ["demands"], None)
        if dobj is not None:
            for k in dobj:
                if is_num(dobj[k]):
                    demand[k] = float(dobj[k])
    except:
        pass

    customers = get_any(instance, ["customers", "nodes", "points", "locations"], None)
    if customers is not None:
        try:
            items = customers.items()
        except:
            items = enumerate(customers)
        for k, v in items:
            try:
                cid = v.get("id", k) if has_key(v, "id") else k
                p = to_point(v)
                if p is None and has_key(v, "coord"):
                    p = to_point(v["coord"])
                if p is not None:
                    coords[cid] = p
                if has_key(v, "demand") and is_num(v["demand"]):
                    demand[cid] = float(v["demand"])
            except:
                pass

    try:
        for key in ["nodes", "locations", "points"]:
            val = instance.get(key) if has_key(instance, key) else None
            if val is not None:
                try:
                    n = len(val)
                except:
                    n = 0
                for i in range(n):
                    v = val[i]
                    try:
                        cid = v.get("id", i) if has_key(v, "id") else i
                        p = to_point(v)
                        if p is None and has_key(v, "coord"):
                            p = to_point(v["coord"])
                        if p is not None:
                            coords[cid] = p
                        if has_key(v, "demand") and is_num(v["demand"]):
                            demand[cid] = float(v["demand"])
                    except:
                        pass
                break
    except:
        pass

    if depot_point is None:
        try:
            if depot_id in coords:
                depot_point = coords[depot_id]
            else:
                dep = get_any(instance, ["depot"], None)
                depot_point = to_point(dep) if dep is not None else None
        except:
            depot_point = None
    if depot_point is None:
        depot_point = (0.0, 0.0)

    customer_ids = [k for k in coords.keys() if k != depot_id]
    if not customer_ids:
        customer_ids = [k for k in demand.keys() if k != depot_id]

    for cid in customer_ids:
        if cid not in demand:
            demand[cid] = 1.0
        if cid not in coords:
            coords[cid] = depot_point

    def ang_key(cid):
        p = coords[cid]
        dx = p[0] - depot_point[0]
        dy = p[1] - depot_point[1]
        quad = 0 if dy >= 0 and dx >= 0 else 1 if dy >= 0 and dx < 0 else 2 if dy < 0 and dx < 0 else 3
        return (quad, dy / (abs(dx) + abs(dy) + 1e-12), dist(depot_point, p), cid)

    unrouted = sorted(customer_ids, key=ang_key)
    routes = []

    while unrouted:
        route = []
        load = 0.0
        current = depot_point
        while True:
            best_i = -1
            best_score = None
            best_cid = None
            for i in range(len(unrouted)):
                cid = unrouted[i]
                dem = demand[cid]
                if load + dem > capacity + 1e-12:
                    continue
                p = coords[cid]
                dcur = dist(current, p)
                ddep = dist(depot_point, p)
                score = dcur + 0.15 * ddep - 0.05 * (capacity - load - dem)
                if best_score is None or score < best_score or (score == best_score and cid < best_cid):
                    best_score = score
                    best_i = i
                    best_cid = cid
            if best_i < 0:
                break
            cid = unrouted.pop(best_i)
            route.append(cid)
            load += demand[cid]
            current = coords[cid]
            if load >= capacity - 1e-12:
                break
        if not route and unrouted:
            cid = unrouted.pop(0)
            route = [cid]
        routes.append(route)

    all_ids = set(customer_ids)
    seen = set()
    cleaned = []
    for r in routes:
        nr = []
        load = 0.0
        for cid in r:
            if cid in seen or cid not in all_ids:
                continue
            if load + demand[cid] <= capacity + 1e-12:
                nr.append(cid)
                seen.add(cid)
                load += demand[cid]
            else:
                cleaned.append(nr)
                nr = [cid]
                seen.add(cid)
                load = demand[cid]
        cleaned.append(nr)

    missing = [cid for cid in customer_ids if cid not in seen]
    for cid in missing:
        placed = False
        for r in cleaned:
            load = 0.0
            for x in r:
                load += demand[x]
            if load + demand[cid] <= capacity + 1e-12:
                r.append(cid)
                placed = True
                break
        if not placed:
            cleaned.append([cid])

    routes = [r for r in cleaned if r]

    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            r = routes[i]
            if len(r) < 2:
                continue
            best_r = r[:]
            best_cost = route_cost(r, coords, depot_point)
            n = len(r)
            for a in range(n):
                for b in range(a + 1, n):
                    cand = r[:a] + r[a:b + 1][::-1] + r[b + 1:]
                    c = route_cost(cand, coords, depot_point)
                    if c + 1e-12 < best_cost:
                        best_cost = c
                        best_r = cand
            if best_r != r:
                routes[i] = best_r
                improved = True

        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                ri = routes[i]
                rj = routes[j]
                if not ri or not rj:
                    continue
                load_i = 0.0
                for x in ri:
                    load_i += demand[x]
                load_j = 0.0
                for x in rj:
                    load_j += demand[x]
                bi = route_cost(ri, coords, depot_point)
                bj = route_cost(rj, coords, depot_point)
                done = False
