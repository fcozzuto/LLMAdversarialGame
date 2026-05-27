def solve_cvrp(instance):
    def get_any(obj, keys, default=None):
        if obj is None:
            return default
        try:
            for k in keys:
                try:
                    if k in obj:
                        return obj[k]
                except Exception:
                    pass
        except Exception:
            pass
        try:
            d = obj.__dict__
            for k in keys:
                if k in d:
                    return d[k]
        except Exception:
            pass
        return default

    coords = get_any(instance, ["coordinates", "coords", "locations", "points", "xy"])
    demands = get_any(instance, ["demands", "demand"])
    capacity = get_any(instance, ["capacity", "vehicle_capacity", "cap"])

    if coords is None:
        nodes = get_any(instance, ["nodes", "customers"])
        if nodes is not None:
            coords = []
            for n in nodes:
                coords.append(get_any(n, ["coord", "coordinates", "location", "xy"]))
    if demands is None:
        if coords is not None:
            demands = [0] * len(coords)
        else:
            demands = [0]

    if coords is not None:
        n = len(coords) - 1
    else:
        n = len(demands) - 1
    if n < 0:
        n = 0

    if capacity is None:
        s = 0
        for i in range(1, len(demands)):
            s += demands[i]
        capacity = s if s > 0 else 1

    def demand_of(i):
        if 0 <= i < len(demands):
            return demands[i]
        return 0

    def dist(i, j):
        if coords is None:
            return 0.0
        if i < 0 or j < 0 or i >= len(coords) or j >= len(coords):
            return 0.0
        a = coords[i]
        b = coords[j]
        if a is None or b is None:
            return 0.0
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    customers = [i for i in range(1, n + 1)]

    # Deterministic sweep ordering
    order = customers[:]
    if coords is not None and len(coords) > 0 and coords[0] is not None:
        depot = coords[0]
        tmp = []
        for i in customers:
            if i >= len(coords) or coords[i] is None:
                tmp.append((2, 0.0, 0.0, i))
            else:
                x, y = coords[i]
                dx = x - depot[0]
                dy = y - depot[1]
                ang_key = 0 if (dy > 0 or (dy == 0 and dx >= 0)) else 1
                tmp.append((ang_key, dy / (abs(dx) + abs(dy) + 1e-12), dx * dx + dy * dy, i))
        tmp.sort()
        order = [t[3] for t in tmp]
    else:
        tmp = []
        for i in customers:
            tmp.append((-demand_of(i), i))
        tmp.sort()
        order = [t[1] for t in tmp]

    # Initial feasible routes
    routes = []
    cur = []
    load = 0
    for c in order:
        d = demand_of(c)
        if cur and load + d > capacity:
            routes.append(cur)
            cur = []
            load = 0
        cur.append(c)
        load += d
    if cur:
        routes.append(cur)

    def route_load(r):
        s = 0
        for c in r:
            s += demand_of(c)
        return s

    def route_cost(r):
        if not r:
            return 0.0
        s = dist(0, r[0])
        for i in range(len(r) - 1):
            s += dist(r[i], r[i + 1])
        s += dist(r[-1], 0)
        return s

    def total_cost(rs):
        s = 0.0
        for r in rs:
            s += route_cost(r)
        return s

    # Intra-route 2-opt
    improved = True
    while improved:
        improved = False
        for ri in range(len(routes)):
            r = routes[ri]
            m = len(r)
            if m < 4:
                continue
            base = route_cost(r)
            best_r = None
            best_delta = 0.0
            for i in range(m - 2):
                for j in range(i + 2, m):
                    nr = r[:i + 1] + r[i + 1:j + 1][::-1] + r[j + 1:]
                    delta = route_cost(nr) - base
                    if delta < best_delta:
                        best_delta = delta
                        best_r = nr
            if best_r is not None:
                routes[ri] = best_r
                improved = True

    # Inter-route relocate and swap
    for _ in range(3):
        moved = True
        while moved:
            moved = False
            best = None
            best_gain = 0.0
            for i in range(len(routes)):
                ri = routes[i]
                ci_len = len(ri)
                if ci_len == 0:
                    continue
                for p in range(ci_len):
                    c = ri[p]
                    dc = demand_of(c)
                    ri_removed = ri[:p] + ri[p + 1:]
                    old_i_cost = route_cost(ri)
                    new_i_cost = route_cost(ri_removed) if ri_removed else 0.0
                    for j in range(len(routes)):
                        if i == j:
                            continue
                        rj = routes[j]
                        if route_load(rj) + dc > capacity:
                            continue
                        old_j_cost = route_cost(rj)
                        for pos in range(len(rj) + 1):
                            nrj = rj[:pos] + [c] + rj[pos:]
                            gain = (old_i_cost + old_j_cost) - (new_i_cost + route_cost(nrj))
                            if gain > best_gain + 1e-12:
                                best_gain = gain
                                best = ("rel", i, j, p, pos, ri_removed, nrj)
            if best is not None:
                _, i, j, p, pos, ri_removed, nrj = best
                routes[i] = ri_removed
                routes[j] = nrj
                if not routes[i]:
                    routes.pop(i)
                moved = True

        swapped = True
        while swapped:
            swapped = False
            best = None
            best_gain = 0.0
            for i in range(len(routes)):
                ri = routes[i]
                for j in range(i + 1, len(routes)):
                    rj = routes[j]
                    li = route_load(ri)
                    lj = route_load(rj)
                    for a in range(len(ri)):
                        ca = ri[a]
                        da = demand_of(ca)
                        for b in range(len(rj)):
                            cb = rj[b]
                            db = demand_of(cb)
                            if li - da + db > capacity:
                                continue
                            if lj - db + da > capacity:
                                continue
                            nri = ri[:a] + [cb] + ri[a + 1:]
                            nrj = rj[:b] + [ca] + rj[b + 1:]
                            gain = (route_cost(ri) + route_cost(rj)) - (route_cost(nri) + route_cost(nrj))
                            if gain > best_gain + 1e-12:
                                best_gain = gain
                                best = (i, j, nri, nrj)
            if best is not None:
                i, j, nri, nrj = best
                routes[i] = nri
                routes[j] = nrj
                swapped = True

    # Final cleanup: remove empties and ensure all customers appear once
    clean = []
    seen = {}
    for r in routes:
        nr = []
        load = 0
        for c in r:
            if c not in seen:
                seen[c] = 1
                nr.append(c)
                load += demand_of(c)
        if nr:
            clean.append(nr)
    routes = clean

    missing = []
    for c in customers:
        if c not in seen:
            missing.append(c)

    for c in missing:
        d = demand_of(c)
        best_idx = -1
        best_pos = 0
        best_cost = None
        for i in range(len(routes)):
            if route_load(routes[i]) + d > capacity:
                continue
            r = routes[i]
            for pos in range(len(r) + 1):
                nr = r[:pos] + [c] + r[pos:]
                cc = route_cost(nr)
                if best_cost is None or cc < best_cost:
                    best_cost = cc
                    best_idx = i
                    best_pos = pos
        if best_idx == -1:
            routes.append([c])
        else:
            r = routes[best_idx]
            routes[best_idx] = r[:best_pos] + [c] + r[best_pos:]

    return routes
