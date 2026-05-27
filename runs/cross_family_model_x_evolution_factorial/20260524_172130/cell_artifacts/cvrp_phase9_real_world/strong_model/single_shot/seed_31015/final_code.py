def solve_cvrp(instance):
    def attr(obj, name, default=None):
        if isinstance(obj, dict):
            return obj.get(name, default)
        d = obj.__dict__ if hasattr(obj, "__dict__") else None
        if d is not None:
            return d.get(name, default)
        return default

    def as_list(x):
        if x is None:
            return None
        if isinstance(x, list):
            return x
        if isinstance(x, tuple):
            return list(x)
        try:
            return list(x)
        except Exception:
            return None

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    cap = attr(instance, "capacity", None)
    if cap is None:
        cap = attr(instance, "vehicle_capacity", None)
    if cap is None:
        cap = attr(instance, "cap", None)
    if cap is None:
        cap = 0.0

    coords = attr(instance, "coordinates", None)
    if coords is None:
        coords = attr(instance, "coords", None)
    if coords is None:
        coords = attr(instance, "points", None)

    demands = attr(instance, "demands", None)
    if demands is None:
        demands = attr(instance, "demand", None)

    depot = attr(instance, "depot", 0)

    coord_map = {}
    if isinstance(coords, dict):
        for k, v in coords.items():
            coord_map[k] = (float(v[0]), float(v[1]))
    else:
        cl = as_list(coords)
        if cl is not None:
            for i, v in enumerate(cl):
                coord_map[i] = (float(v[0]), float(v[1]))

    if depot not in coord_map:
        depot = 0 if 0 in coord_map else (next(iter(coord_map)) if coord_map else 0)
    depot_coord = coord_map.get(depot, (0.0, 0.0))

    demand_map = {}
    if isinstance(demands, dict):
        for k, v in demands.items():
            demand_map[k] = float(v)
    else:
        dl = as_list(demands)
        if dl is not None:
            for i, v in enumerate(dl):
                demand_map[i] = float(v)

    ids = [k for k in coord_map.keys() if k != depot]
    if not ids:
        ids = [k for k in demand_map.keys() if k != depot]
    ids = sorted(ids)

    def dem(c):
        return demand_map.get(c, 0.0)

    def co(c):
        return coord_map.get(c, depot_coord)

    def route_cost(route):
        if not route:
            return 0.0
        total = dist(depot_coord, co(route[0]))
        for i in range(len(route) - 1):
            total += dist(co(route[i]), co(route[i + 1]))
        total += dist(co(route[-1]), depot_coord)
        return total

    def route_load(route):
        s = 0.0
        for c in route:
            s += dem(c)
        return s

    def sort_key(c):
        x, y = co(c)
        dx = x - depot_coord[0]
        dy = y - depot_coord[1]
        ang = 0 if dx == 0 and dy == 0 else (dy / (abs(dx) + abs(dy) + 1e-12) + (2.0 if dx < 0 else 0.0))
        return (ang, dist(co(c), depot_coord), c)

    ordered = sorted(ids, key=sort_key)
    routes = []
    cur = []
    load = 0.0
    for c in ordered:
        d = dem(c)
        if cur and load + d > cap:
            routes.append(cur)
            cur = []
            load = 0.0
        cur.append(c)
        load += d
    if cur:
        routes.append(cur)

    def improve(route):
        if len(route) <= 2:
            return route[:]
        r = route[:]
        best = route_cost(r)
        improved = True
        while improved:
            improved = False
            n = len(r)
            for i in range(n - 2):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    cand = r[:i + 1] + r[i + 1:j + 1][::-1] + r[j + 1:]
                    cc = route_cost(cand)
                    if cc + 1e-12 < best:
                        r = cand
                        best = cc
                        improved = True
                        break
                if improved:
                    break
        return r

    routes = [improve(r) for r in routes if r]

    changed = True
    while changed:
        changed = False
        loads = [route_load(r) for r in routes]
        for i in range(len(routes)):
            if not routes[i]:
                continue
            for p, c in enumerate(routes[i]):
                dc = dem(c)
                best = None
                best_delta = 0.0
                for j in range(len(routes)):
                    if i == j:
                        continue
                    if loads[j] + dc > cap:
                        continue
                    r1 = routes[i][:p] + routes[i][p + 1:]
                    r2 = routes[j][:]
                    if not r1:
                        new1 = []
                        c1 = 0.0
                    else:
                        new1 = improve(r1)
                        c1 = route_cost(new1)
                    best2 = None
                    c2 = None
                    for k in range(len(r2) + 1):
                        cand = r2[:k] + [c] + r2[k:]
                        cand = improve(cand)
                        cc = route_cost(cand)
                        if c2 is None or cc < c2:
                            c2 = cc
                            best2 = cand
                    delta = c1 + c2 - route_cost(routes[i]) - route_cost(routes[j])
                    if best is None or delta < best_delta:
                        best = (j, new1, best2)
                        best_delta = delta
                if best is not None and best_delta < -1e-9:
                    j, new1, new2 = best
                    routes[i] = new1
                    routes[j] = new2
                    changed = True
                    break
            if changed:
                break
        routes = [r for r in routes if r]

    seen = set()
    final_routes = []
    for r in routes:
        rr = []
        for c in r:
            if c != depot and c not in seen:
                seen.add(c)
                rr.append(c)
        if rr:
            final_routes.append(rr)

    missing = [c for c in ids if c not in seen]
    for c in missing:
        placed = False
        dc = dem(c)
        best_i = None
        best_route = None
        best_cost = None
        for i, r in enumerate(final_routes):
            if route_load(r) + dc > cap:
                continue
            for k in range(len(r) + 1):
                cand = r[:k] + [c] + r[k:]
                cand = improve(cand)
                cc = route_cost(cand)
                if best_cost is None or cc < best_cost:
                    best_cost = cc
                    best_i = i
                    best_route = cand
        if best_i is not None:
            final_routes[best_i] = best_route
            placed = True
        if not placed:
            final_routes.append([c])

    return final_routes
