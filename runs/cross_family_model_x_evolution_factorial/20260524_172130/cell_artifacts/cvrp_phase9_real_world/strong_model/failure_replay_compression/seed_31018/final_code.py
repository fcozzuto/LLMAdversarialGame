def solve_cvrp(instance):
    def getv(obj, *keys, default=None):
        if isinstance(obj, dict):
            for k in keys:
                if k in obj:
                    return obj[k]
            return default
        d = obj.__dict__ if hasattr(obj, "__dict__") else None
        if d is not None:
            for k in keys:
                if k in d:
                    return d[k]
        return default

    def xy_of(rec):
        if isinstance(rec, dict):
            if "x" in rec and "y" in rec:
                return rec["x"], rec["y"]
            for k in ("coord", "coords", "pos", "position"):
                if k in rec and rec[k] is not None:
                    c = rec[k]
                    return c[0], c[1]
        else:
            d = rec.__dict__ if hasattr(rec, "__dict__") else None
            if d is not None:
                if "x" in d and "y" in d:
                    return d["x"], d["y"]
                for k in ("coord", "coords", "pos", "position"):
                    if k in d and d[k] is not None:
                        c = d[k]
                        return c[0], c[1]
        return None

    def id_of(rec, fallback):
        if isinstance(rec, dict):
            for k in ("id", "customer_id", "node_id"):
                if k in rec:
                    return rec[k]
        else:
            d = rec.__dict__ if hasattr(rec, "__dict__") else None
            if d is not None:
                for k in ("id", "customer_id", "node_id"):
                    if k in d:
                        return d[k]
        return fallback

    def demand_of(rec):
        if isinstance(rec, dict):
            for k in ("demand", "dem", "q"):
                if k in rec:
                    return rec[k]
        else:
            d = rec.__dict__ if hasattr(rec, "__dict__") else None
            if d is not None:
                for k in ("demand", "dem", "q"):
                    if k in d:
                        return d[k]
        return 0

    cap = getv(instance, "capacity", "vehicle_capacity", "cap", default=None)
    depot = getv(instance, "depot", default=None)
    customers = getv(instance, "customers", "nodes", "points", default=[])
    dist = getv(instance, "distance_matrix", "dist_matrix", default=None)

    depot_id = 0
    depot_xy = (0.0, 0.0)
    if depot is not None:
        depot_id = id_of(depot, 0)
        xy = xy_of(depot)
        if xy is not None:
            depot_xy = (float(xy[0]), float(xy[1]))

    if not customers:
        return []

    items = []
    for i, rec in enumerate(customers):
        rid = id_of(rec, i + 1)
        if rid == depot_id:
            xy = xy_of(rec)
            if xy is not None:
                depot_xy = (float(xy[0]), float(xy[1]))
            continue
        xy = xy_of(rec)
        if xy is None:
            xy = (float(rid), 0.0)
        items.append((rid, float(xy[0]), float(xy[1]), float(demand_of(rec))))

    if not items:
        return []

    if cap is None:
        cap = sum(d for _, _, _, d in items)

    coords = {rid: (x, y) for rid, x, y, _ in items}
    demand = {rid: d for rid, _, _, d in items}
    all_ids = [rid for rid, _, _, _ in items]
    pos_of = {rid: i for i, (rid, _, _, _) in enumerate(items)}

    def dist_id(a, b):
        if a == b:
            return 0.0
        if dist is not None:
            ia = pos_of.get(a)
            ib = pos_of.get(b)
            if ia is not None and ib is not None:
                return float(dist[ia][ib])
        ax, ay = depot_xy if a == depot_id else coords[a]
        bx, by = depot_xy if b == depot_id else coords[b]
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    def route_load(route):
        s = 0.0
        for c in route:
            s += demand[c]
        return s

    def route_len(route):
        if not route:
            return 0.0
        t = dist_id(depot_id, route[0])
        for i in range(len(route) - 1):
            t += dist_id(route[i], route[i + 1])
        return t + dist_id(route[-1], depot_id)

    def best_insert(route, c):
        n = len(route)
        best_p, best_d = 0, None
        for p in range(n + 1):
            left = depot_id if p == 0 else route[p - 1]
            right = depot_id if p == n else route[p]
            delta = dist_id(left, c) + dist_id(c, right) - dist_id(left, right)
            if best_d is None or delta < best_d:
                best_d, best_p = delta, p
        return best_p, best_d

    def two_opt(route):
        r = route[:]
        n = len(r)
        if n < 4:
            return r
        improved = True
        while improved:
            improved = False
            base = route_len(r)
            for i in range(n - 2):
                for k in range(i + 2, n):
                    if i == 0 and k == n - 1:
                        continue
                    nr = r[:i + 1] + r[i + 1:k + 1][::-1] + r[k + 1:]
                    if route_len(nr) + 1e-12 < base:
                        r = nr
                        n = len(r)
                        improved = True
                        break
                if improved:
                    break
        return r

    unserved = set(all_ids)
    seed_order = sorted(all_ids, key=lambda c: (-(coords[c][0] - depot_xy[0]) ** 2 - (coords[c][1] - depot_xy[1]) ** 2, -demand[c], c))
    routes = []

    for seed in seed_order:
        if seed not in unserved:
            continue
        route = [seed]
        unserved.remove(seed)
        load = demand[seed]
        while True:
            best = None
            for c in list(unserved):
                if load + demand[c] > cap:
                    continue
                p, dlt = best_insert(route, c)
                key = (dlt, -dist_id(depot_id, c), c)
                if best is None or key < best[0]:
                    best = (key, c, p)
            if best is None:
                break
            _, c, p = best
            route.insert(p, c)
            load += demand[c]
            unserved.remove(c)
        routes.append(route)

    for c in list(unserved):
        routes.append([c])
        unserved.remove(c)

    for i in range(len(routes)):
        routes[i] = two_opt(routes[i])

    changed = True
    while changed:
        changed = False
        best_move = None
        best_delta = 0.0
        for i in range(len(routes)):
            ri = routes[i]
            li = route_load(ri)
            for p, c in enumerate(ri):
                rem = ri[:p] + ri[p + 1:]
                gain_remove = route_len(ri) - route_len(rem)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    if route_load(rj) + demand[c] > cap:
                        continue
                    pos, ins = best_insert(rj, c)
                    delta = route_len(rem) + (route_len(rj) + ins) - (route_len(ri) + route_len(rj))
                    if best_move is None or delta < best_delta:
                        best_delta = delta
                        best_move = (i, j, p, pos, c)
        if best_move is not None and best_delta < -1e-9:
            i, j, p, pos, c = best_move
            if i < len(routes) and j < len(routes) and p < len(routes[i]) and routes[i][p] == c:
                routes[i].pop(p)
                routes[j].insert(pos, c)
                if not routes[i]:
                    routes.pop(i)
                changed = True
                continue

        merged = False
        for i in range(len(routes)):
            if merged:
                break
            for j in range(i + 1, len(routes)):
                a, b = routes[i], routes[j]
                if route_load(a) + route_load(b) > cap:
                    continue
                cands = [a + b, a + b[::-1], a[::-1] + b, a[::-1] + b[::-1], b + a, b + a[::-1], b[::-1] + a, b[::-1] + a[::-1]]
                best_cand = None
                best_len = None
                for cand in cands:
                    L = route_len(cand)
                    if best_len is None or L < best_len:
                        best_len = L
                        best_cand = cand
                if best_len + 1e-12 < route_len(a) + route_len(b):
                    routes[i] = best_cand
                    routes.pop(j)
                    changed = True
                    merged = True
                    break

    for i in range(len(routes)):
        routes[i] = two_opt(routes[i])

    seen = set()
    final_routes = []
    for r in routes:
        nr = []
        for c in r:
            if c not in seen:
                seen.add(c)
                nr.append(c)
        if nr:
            final_routes.append(nr)

    for c in all_ids:
        if c in seen:
            continue
        placed = False
        best = None
        for i in range(len(final_routes)):
            if route_load(final_routes[i]) + demand[c] > cap:
                continue
            pos, dlt = best_insert(final_routes[i], c)
            key = (dlt, len(final_routes[i]), i)
            if best is None or key < best[0]:
                best = (key, i, pos)
        if best is None:
            final_routes.append([c])
        else:
            _, i, pos = best
            final_routes[i].insert(pos, c)

    return final_routes
