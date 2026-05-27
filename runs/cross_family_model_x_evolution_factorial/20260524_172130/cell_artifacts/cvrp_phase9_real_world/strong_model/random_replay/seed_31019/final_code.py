def solve_cvrp(instance):
    def field(x, *names, default=None):
        for n in names:
            try:
                if x.__class__.__name__ == "dict" and n in x:
                    return x[n]
            except:
                pass
            try:
                d = x.__dict__
                if n in d:
                    return d[n]
            except:
                pass
        return default

    def seq(x):
        if x is None:
            return []
        if x.__class__.__name__ == "list" or x.__class__.__name__ == "tuple":
            return x
        try:
            return list(x)
        except:
            return [x]

    def is_dict(x):
        return x.__class__.__name__ == "dict"

    def is_pair(p):
        return (p.__class__.__name__ == "list" or p.__class__.__name__ == "tuple") and len(p) >= 2

    cap = field(instance, "capacity", "vehicle_capacity", "cap", default=10**18)
    depot = field(instance, "depot", "depot_id", default=0)
    if is_dict(depot):
        depot = depot.get("id", depot.get("node", depot.get("index", 0)))
    if depot.__class__.__name__ == "list" or depot.__class__.__name__ == "tuple":
        depot = depot[0] if depot else 0

    raw_dem = field(instance, "demands", "demand", default=None)
    raw_xy = field(instance, "coordinates", "coords", "locations", default=None)
    cust = field(instance, "customers", "customer_ids", default=None)

    dem = {}
    if raw_dem is not None:
        if is_dict(raw_dem):
            for k in raw_dem:
                dem[k] = raw_dem[k]
        else:
            a = seq(raw_dem)
            i = 0
            for v in a:
                dem[i] = v
                i += 1

    xy = None
    if raw_xy is not None:
        xy = {}
        if is_dict(raw_xy):
            for k in raw_xy:
                p = raw_xy[k]
                if is_pair(p):
                    xy[k] = (float(p[0]), float(p[1]))
        else:
            a = seq(raw_xy)
            i = 0
            for p in a:
                if is_pair(p):
                    xy[i] = (float(p[0]), float(p[1]))
                i += 1

    if cust is None:
        customers = []
        for k in dem:
            if k != depot:
                customers.append(k)
    else:
        customers = []
        for c in seq(cust):
            if c != depot:
                customers.append(c)

    for c in customers:
        if c not in dem:
            dem[c] = 0

    if not customers:
        return []

    if xy is None:
        customers = sorted(customers)
        routes = []
        cur = []
        load = 0
        for c in customers:
            d = dem.get(c, 0)
            if cur and load + d > cap:
                routes.append(cur)
                cur = [c]
                load = d
            else:
                cur.append(c)
                load += d
        if cur:
            routes.append(cur)
        return routes

    if depot not in xy:
        xy[depot] = (0.0, 0.0)
    dx0, dy0 = xy[depot]

    def dist(a, b):
        pa = xy.get(a)
        pb = xy.get(b)
        if pa is None or pb is None:
            return 0.0
        dx = pa[0] - pb[0]
        dy = pa[1] - pb[1]
        return (dx * dx + dy * dy) ** 0.5

    def ang(c):
        x, y = xy.get(c, (0.0, 0.0))
        return (y - dy0, x - dx0)

    customers = sorted(customers, key=lambda c: (ang(c)[0] / (abs(ang(c)[0]) + abs(ang(c)[1]) + 1e-12), dist(depot, c), c))
    routes = []
    cur = []
    load = 0
    for c in customers:
        d = dem.get(c, 0)
        if d > cap:
            if cur:
                routes.append(cur)
                cur = []
                load = 0
            routes.append([c])
            continue
        if cur and load + d > cap:
            routes.append(cur)
            cur = [c]
            load = d
        else:
            cur.append(c)
            load += d
    if cur:
        routes.append(cur)

    def rload(r):
        s = 0
        for c in r:
            s += dem.get(c, 0)
        return s

    def rcost(r):
        if not r:
            return 0.0
        s = dist(depot, r[0]) + dist(r[-1], depot)
        i = 0
        while i + 1 < len(r):
            s += dist(r[i], r[i + 1])
            i += 1
        return s

    # remove duplicates, keep first occurrence
    seen = {}
    cleaned = []
    for r in routes:
        nr = []
        for c in r:
            if c not in seen:
                seen[c] = 1
                nr.append(c)
        if nr:
            cleaned.append(nr)
    routes = cleaned

    # add missing
    for c in customers:
        if c not in seen:
            placed = False
            for r in routes:
                if rload(r) + dem.get(c, 0) <= cap:
                    r.append(c)
                    placed = True
                    break
            if not placed:
                routes.append([c])

    # simple merge improvement
    improved = True
    while improved:
        improved = False
        best = None
        best_gain = 0.0
        n = len(routes)
        i = 0
        while i < n:
            j = i + 1
            while j < n:
                if rload(routes[i]) + rload(routes[j]) <= cap:
                    base = rcost(routes[i]) + rcost(routes[j])
                    cand1 = routes[i] + routes[j]
                    cand2 = routes[i] + routes[j][::-1]
                    cand3 = routes[i][::-1] + routes[j]
                    cand4 = routes[i][::-1] + routes[j][::-1]
                    for m in (cand1, cand2, cand3, cand4):
                        g = base - rcost(m)
                        if g > best_gain + 1e-12:
                            best_gain = g
                            best = (i, j, m)
                j += 1
            i += 1
        if best is not None:
            i, j, m = best
            nr = []
            k = 0
            while k < len(routes):
                if k == i:
                    nr.append(m)
                elif k != j:
                    nr.append(routes[k])
                k += 1
            routes = nr
            improved = True

    final = []
    seen2 = {}
    for r in routes:
        nr = []
        load = 0
        for c in r:
            if c not in seen2:
                seen2[c] = 1
                nr.append(c)
                load += dem.get(c, 0)
        if nr:
            if load <= cap:
                final.append(nr)
            else:
                buf = []
                bl = 0
                for c in nr:
                    d = dem.get(c, 0)
                    if buf and bl + d > cap:
                        final.append(buf)
                        buf = [c]
                        bl = d
                    else:
                        buf.append(c)
                        bl += d
                if buf:
                    final.append(buf)

    for c in customers:
        if c not in seen2:
            d = dem.get(c, 0)
            placed = False
            for r in final:
                if rload(r) + d <= cap:
                    r.append(c)
                    placed = True
                    break
            if not placed:
                final.append([c])

    return final
