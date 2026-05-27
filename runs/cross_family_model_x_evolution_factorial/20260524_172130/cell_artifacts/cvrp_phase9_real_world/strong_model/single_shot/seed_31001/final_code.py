def solve_cvrp(instance):
    def g(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        try:
            return obj.__dict__.get(key, default)
        except Exception:
            return default

    cap = g(instance, "capacity", g(instance, "vehicle_capacity", g(instance, "Q", g(instance, "cap", None))))
    depot = g(instance, "depot", 0)
    if isinstance(depot, dict):
        depot_id = depot.get("id", depot.get("idx", 0))
    else:
        depot_id = depot

    demands = g(instance, "demands", None)
    coords = g(instance, "coords", g(instance, "coordinates", None))
    dm = g(instance, "distance_matrix", g(instance, "dist_matrix", None))
    customers = g(instance, "customers", None)
    if customers is None:
        if isinstance(demands, dict):
            customers = [k for k in demands if k != depot_id]
        elif isinstance(coords, dict):
            customers = [k for k in coords if k != depot_id]
        elif dm is not None:
            customers = [i for i in range(len(dm)) if i != depot_id]
        else:
            n = g(instance, "n", g(instance, "size", 0))
            customers = [i for i in range(n) if i != depot_id]
    customers = sorted(customers)

    if cap is None:
        s = 0
        for c in customers:
            if isinstance(demands, dict):
                s += demands.get(c, 1)
            elif isinstance(demands, list) and c < len(demands):
                s += demands[c]
            else:
                s += 1
        cap = max(1, s)

    def dem(i):
        if demands is None:
            return 1
        if isinstance(demands, dict):
            return demands.get(i, 0)
        return demands[i] if i < len(demands) else 0

    def xy(i):
        if coords is None:
            return None
        v = coords.get(i) if isinstance(coords, dict) else (coords[i] if i < len(coords) else None)
        if v is None:
            return None
        if isinstance(v, dict):
            return (v.get("x", 0.0), v.get("y", 0.0))
        return (v[0], v[1])

    def dist(i, j):
        if dm is not None:
            return dm[i][j]
        a, b = xy(i), xy(j)
        if a is None or b is None:
            return 0.0
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    def load(r):
        s = 0
        for c in r:
            s += dem(c)
        return s

    def cost(r):
        if not r:
            return 0.0
        c = dist(depot_id, r[0])
        for i in range(len(r) - 1):
            c += dist(r[i], r[i + 1])
        return c + dist(r[-1], depot_id)

    routes = [[c] for c in customers]
    owner = {c: i for i, c in enumerate(customers)}
    active = [True] * len(routes)

    sv = []
    for i in range(len(customers)):
        a = customers[i]
        for j in range(i + 1, len(customers)):
            b = customers[j]
            sv.append((-(dist(depot_id, a) + dist(depot_id, b) - dist(a, b)), a, b))
    sv.sort()

    def rebuild():
        owner.clear()
        for k, r in enumerate(routes):
            if active[k]:
                for c in r:
                    owner[c] = k

    for _, a, b in sv:
        ra = owner.get(a)
        rb = owner.get(b)
        if ra is None or rb is None or ra == rb or not active[ra] or not active[rb]:
            continue
        r1, r2 = routes[ra], routes[rb]
        if load(r1) + load(r2) > cap:
            continue
        if r1[-1] == a and r2[0] == b:
            nr = r1 + r2
        elif r1[0] == a and r2[-1] == b:
            nr = r2 + r1
        elif r1[0] == a and r2[0] == b:
            nr = list(reversed(r1)) + r2
        elif r1[-1] == a and r2[-1] == b:
            nr = r1 + list(reversed(r2))
        else:
            continue
        routes[ra] = nr
        active[rb] = False
        rebuild()

    routes = [r for i, r in enumerate(routes) if active[i] and r]

    def orient(r):
        rr = list(reversed(r))
        return rr if cost(rr) < cost(r) else r[:]

    routes = [orient(r) for r in routes]

    seen = set()
    fixed = []
    for r in routes:
        cur = []
        l = 0
        for c in r:
            if c in seen:
                continue
            d = dem(c)
            if d > cap:
                if cur:
                    fixed.append(cur)
                    cur = []
                    l = 0
                fixed.append([c])
                seen.add(c)
                continue
            if l + d > cap and cur:
                fixed.append(cur)
                cur = [c]
                l = d
            else:
                cur.append(c)
                l += d
            seen.add(c)
        if cur:
            fixed.append(cur)
    for c in customers:
        if c not in seen:
            fixed.append([c])
    routes = fixed

    def rem_delta(r, p):
        c = r[p]
        a = depot_id if p == 0 else r[p - 1]
        b = depot_id if p == len(r) - 1 else r[p + 1]
        return -dist(a, c) - dist(c, b) + dist(a, b)

    def ins_delta(r, p, c):
        a = depot_id if p == 0 else r[p - 1]
        b = depot_id if p == len(r) else r[p]
        return -dist(a, b) + dist(a, c) + dist(c, b)

    improved = True
    while improved:
        improved = False
        best = None
        best_gain = 0.0
        for i in range(len(routes)):
            ri = routes[i]
            li = load(ri)
            for p in range(len(ri)):
                a = ri[p]
                da = dem(a)
                rd = rem_delta(ri, p)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    if load(rj) + da > cap:
                        continue
                    for q in range(len(rj) + 1):
                        gain = rd + ins_delta(rj, q, a)
                        if gain > best_gain + 1e-12:
                            best_gain = gain
                            best = (i, p, j, q)
        if best is not None:
            i, p, j, q = best
            a = routes[i][p]
            r1 = routes[i][:]
            r2 = routes[j][:]
            del r1[p]
            r2.insert(q, a)
            routes[i] = r1
            routes[j] = r2
            routes = [r for r in routes if r]
            improved = True
            continue

        best = None
        best_gain = 0.0
        for i in range(len(routes)):
            ri = routes[i]
            li = load(ri)
            for j in range(i + 1, len(routes)):
                rj = routes[j]
                lj = load(rj)
                for p in range(len(ri)):
                    a = ri[p]
                    da = dem(a)
                    for q in range(len(rj)):
                        b = rj[q]
                        db = dem(b)
                        if li - da + db > cap or lj - db + da > cap:
                            continue
                        nri = ri[:p] + [b] + ri[p + 1:]
                        nrj = rj[:q] + [a] + rj[q + 1:]
                        gain = cost(ri) + cost(rj) - cost(nri) - cost(nrj)
                        if gain > best_gain + 1e-12:
                            best_gain = gain
                            best = (i, p, j, q)
        if best is not None:
            i, p, j, q = best
            a = routes[i][p]
            b = routes[j][q]
            ri = routes[i][:]
            rj = routes[j][:]
            ri[p] = b
            rj[q] = a
            routes[i] = ri
            routes[j] = rj
            improved = True

    routes = [orient(r) for r in routes if r]
    seen = set()
    out = []
    for r in routes:
        nr = []
        for c in r:
            if c not in seen:
                seen.add(c)
                nr.append(c)
        if nr:
            out.append(nr)
    for c in customers:
        if c not in seen:
            out.append([c])
    return out
