def solve_cvrp(instance):
    def gv(o, *names, default=None):
        if isinstance(o, dict):
            for n in names:
                if n in o:
                    return o[n]
        for n in names:
            try:
                return o[n]
            except Exception:
                pass
            try:
                return o.__dict__[n]
            except Exception:
                pass
        return default

    def num(x, d=0.0):
        try:
            return float(x)
        except Exception:
            try:
                return float(int(x))
            except Exception:
                return d

    def cid(x, d=None):
        try:
            return int(x)
        except Exception:
            return x if d is None else d

    def xy(v):
        if isinstance(v, dict):
            if "coord" in v:
                a = v["coord"]
                return (num(a[0]), num(a[1]))
            if "coords" in v:
                a = v["coords"]
                return (num(a[0]), num(a[1]))
            if "x" in v and "y" in v:
                return (num(v["x"]), num(v["y"]))
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (num(v[0]), num(v[1]))
        return (0.0, 0.0)

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    data = gv(instance, "customers", "nodes", "points", "locations", default=None)
    depot = gv(instance, "depot", "depot_id", default=None)
    cap = gv(instance, "capacity", "vehicle_capacity", "cap", default=None)

    coords, dem = {}, {}
    if isinstance(data, dict):
        for k, v in data.items():
            i = cid(k)
            coords[i] = xy(v)
            dem[i] = int(num(gv(v, "demand", default=1), 1))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            j = cid(gv(v, "id", "customer_id", default=i), i) if isinstance(v, dict) else i
            coords[j] = xy(v)
            dem[j] = int(num(gv(v, "demand", default=1), 1)) if isinstance(v, dict) else 1

    if not coords:
        return []

    depot_xy = (0.0, 0.0)
    depot_id = None
    if isinstance(depot, dict):
        depot_xy = xy(depot)
        depot_id = cid(gv(depot, "id", "depot_id", default=None), None)
        if depot_id is not None:
            coords[depot_id] = depot_xy
    elif isinstance(depot, int) and depot in coords:
        depot_id = depot
        depot_xy = coords[depot]
    elif isinstance(depot, (list, tuple)) and len(depot) >= 2:
        depot_xy = xy(depot)

    customers = [i for i in sorted(coords) if i != depot_id]
    if cap is None or int(num(cap, 0)) <= 0:
        cap = max(1, max((dem.get(i, 1) for i in customers), default=1))
    cap = int(num(cap, 1))

    routes, unserved = [], customers[:]
    while unserved:
        r, load, cur = [], 0, depot_xy
        while True:
            best = None
            bk = None
            for c in unserved:
                d = dem.get(c, 1)
                if load + d > cap:
                    continue
                k = (dist(cur, coords[c]), d, c)
                if bk is None or k < bk:
                    best, bk = c, k
            if best is None:
                break
            r.append(best)
            load += dem.get(best, 1)
            cur = coords[best]
            unserved.remove(best)
        if not r:
            r = [unserved.pop(0)]
        routes.append(r)

    def load(r):
        s = 0
        for c in r:
            s += dem.get(c, 1)
        return s

    def rcost(r):
        if not r:
            return 0.0
        c = dist(depot_xy, coords[r[0]])
        for i in range(len(r) - 1):
            c += dist(coords[r[i]], coords[r[i + 1]])
        return c + dist(coords[r[-1]], depot_xy)

    def total(rs):
        s = 0.0
        for r in rs:
            s += rcost(r)
        return s

    def two_opt(r):
        if len(r) < 4:
            return r[:]
        best = r[:]
        bc = rcost(best)
        improved = True
        while improved:
            improved = False
            n = len(best)
            for i in range(n - 2):
                for j in range(i + 2, n):
                    cand = best[:i + 1] + best[i + 1:j + 1][::-1] + best[j + 1:]
                    c = rcost(cand)
                    if c + 1e-12 < bc:
                        best, bc, improved = cand, c, True
                        break
                if improved:
                    break
        return best

    routes = [two_opt(r) for r in routes]

    changed = True
    while changed:
        changed = False
        base = total(routes)
        for i in range(len(routes)):
            for p in range(len(routes[i])):
                c = routes[i][p]
                for j in range(len(routes)):
                    for ins in range(len(routes[j]) + 1):
                        if i == j and (ins == p or ins == p + 1):
                            continue
                        if i == j:
                            cand = [x[:] for x in routes]
                            rr = cand[i]
                            v = rr.pop(p)
                            if ins > p:
                                ins -= 1
                            rr.insert(ins, v)
                        else:
                            cand = [x[:] for x in routes]
                            a, b = cand[i], cand[j]
                            if load(a) - dem.get(c, 1) > cap or load(b) + dem.get(c, 1) > cap:
                                continue
                            v = a.pop(p)
                            b.insert(ins, v)
                        if total(cand) + 1e-12 < base:
                            routes, changed = cand, True
                            break
                    if changed:
                        break
                if changed:
                    break
            if changed:
                break

    seen = {}
    for r in routes:
        for c in r:
            seen[c] = seen.get(c, 0) + 1
    missing = [c for c in customers if seen.get(c, 0) == 0]

    if missing:
        nr = []
        used = {}
        for r in routes:
            t = []
            for c in r:
                if not used.get(c, 0):
                    t.append(c)
                    used[c] = 1
            if t:
                nr.append(t)
        routes = nr
        for c in missing:
            d = dem.get(c, 1)
            best = None
            bp = None
            bd = None
            for i, r in enumerate(routes):
                if load(r) + d > cap:
                    continue
                for p in range(len(r) + 1):
                    a = depot_xy if p == 0 else coords[r[p - 1]]
                    b = depot_xy if p == len(r) else coords[r[p]]
                    delta = dist(a, coords[c]) + dist(coords[c], b) - dist(a, b)
                    k = (delta, i, p)
                    if bd is None or k < bd:
                        best, bp, bd = i, p, k
            if best is None:
                routes.append([c])
            else:
                routes[best].insert(bp, c)

    routes = [[c for c in r if c != depot_id and c in coords] for r in routes]
    return [r for r in routes if r]
