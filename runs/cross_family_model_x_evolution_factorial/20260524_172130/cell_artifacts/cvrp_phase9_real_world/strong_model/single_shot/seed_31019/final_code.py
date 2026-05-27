def solve_cvrp(instance):
    def read(obj, names, default=None):
        if isinstance(obj, dict):
            for n in names:
                if n in obj:
                    return obj[n]
            return default
        for n in names:
            try:
                return object.__getattribute__(obj, n)
            except Exception:
                pass
        return default

    def coords_of(x):
        if isinstance(x, (list, tuple)) and len(x) >= 2:
            return x[0], x[1]
        if isinstance(x, dict):
            if 0 in x and 1 in x:
                return x[0], x[1]
            if "x" in x and "y" in x:
                return x["x"], x["y"]
        return None

    depot = read(instance, ["depot", "depot_id", "start", "origin"], 0)
    dm = read(instance, ["distance_matrix", "distances", "distance"], None)
    coords = read(instance, ["coords", "coordinates", "locations", "points"], None)
    cap = read(instance, ["capacity", "vehicle_capacity", "cap"], None)
    dem = read(instance, ["demands", "demand"], None)

    customers = read(instance, ["customer_ids", "customers", "nodes"], None)
    if customers is None:
        n = read(instance, ["n", "num_customers", "size"], None)
        if isinstance(n, int):
            customers = [i for i in range(n + 1) if i != depot]
        elif isinstance(dem, dict):
            customers = [k for k in dem.keys() if k != depot]
        elif isinstance(dem, (list, tuple)):
            customers = [i for i in range(len(dem)) if i != depot]
        else:
            customers = []
    else:
        customers = [c for c in customers if c != depot]

    demand = {}
    if isinstance(dem, dict):
        for c in customers:
            v = dem.get(c, dem.get(str(c), 0))
            demand[c] = 0 if v is None else v
    elif isinstance(dem, (list, tuple)):
        for c in customers:
            if isinstance(c, int) and 0 <= c < len(dem):
                demand[c] = dem[c]
            elif isinstance(c, int) and 1 <= c <= len(dem):
                demand[c] = dem[c - 1]
            else:
                demand[c] = 0
    else:
        for c in customers:
            demand[c] = 0

    coord_map = None
    if isinstance(coords, dict):
        coord_map = coords
    elif isinstance(coords, (list, tuple)):
        coord_map = {i: coords[i] for i in range(len(coords))}

    def dist(a, b):
        if a == b:
            return 0.0
        if dm is not None:
            try:
                return dm[a][b]
            except Exception:
                try:
                    return dm[b][a]
                except Exception:
                    pass
        if coord_map is not None and a in coord_map and b in coord_map:
            pa = coords_of(coord_map[a])
            pb = coords_of(coord_map[b])
            if pa and pb:
                dx = pa[0] - pb[0]
                dy = pa[1] - pb[1]
                return (dx * dx + dy * dy) ** 0.5
        return abs(a - b)

    ordered = list(customers)
    if coord_map is not None and depot in coord_map:
        dp = coords_of(coord_map[depot])
        if dp:
            def key(c):
                p = coords_of(coord_map[c])
                if not p:
                    return (2, 0, 0, c)
                dx = p[0] - dp[0]
                dy = p[1] - dp[1]
                half = 0 if (dy > 0 or (dy == 0 and dx >= 0)) else 1
                slope = dy / dx if dx != 0 else (10**18 if dy >= 0 else -10**18)
                r2 = dx * dx + dy * dy
                return (half, slope, r2, c)
            ordered.sort(key=key)
    else:
        ordered.sort(key=lambda c: (-demand.get(c, 0), c))

    unvisited = set(customers)
    routes = []

    while unvisited:
        start = None
        best = None
        for c in ordered:
            if c not in unvisited:
                continue
            k = (dist(depot, c), demand.get(c, 0), -c)
            if best is None or k > best:
                best = k
                start = c
        if start is None:
            break
        route = [start]
        unvisited.remove(start)
        load = demand.get(start, 0)
        while True:
            nxt = None
            best = None
            last = route[-1]
            for c in ordered:
                if c not in unvisited:
                    continue
                d = demand.get(c, 0)
                if cap is not None and load + d > cap:
                    continue
                k = (dist(last, c), dist(depot, c), d, c)
                if best is None or k < best:
                    best = k
                    nxt = c
            if nxt is None:
                break
            route.append(nxt)
            unvisited.remove(nxt)
            load += demand.get(nxt, 0)
        routes.append(route)

    def load_of(r):
        s = 0
        for x in r:
            s += demand.get(x, 0)
        return s

    if unvisited:
        for c in sorted(unvisited):
            placed = False
            for r in routes:
                if cap is not None and load_of(r) + demand.get(c, 0) > cap:
                    continue
                best_pos = 0
                best_delta = None
                for i in range(len(r) + 1):
                    a = depot if i == 0 else r[i - 1]
                    b = depot if i == len(r) else r[i]
                    delta = dist(a, c) + dist(c, b) - dist(a, b)
                    if best_delta is None or delta < best_delta:
                        best_delta = delta
                        best_pos = i
                r.insert(best_pos, c)
                placed = True
                break
            if not placed:
                routes.append([c])

    def route_cost(r):
        if not r:
            return 0.0
        s = dist(depot, r[0])
        for i in range(len(r) - 1):
            s += dist(r[i], r[i + 1])
        s += dist(r[-1], depot)
        return s

    improved = True
    while improved:
        improved = False
        for r in routes:
            n = len(r)
            if n < 4:
                continue
            base = route_cost(r)
            best_gain = 0.0
            best_i = best_j = None
            for i in range(n - 2):
                for j in range(i + 2, n):
                    nr = r[:i + 1] + r[i + 1:j + 1][::-1] + r[j + 1:]
                    gain = base - route_cost(nr)
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best_i, best_j = i, j
            if best_i is not None:
                r[:] = r[:best_i + 1] + r[best_i + 1:best_j + 1][::-1] + r[best_j + 1:]
                improved = True
        for a in range(len(routes)):
            if improved:
                break
            ra = routes[a]
            for i, x in enumerate(list(ra)):
                dx = demand.get(x, 0)
                rem_prev = depot if i == 0 else ra[i - 1]
                rem_next = depot if i == len(ra) - 1 else ra[i + 1]
                rem_delta = dist(rem_prev, x) + dist(x, rem_next) - dist(rem_prev, rem_next)
                for b in range(len(routes)):
                    if a == b:
                        continue
                    rb = routes[b]
                    if cap is not None and load_of(rb) + dx > cap:
                        continue
                    best_pos = 0
                    best_ins = None
                    for pos in range(len(rb) + 1):
                        p = depot if pos == 0 else rb[pos - 1]
                        q = depot if pos == len(rb) else rb[pos]
                        ins = dist(p, x) + dist(x, q) - dist(p, q)
                        if best_ins is None or ins < best_ins:
                            best_ins = ins
                            best_pos = pos
                    if best_ins is not None and best_ins + rem_delta < -1e-12:
                        rb.insert(best_pos, x)
                        del ra[i]
                        improved = True
                        break
                if improved:
                    break
        routes = [r for r in routes if r]

    seen = set()
    out = []
    for r in routes:
        nr = []
        for x in r:
            if x not in seen:
                seen.add(x)
                nr.append(x)
        if nr:
            out.append(nr)

    missing = [c for c in customers if c not in seen]
    for c in missing:
        placed = False
        for r in out:
            if cap is not None and load_of(r) + demand.get(c, 0) > cap:
                continue
            best_pos = 0
            best_delta = None
            for i in range(len(r) + 1):
                a = depot if i == 0 else r[i - 1]
                b = depot if i == len(r) else r[i]
                delta = dist(a, c) + dist(c, b) - dist(a, b)
                if best_delta is None or delta < best_delta:
                    best_delta = delta
                    best_pos = i
            r.insert(best_pos, c)
            placed = True
            break
        if not placed:
            out.append([c])

    return [r for r in out if r]
