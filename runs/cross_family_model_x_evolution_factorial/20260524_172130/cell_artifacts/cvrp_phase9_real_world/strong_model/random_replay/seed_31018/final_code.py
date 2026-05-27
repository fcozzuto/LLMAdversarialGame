def solve_cvrp(instance):
    def getv(obj, key, default=None):
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
        except:
            pass
        try:
            return obj[key]
        except:
            pass
        try:
            d = vars(obj)
            if key in d:
                return d[key]
        except:
            pass
        return default

    depot = getv(instance, "depot", 0)
    cap = getv(instance, "capacity", None)
    if cap is None:
        cap = getv(instance, "vehicle_capacity", getv(instance, "cap", 0))

    demands = getv(instance, "demands", getv(instance, "demand", {}))
    dist = getv(instance, "distance_matrix", None)
    coords = getv(instance, "coords", getv(instance, "points", None))

    def dem(i):
        try:
            if isinstance(demands, dict):
                return demands.get(i, 0)
        except:
            pass
        try:
            return demands[i]
        except:
            return 0

    def coord(i):
        try:
            if isinstance(coords, dict):
                return coords.get(i, None)
        except:
            pass
        try:
            return coords[i]
        except:
            return None

    def d(i, j):
        if dist is not None:
            try:
                return dist[i][j]
            except:
                try:
                    return dist[i, j]
                except:
                    pass
        a = coord(i)
        b = coord(j)
        if a is None or b is None:
            return 0.0
        x = a[0] - b[0]
        y = a[1] - b[1]
        return (x * x + y * y) ** 0.5

    customers = getv(instance, "customers", None)
    if customers is None:
        n = getv(instance, "n", getv(instance, "num_customers", getv(instance, "size", None)))
        if n is None:
            if dist is not None:
                try:
                    n = len(dist) - 1
                except:
                    n = 0
            elif coords is not None:
                try:
                    n = len(coords) - 1
                except:
                    n = 0
            else:
                try:
                    n = len(demands) - 1
                except:
                    n = 0
        customers = [i for i in range(1, int(n) + 1)]
    else:
        customers = [c for c in customers if c != depot]

    if not customers:
        return []

    def load(route):
        s = 0
        for c in route:
            s += dem(c)
        return s

    def cost(route):
        if not route:
            return 0.0
        t = d(depot, route[0])
        for a, b in zip(route, route[1:]):
            t += d(a, b)
        return t + d(route[-1], depot)

    def ins_cost(route, pos, c):
        a = depot if pos == 0 else route[pos - 1]
        b = depot if pos == len(route) else route[pos]
        return d(a, c) + d(c, b) - d(a, b)

    def route_nodes():
        if coords is not None:
            dep = coord(depot)
            if dep is not None:
                x0, y0 = dep[0], dep[1]

                def keyf(c):
                    p = coord(c)
                    if p is None:
                        return (2, 0.0, -dem(c), c)
                    dx = p[0] - x0
                    dy = p[1] - y0
                    sector = 0 if dx >= 0 else 1
                    return (sector, dy / (abs(dx) + abs(dy) + 1e-12), -dem(c), c)

                return sorted(customers, key=keyf)
        return sorted(customers, key=lambda c: (-dem(c), d(depot, c), c))

    order = route_nodes()
    routes = []
    for c in order:
        best = None
        bestm = None
        dc = dem(c)
        for ri, r in enumerate(routes):
            if load(r) + dc > cap:
                continue
            for pos in range(len(r) + 1):
                m = (ins_cost(r, pos, c), len(r), ri, pos)
                if bestm is None or m < bestm:
                    bestm = m
                    best = (ri, pos)
        if best is None:
            routes.append([c])
        else:
            routes[best[0]].insert(best[1], c)

    seen = {}
    for r in routes:
        for c in r:
            seen[c] = seen.get(c, 0) + 1

    missing = [c for c in customers if seen.get(c, 0) == 0]
    if missing:
        for c in sorted(missing, key=lambda x: (-dem(x), x)):
            best = None
            bestm = None
            for ri, r in enumerate(routes):
                if load(r) + dem(c) > cap:
                    continue
                for pos in range(len(r) + 1):
                    m = (ins_cost(r, pos, c), len(r), ri, pos)
                    if bestm is None or m < bestm:
                        bestm = m
                        best = (ri, pos)
            if best is None:
                routes.append([c])
            else:
                routes[best[0]].insert(best[1], c)

    seen = {}
    cleaned = []
    for r in routes:
        nr = []
        for c in r:
            if seen.get(c, 0) == 0:
                nr.append(c)
                seen[c] = 1
        if nr:
            cleaned.append(nr)
    routes = cleaned

    missing = [c for c in customers if seen.get(c, 0) == 0]
    for c in sorted(missing, key=lambda x: (-dem(x), x)):
        best = None
        bestm = None
        for ri, r in enumerate(routes):
            if load(r) + dem(c) > cap:
                continue
            for pos in range(len(r) + 1):
                m = (ins_cost(r, pos, c), len(r), ri, pos)
                if bestm is None or m < bestm:
                    bestm = m
                    best = (ri, pos)
        if best is None:
            routes.append([c])
        else:
            routes[best[0]].insert(best[1], c)

    def two_opt(route):
        n = len(route)
        base = cost(route)
        best_route = route
        best_cost = base
        for i in range(n - 1):
            for j in range(i + 1, n):
                cand = route[:i] + route[i:j + 1][::-1] + route[j + 1:]
                cc = cost(cand)
                if cc + 1e-12 < best_cost:
                    best_cost = cc
                    best_route = cand
        return best_route, best_cost + 1e-12 < base

    def relocate(routes):
        for i in range(len(routes)):
            for a in range(len(routes[i])):
                c = routes[i][a]
                dc = dem(c)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    if load(routes[j]) + dc > cap:
                        continue
                    base = cost(routes[i]) + cost(routes[j])
                    ri = routes[i][:a] + routes[i][a + 1:]
                    for pos in range(len(routes[j]) + 1):
                        rj = routes[j][:pos] + [c] + routes[j][pos:]
                        if load(ri) <= cap and load(rj) <= cap:
                            nc = cost(ri) + cost(rj)
                            if nc + 1e-12 < base:
                                routes[i] = ri
                                routes[j] = rj
                                return True
        return False

    def swap(routes):
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                li = load(routes[i])
                lj = load(routes[j])
                for a in range(len(routes[i])):
                    ca = routes[i][a]
                    da = dem(ca)
                    for b in range(len(routes[j])):
                        cb = routes[j][b]
                        db = dem(cb)
                        if li - da + db > cap or lj - db + da > cap:
                            continue
                        base = cost(routes[i]) + cost(routes[j])
                        ri = routes[i][:a] + [cb] + routes[i][a + 1:]
                        rj = routes[j][:b] + [ca] + routes[j][b + 1:]
                        nc = cost(ri) + cost(rj)
                        if nc + 1e-12 < base:
                            routes[i] = ri
                            routes[j] = rj
                            return True
        return False

    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            nr, ok = two_opt(routes[i])
            if ok:
                routes[i] = nr
                improved = True
        if improved:
            continue
        if relocate(routes):
            improved = True
            continue
        if swap(routes):
            improved = True
            continue

    return [r for r in routes if r]
