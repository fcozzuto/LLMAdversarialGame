def solve_cvrp(instance):
    def get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        try:
            return obj[key]
        except Exception:
            pass
        try:
            d = obj.__dict__
            if key in d:
                return d[key]
        except Exception:
            pass
        return default

    def safe_list(x):
        if x is None:
            return []
        return list(x)

    depot = get(instance, "depot", 0)
    n = get(instance, "n", None)
    customers = get(instance, "customers", None)
    demands = get(instance, "demands", None)
    coords = get(instance, "coords", None)
    if coords is None:
        coords = get(instance, "positions", None)
    dist_matrix = get(instance, "distance_matrix", None)
    if dist_matrix is None:
        dist_matrix = get(instance, "dist", None)

    if customers is None:
        if n is not None:
            customers = [i for i in range(n) if i != depot]
        elif isinstance(demands, dict):
            customers = [k for k in demands.keys() if k != depot]
        elif coords is not None:
            customers = [i for i in range(len(coords)) if i != depot]
        elif dist_matrix is not None:
            customers = [i for i in range(len(dist_matrix)) if i != depot]
        else:
            customers = []
    customers = [c for c in safe_list(customers) if c != depot]

    capacity = get(instance, "capacity", None)
    if capacity is None:
        capacity = get(instance, "vehicle_capacity", None)
    if capacity is None:
        capacity = 10**18

    if isinstance(demands, dict):
        demand = lambda c: demands.get(c, 0)
    elif isinstance(demands, (list, tuple)):
        demand = lambda c: demands[c] if 0 <= c < len(demands) else 0
    else:
        demand = lambda c: 0

    def dist(i, j):
        if dist_matrix is not None:
            return dist_matrix[i][j]
        if coords is not None:
            a = coords[i]
            b = coords[j]
            dx = a[0] - b[0]
            dy = a[1] - b[1]
            return (dx * dx + dy * dy) ** 0.5
        return abs(i - j)

    def route_load(r):
        s = 0
        for x in r:
            s += demand(x)
        return s

    def route_cost(r):
        if not r:
            return 0
        s = dist(depot, r[0])
        for i in range(len(r) - 1):
            s += dist(r[i], r[i + 1])
        s += dist(r[-1], depot)
        return s

    def route_delta_insert(r, c, pos):
        a = depot if pos == 0 else r[pos - 1]
        b = depot if pos == len(r) else r[pos]
        return dist(a, c) + dist(c, b) - dist(a, b)

    unserved = set(customers)
    routes = []
    if not unserved:
        return []

    ordered = sorted(unserved, key=lambda c: (-demand(c), -dist(depot, c), c))
    while ordered:
        seed = ordered.pop(0)
        if seed not in unserved:
            continue
        r = [seed]
        unserved.remove(seed)
        load = demand(seed)
        while unserved:
            best = None
            best_pos = None
            best_delta = None
            for c in sorted(unserved, key=lambda x: (dist(r[-1], x), -demand(x), x)):
                dc = demand(c)
                if load + dc > capacity:
                    continue
                for pos in range(len(r) + 1):
                    dlt = route_delta_insert(r, c, pos)
                    if best_delta is None or dlt < best_delta - 1e-12 or (abs(dlt - best_delta) <= 1e-12 and (c < best or (c == best and pos < best_pos))):
                        best = c
                        best_pos = pos
                        best_delta = dlt
            if best is None:
                break
            r.insert(best_pos, best)
            load += demand(best)
            unserved.remove(best)
        routes.append(r)

    if unserved:
        for c in sorted(unserved, key=lambda x: (-demand(x), dist(depot, x), x)):
            best_r = None
            best_pos = None
            best_delta = None
            for i, r in enumerate(routes):
                if route_load(r) + demand(c) > capacity:
                    continue
                for pos in range(len(r) + 1):
                    dlt = route_delta_insert(r, c, pos)
                    if best_delta is None or dlt < best_delta - 1e-12:
                        best_delta = dlt
                        best_r = i
                        best_pos = pos
            if best_r is None:
                routes.append([c])
            else:
                routes[best_r].insert(best_pos, c)
            unserved.discard(c)

    def two_opt_best(r):
        base = route_cost(r)
        best_r = r
        best_c = base
        n = len(r)
        for i in range(n - 2):
            for j in range(i + 2, n):
                cand = r[:i] + r[i:j + 1][::-1] + r[j + 1:]
                cc = route_cost(cand)
                if cc < best_c - 1e-12 or (abs(cc - best_c) <= 1e-12 and cand < best_r):
                    best_r = cand
                    best_c = cc
        return best_r, best_c, base

    improved = True
    while improved:
        improved = False

        for i in range(len(routes)):
            if len(routes[i]) >= 4:
                nr, nc, oc = two_opt_best(routes[i])
                if nc < oc - 1e-12:
                    routes[i] = nr
                    improved = True

        if improved:
            continue

        for i in range(len(routes)):
            ri = routes[i]
            li = route_load(ri)
            for aidx, a in enumerate(ri):
                da = demand(a)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    lj = route_load(rj)
                    if lj + da > capacity:
                        continue
                    ap = depot if aidx == 0 else ri[aidx - 1]
                    an = depot if aidx == len(ri) - 1 else ri[aidx + 1]
                    rem = dist(ap, an) - dist(ap, a) - dist(a, an)
                    for pos in range(len(rj) + 1):
                        ins = route_delta_insert(rj, a, pos)
                        if rem + ins < -1e-12:
                            nri = ri[:aidx] + ri[aidx + 1:]
                            nrj = rj[:pos] + [a] + rj[pos:]
                            if route_load(nri) <= capacity and route_load(nrj) <= capacity:
                                routes[i] = nri
                                routes[j] = nrj
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

        if improved:
            continue

        for i in range(len(routes)):
            ri = routes[i]
            li = route_load(ri)
            for j in range(i + 1, len(routes)):
                rj = routes[j]
                lj = route_load(rj)
                for ai, a in enumerate(ri):
                    da = demand(a)
                    for bj, b in enumerate(rj):
                        db = demand(b)
                        if li - da + db > capacity or lj - db + da > capacity:
                            continue
                        a0 = depot if ai == 0 else ri[ai - 1]
                        a1 = depot if ai == len(ri) - 1 else ri[ai + 1]
                        b0 = depot if bj == 0 else rj[bj - 1]
                        b1 = depot if bj == len(rj) - 1 else rj[bj + 1]
                        old = dist(a0, a) + dist(a, a1) + dist(b0, b) + dist(b, b1)
                        new = dist(a0, b) + dist(b, a1) + dist(b0, a) + dist(a, b1)
                        if new < old - 1e-12:
                            nr1 = ri[:]
                            nr2 = rj[:]
                            nr1[ai] = b
                            nr2[bj] = a
                            routes[i] = nr1
                            routes[j] = nr2
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    routes = [r for r in routes if r]

    seen = {}
    for r in routes:
        for c in r:
            seen[c] = seen.get(c, 0) + 1
    missing = [c for c in customers if seen.get(c, 0) == 0]
    bad = any(v != 1 for v in seen.values()) or bool(missing)
    if bad:
        routes = []
        unserved = set(customers)
        while unserved:
            seed = min(unserved, key=lambda c: (-demand(c), dist(depot, c), c))
            r = [seed]
            unserved.remove(seed)
            load = demand(seed)
            while True:
                best = None
                best_pos = None
                best_delta = None
                for c in sorted(unserved, key=lambda x: (dist(r[-1], x), -demand(x), x)):
                    if load + demand(c) > capacity:
                        continue
                    for pos in range(len(r) + 1):
                        dlt = route_delta_insert(r, c, pos)
                        if best_delta is None or dlt < best_delta - 1e-12 or (abs(dlt - best_delta) <= 1e-12 and (c < best or (c == best and pos < best_pos))):
                            best = c
                            best_pos = pos
                            best_delta = dlt
                if best is None:
                    break
                r.insert(best_pos, best)
                load += demand(best)
                unserved.remove(best)
            routes.append(r)

    return routes
