def solve_cvrp(instance):
    def gd(d, keys, default=None):
        if isinstance(d, dict):
            for k in keys:
                if k in d:
                    return d[k]
        return default

    def as_map(x):
        if isinstance(x, dict):
            return dict(x)
        if isinstance(x, (list, tuple)):
            return {i: x[i] for i in range(len(x))}
        return {}

    def parse(inst):
        depot = 0
        cap = 10**18
        demands = {}
        coords = {}
        matrix = None
        if isinstance(inst, dict):
            depot = gd(inst, ["depot", "depot_id", "start", "origin"], 0)
            cap = gd(inst, ["capacity", "vehicle_capacity", "cap"], cap)
            demands = as_map(gd(inst, ["demands", "demand"], {}))
            coords = as_map(gd(inst, ["coords", "coordinates", "locations", "points", "xy"], {}))
            matrix = gd(inst, ["distance_matrix", "distances", "matrix"], None)
        elif isinstance(inst, (list, tuple)):
            if len(inst) >= 1 and isinstance(inst[0], dict):
                return parse(inst[0])
            if len(inst) >= 2:
                demands = as_map(inst[1])
            if len(inst) >= 3:
                coords = as_map(inst[2])
            if len(inst) >= 4:
                cap = inst[3]
        if cap is None:
            cap = 10**18
        return depot, cap, demands, coords, matrix

    depot, capacity, demands, coords, matrix = parse(instance)

    def dist(a, b):
        if a == b:
            return 0.0
        if matrix is not None:
            try:
                return matrix[a][b]
            except Exception:
                try:
                    return matrix[a, b]
                except Exception:
                    pass
        pa = coords.get(a)
        pb = coords.get(b)
        if pa is not None and pb is not None:
            dx = pa[0] - pb[0]
            dy = pa[1] - pb[1]
            return (dx * dx + dy * dy) ** 0.5
        return abs(a - b)

    customers = [c for c in (demands.keys() if demands else coords.keys() if coords else range(len(matrix) if matrix is not None else 0)) if c != depot]
    customers = sorted(customers)
    for c in customers:
        demands.setdefault(c, 0)

    def load(route):
        s = 0
        for c in route:
            s += demands.get(c, 0)
        return s

    def rcost(route):
        if not route:
            return 0.0
        c = dist(depot, route[0])
        for i in range(len(route) - 1):
            c += dist(route[i], route[i + 1])
        return c + dist(route[-1], depot)

    if coords and depot in coords:
        dx0, dy0 = coords[depot]
        def key(c):
            p = coords.get(c)
            if p is None:
                return (10, 0.0, c)
            dx = p[0] - dx0
            dy = p[1] - dy0
            quad = 0 if dy >= 0 and dx >= 0 else 1 if dy >= 0 else 2 if dx < 0 else 3
            ang = dy / (abs(dx) + abs(dy) + 1e-12)
            return (quad, ang, dist(depot, c), c)
        ordered = sorted(customers, key=key)
    else:
        ordered = sorted(customers, key=lambda c: (-demands.get(c, 0), c))

    unserved = set(customers)
    routes = []
    while unserved:
        seed = next((c for c in ordered if c in unserved), None)
        if seed is None:
            break
        r = [seed]
        unserved.remove(seed)
        cur = seed
        cap_left = capacity - demands.get(seed, 0)
        while True:
            best = None
            bestk = None
            for c in unserved:
                d = demands.get(c, 0)
                if d > cap_left:
                    continue
                k = (dist(cur, c), dist(depot, c), -d, c)
                if best is None or k < bestk:
                    best = c
                    bestk = k
            if best is None:
                break
            r.append(best)
            unserved.remove(best)
            cap_left -= demands.get(best, 0)
            cur = best
        routes.append(r)

    def two_opt(r):
        n = len(r)
        if n < 4:
            return r
        improved = True
        while improved:
            improved = False
            base = rcost(r)
            for i in range(n - 2):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    nr = r[:i + 1] + r[i + 1:j + 1][::-1] + r[j + 1:]
                    nc = rcost(nr)
                    if nc + 1e-12 < base:
                        r = nr
                        n = len(r)
                        base = nc
                        improved = True
                        break
                if improved:
                    break
        return r

    routes = [two_opt(r) for r in routes if r]

    changed = True
    while changed:
        changed = False
        routes = [r for r in routes if r]
        for i in range(len(routes)):
            nr = two_opt(routes[i])
            if nr != routes[i]:
                routes[i] = nr
                changed = True

        best = None
        best_delta = 0.0
        costs = [rcost(r) for r in routes]
        loads = [load(r) for r in routes]
        for i, r1 in enumerate(routes):
            for p, c in enumerate(r1):
                dc = demands.get(c, 0)
                rem1 = r1[:p] + r1[p + 1:]
                if not rem1:
                    continue
                c1 = rcost(rem1)
                for j, r2 in enumerate(routes):
                    if i == j or loads[j] + dc > capacity:
                        continue
                    base = costs[i] + costs[j]
                    for ins in range(len(r2) + 1):
                        nr2 = r2[:ins] + [c] + r2[ins:]
                        delta = c1 + rcost(nr2) - base
                        cand = (i, p, j, ins, c)
                        if delta < best_delta - 1e-12 or (abs(delta - best_delta) <= 1e-12 and (best is None or cand < best)):
                            best = cand
                            best_delta = delta
        if best is not None and best_delta < -1e-12:
            i, p, j, ins, c = best
            routes[i] = routes[i][:p] + routes[i][p + 1:]
            routes[j] = routes[j][:ins] + [c] + routes[j][ins:]
            changed = True
            continue

        best = None
        best_delta = 0.0
        costs = [rcost(r) for r in routes]
        loads = [load(r) for r in routes]
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                r1, r2 = routes[i], routes[j]
                for p, a in enumerate(r1):
                    da = demands.get(a, 0)
                    for q, b in enumerate(r2):
                        db = demands.get(b, 0)
                        if loads[i] - da + db > capacity or loads[j] - db + da > capacity:
                            continue
                        nr1 = r1[:p] + [b] + r1[p + 1:]
                        nr2 = r2[:q] + [a] + r2[q + 1:]
                        delta = rcost(nr1) + rcost(nr2) - costs[i] - costs[j]
                        cand = (i, p, j, q, a, b)
                        if delta < best_delta - 1e-12 or (abs(delta - best_delta) <= 1e-12 and (best is None or cand < best)):
                            best = cand
                            best_delta = delta
        if best is not None and best_delta < -1e-12:
            i, p, j, q, a, b = best
            routes[i] = routes[i][:p] + [b] + routes[i][p + 1:]
            routes[j] = routes[j][:q] + [a] + routes[j][q + 1:]
            changed = True

    seen = set()
    for r in routes:
        for c in r:
            seen.add(c)
    missing = [c for c in customers if c not in seen]
    for c in missing:
        placed = False
        for i in range(len(routes)):
            if load(routes[i]) + demands.get(c, 0) <= capacity:
                r = routes[i]
                best_pos = 0
                best_inc = None
                for pos in range(len(r) + 1):
                    nr = r[:pos] + [c] + r[pos:]
                    inc = rcost(nr) - rcost(r)
                    if best_inc is None or inc < best_inc:
                        best_inc = inc
                        best_pos = pos
                routes[i] = r[:best_pos] + [c] + r[best_pos:]
                placed = True
                break
        if not placed:
            routes.append([c])

    return [r for r in routes if r]
