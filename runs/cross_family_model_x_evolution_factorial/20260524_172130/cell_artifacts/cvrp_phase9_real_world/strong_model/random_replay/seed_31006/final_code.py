def solve_cvrp(instance):
    def getv(obj, *keys, default=None):
        try:
            for k in keys:
                try:
                    if k in obj:
                        return obj[k]
                except:
                    pass
        except:
            pass
        try:
            d = vars(obj)
            for k in keys:
                if k in d:
                    return d[k]
        except:
            pass
        return default

    def as_list(x):
        try:
            return list(x)
        except:
            if x is None:
                return []
            return [x]

    coords = getv(instance, "coordinates", "coords", "locations", "points", default=None)
    demand = getv(instance, "demands", "demand", default=None)
    capacity = getv(instance, "capacity", "vehicle_capacity", "cap", default=0)
    try:
        capacity = float(capacity)
    except:
        capacity = 0.0

    def xy(i):
        try:
            if coords is None:
                return (0.0, 0.0)
            try:
                v = coords[i]
                return (float(v[0]), float(v[1]))
            except:
                return (0.0, 0.0)
        except:
            return (0.0, 0.0)

    def dem(i):
        try:
            if demand is None:
                return 0.0
            try:
                return float(demand[i])
            except:
                return 0.0
        except:
            return 0.0

    ids = []
    try:
        if demand is not None:
            try:
                ids = [k for k in demand.keys() if k != 0]
            except:
                ids = list(range(1, len(demand)))
        elif coords is not None:
            try:
                ids = [k for k in coords.keys() if k != 0]
            except:
                ids = list(range(1, len(coords)))
        else:
            ids = as_list(getv(instance, "customers", default=[]))
            ids = [i for i in ids if i != 0]
    except:
        ids = []

    ids = sorted(ids)
    if not ids:
        return []

    if capacity <= 0:
        return [[i] for i in ids]

    depot = 0
    dx, dy = xy(depot)

    def dist(i, j):
        xi, yi = xy(i)
        xj, yj = xy(j)
        a = xi - xj
        b = yi - yj
        return (a * a + b * b) ** 0.5

    # Deterministic sweep order
    def key(i):
        x, y = xy(i)
        return ((y - dy) / (abs(x - dx) + abs(y - dy) + 1e-12), dist(depot, i), -dem(i), i)

    customers = sorted(ids, key=key)

    # Initial split
    routes = []
    cur = []
    load = 0.0
    for c in customers:
        d = dem(c)
        if cur and load + d > capacity:
            routes.append(cur)
            cur = [c]
            load = d
        else:
            cur.append(c)
            load += d
    if cur:
        routes.append(cur)

    def rload(r):
        s = 0.0
        for c in r:
            s += dem(c)
        return s

    def rcost(r):
        if not r:
            return 0.0
        c = dist(depot, r[0])
        for a, b in zip(r, r[1:]):
            c += dist(a, b)
        c += dist(r[-1], depot)
        return c

    def two_opt(r):
        n = len(r)
        if n < 4:
            return r
        improved = True
        while improved:
            improved = False
            best = 0.0
            bi = bj = -1
            for i in range(n - 2):
                a = depot if i == 0 else r[i - 1]
                b = r[i]
                for j in range(i + 1, n - 1):
                    c = r[j]
                    d = depot if j == n - 1 else r[j + 1]
                    delta = (dist(a, c) + dist(b, d)) - (dist(a, b) + dist(c, d))
                    if delta < best:
                        best = delta
                        bi, bj = i, j
            if bi >= 0:
                r = r[:bi] + r[bi:bj + 1][::-1] + r[bj + 1:]
                n = len(r)
                improved = True
        return r

    def normalize_route(r):
        if len(r) <= 1:
            return r
        r1 = r[:]
        r2 = r[::-1]
        return r1 if rcost(r1) <= rcost(r2) else r2

    routes = [normalize_route(two_opt(r)) for r in routes if r]

    # Merge routes when beneficial and feasible
    changed = True
    while changed:
        changed = False
        best_gain = 1e-12
        best = None
        m = len(routes)
        for i in range(m):
            ri = routes[i]
            li = rload(ri)
            ci = rcost(ri)
            for j in range(i + 1, m):
                rj = routes[j]
                if li + rload(rj) > capacity:
                    continue
                cj = rcost(rj)
                variants = (
                    ri + rj,
                    ri + rj[::-1],
                    ri[::-1] + rj,
                    ri[::-1] + rj[::-1],
                )
                for cand in variants:
                    gain = ci + cj - rcost(cand)
                    if gain > best_gain:
                        best_gain = gain
                        best = (i, j, cand)
        if best is not None:
            i, j, cand = best
            nr = []
            for t, r in enumerate(routes):
                if t == i:
                    nr.append(normalize_route(two_opt(cand)))
                elif t != j:
                    nr.append(r)
            routes = nr
            changed = True

    # Inter-route relocate repair / improvement
    improved = True
    while improved:
        improved = False
        best_delta = 0.0
        action = None
        m = len(routes)
        for i in range(m):
            ri = routes[i]
            li = rload(ri)
            ci = rcost(ri)
            for pos in range(len(ri)):
                c = ri[pos]
                dc = dem(c)
                rem = ri[:pos] + ri[pos + 1:]
                cr = rcost(rem) if rem else 0.0
                for j in range(m):
                    if i == j:
                        continue
                    rj = routes[j]
                    lj = rload(rj)
                    if lj + dc > capacity:
                        continue
                    cj = rcost(rj)
                    # insert c in best position in rj
                    if not rj:
                        candj = [c]
                        delta = (cr + rcost(candj)) - (ci + cj)
                        if delta < best_delta:
                            best_delta = delta
                            action = (i, j, pos, 0, candj)
                        continue
                    best_ins = None
                    best_ins_delta = None
                    for ins in range(len(rj) + 1):
                        candj = rj[:ins] + [c] + rj[ins:]
                        d = rcost(candj) - cj
                        if best_ins_delta is None or d < best_ins_delta:
                            best_ins_delta = d
                            best_ins = ins
                    delta = (cr + (cj + best_ins_delta)) - (ci + cj)
                    if delta < best_delta:
                        best_delta = delta
                        action = (i, j, pos, best_ins, None)
        if action is not None:
            i, j, pos, ins, candj = action
            c = routes[i][pos]
            ri = routes[i][:pos] + routes[i][pos + 1:]
            if candj is None:
                rj = routes[j]
                candj = rj[:ins] + [c] + rj[ins:]
            else:
                rj = candj
            new_routes = []
            for t, r in enumerate(routes):
                if t == i:
                    if ri:
                        new_routes.append(normalize_route(two_opt(ri)))
                elif t == j:
                    new_routes.append(normalize_route(two_opt(candj)))
                else:
                    new_routes.append(r)
            routes = [r for r in new_routes if r]
            improved = True

    # Final ensure all customers exactly once; repair by fallback packing if needed
    seen = {}
    for r in routes:
        for c in r:
            seen[c] = seen.get(c, 0) + 1
    missing = [c for c in ids if seen.get(c, 0) == 0]
    if missing:
        flat = []
