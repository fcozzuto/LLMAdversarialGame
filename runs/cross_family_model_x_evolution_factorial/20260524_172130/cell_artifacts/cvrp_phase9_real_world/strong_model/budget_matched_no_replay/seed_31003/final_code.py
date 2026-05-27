def solve_cvrp(instance):
    def pick(*keys, default=None):
        for k in keys:
            if k in instance:
                return instance[k]
        return default

    def num(x, default=0.0):
        try:
            return float(x)
        except Exception:
            return float(default)

    def coords_of(node):
        if isinstance(node, dict):
            if "x" in node and "y" in node:
                return num(node["x"]), num(node["y"])
            if 0 in node and 1 in node:
                return num(node[0]), num(node[1])
        if isinstance(node, (list, tuple)) and len(node) >= 2:
            return num(node[0]), num(node[1])
        return None

    depot = pick("depot", "depot_coord", "depot_location", default=None)
    if depot is None and "nodes" in instance and instance["nodes"]:
        depot = instance["nodes"][0]
    depot_xy = coords_of(depot) if depot is not None else (0.0, 0.0)

    customers = None
    if "customers" in instance:
        customers = instance["customers"]
    elif "nodes" in instance:
        customers = instance["nodes"][1:]
    elif "coordinates" in instance:
        customers = instance["coordinates"]
    elif "locations" in instance:
        customers = instance["locations"]
    else:
        customers = []

    cap = pick("capacity", "vehicle_capacity", "cap", default=None)
    demand_in = pick("demands", "demand", default=None)

    ids = []
    pos = {}
    dem = {}

    if isinstance(customers, dict):
        items = list(customers.items())
        for cid, node in items:
            if cid == 0 or cid == "0":
                continue
            ids.append(cid)
            c = coords_of(node)
            if c is not None:
                pos[cid] = c
            d = None
            if isinstance(node, dict) and "demand" in node:
                d = num(node["demand"], 1.0)
            dem[cid] = d
    else:
        for i, node in enumerate(customers):
            cid = i + 1
            if isinstance(node, dict) and "id" in node:
                cid = node["id"]
            if cid == 0:
                continue
            ids.append(cid)
            c = coords_of(node)
            if c is not None:
                pos[cid] = c
            d = None
            if isinstance(node, dict) and "demand" in node:
                d = num(node["demand"], 1.0)
            dem[cid] = d

    if isinstance(demand_in, dict):
        for cid in ids:
            if dem.get(cid) is None:
                dem[cid] = num(demand_in.get(cid, demand_in.get(str(cid), 1.0)), 1.0)
    elif isinstance(demand_in, (list, tuple)):
        for i, cid in enumerate(ids):
            if dem.get(cid) is None:
                dem[cid] = num(demand_in[i], 1.0) if i < len(demand_in) else 1.0

    for cid in ids:
        if dem.get(cid) is None:
            dem[cid] = 1.0

    if cap is None:
        cap = sum(dem[c] for c in ids)
        if cap <= 0:
            cap = 1.0

    def dist(a, b):
        ax, ay = depot_xy if a == 0 else pos[a]
        bx, by = depot_xy if b == 0 else pos[b]
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    def route_load(r):
        s = 0.0
        for c in r:
            s += dem[c]
        return s

    def route_cost(r):
        if not r:
            return 0.0
        c = dist(0, r[0])
        for i in range(len(r) - 1):
            c += dist(r[i], r[i + 1])
        return c + dist(r[-1], 0)

    def angle_key(cid):
        x, y = pos[cid]
        dx = x - depot_xy[0]
        dy = y - depot_xy[1]
        quad = 0
        if dy < 0 or (dy == 0 and dx < 0):
            quad = 1
        adx = abs(dx)
        ady = abs(dy)
        ratio = ady / (adx + ady + 1e-12)
        return (quad, ratio, dist(0, cid), -dem[cid], cid)

    unassigned = sorted(ids, key=angle_key)
    routes = []

    while unassigned:
        start = min(unassigned, key=lambda c: (dist(0, c), -dem[c], c))
        route = [start]
        unassigned.remove(start)
        load = dem[start]
        last = start
        while True:
            best = None
            best_key = None
            for c in unassigned:
                d = dem[c]
                if load + d > cap:
                    continue
                k = (dist(last, c), dist(0, c), -d, c)
                if best_key is None or k < best_key:
                    best_key = k
                    best = c
            if best is None:
                break
            route.append(best)
            unassigned.remove(best)
            load += dem[best]
            last = best
        routes.append(route)

    def two_opt(r):
        n = len(r)
        if n < 4:
            return r[:]
        best = r[:]
        best_c = route_cost(best)
        improved = True
        while improved:
            improved = False
            n = len(best)
            for i in range(n - 2):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    cand = best[:i + 1] + best[i + 1:j + 1][::-1] + best[j + 1:]
                    c = route_cost(cand)
                    if c + 1e-12 < best_c:
                        best = cand
                        best_c = c
                        improved = True
                        break
                if improved:
                    break
        return best

    routes = [two_opt(r) for r in routes]

    def can_insert(route, cust):
        return route_load(route) + dem[cust] <= cap + 1e-12

    changed = True
    while changed:
        changed = False
        for i in range(len(routes)):
            for a in range(len(routes[i])):
                c = routes[i][a]
                for j in range(len(routes)):
                    if i == j:
                        continue
                    if not can_insert(routes[j], c):
                        continue
                    ri = routes[i][:a] + routes[i][a + 1:]
                    if not ri:
                        continue
                    base = route_cost(routes[i]) + route_cost(routes[j])
                    best_rj = None
                    best_val = None
                    for p in range(len(routes[j]) + 1):
                        rj = routes[j][:p] + [c] + routes[j][p:]
                        val = route_cost(ri) + route_cost(rj)
                        gain = base - val
                        if best_val is None or gain > best_val or (gain == best_val and rj < best_rj):
                            best_val = gain
                            best_rj = rj
                    if best_val is not None and best_val > 1e-12:
                        routes[i] = two_opt(ri)
                        routes[j] = two_opt(best_rj)
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break

    seen = {}
    for r in routes:
        for c in r:
            seen[c] = seen.get(c, 0) + 1

    if any(seen.get(c, 0) != 1 for c in ids):
        remaining = sorted(ids, key=angle_key)
        routes = []
        while remaining:
            start = min(remaining, key=lambda c: (dist(0, c), -dem[c], c))
            route = [start]
            remaining.remove(start)
            load = dem[start]
            last = start
            while True:
                best = None
                best_key = None
                for c in remaining:
                    d = dem[c]
                    if load + d > cap:
                        continue
                    k = (dist(last, c), dist(0, c), -d, c)
                    if best_key is None or k < best_key:
                        best_key = k
                        best = c
                if best is None:
                    break
                route.append(best)
                remaining.remove(best)
                load += dem[best]
                last = best
            routes.append(two_opt(route))

    return routes
