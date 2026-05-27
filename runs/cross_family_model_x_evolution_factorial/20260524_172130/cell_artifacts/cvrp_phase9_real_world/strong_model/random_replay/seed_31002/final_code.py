def solve_cvrp(instance):
    def gv(obj, keys, default=None):
        if isinstance(keys, str):
            keys = (keys,)
        for k in keys:
            if isinstance(obj, dict) and k in obj:
                return obj[k]
            try:
                return obj[k]
            except Exception:
                pass
            try:
                if hasattr(obj, k):
                    return obj[k]
            except Exception:
                pass
        return default

    def as_list(x):
        if x is None:
            return None
        if isinstance(x, list):
            return x
        try:
            return list(x)
        except Exception:
            return None

    capacity = gv(instance, ("capacity", "vehicle_capacity", "cap"), 0)
    try:
        capacity = int(capacity)
    except Exception:
        try:
            capacity = float(capacity)
        except Exception:
            capacity = 0

    depot = gv(instance, ("depot", "depot_id"), 0)
    try:
        depot = int(depot)
    except Exception:
        pass

    dist_m = gv(instance, ("distance_matrix", "distances", "distance"), None)
    coords = gv(instance, ("coords", "coordinates", "locations"), None)
    demands = gv(instance, ("demands", "demand"), None)

    customers = gv(instance, "customers", None)
    if customers is None:
        n = gv(instance, ("n", "num_nodes", "size"), None)
        if n is not None:
            try:
                customers = [i for i in range(int(n)) if i != depot]
            except Exception:
                customers = []
        elif demands is not None and hasattr(demands, "__len__"):
            customers = [i for i in range(len(demands)) if i != depot]
        elif coords is not None and hasattr(coords, "keys"):
            customers = [i for i in coords.keys() if i != depot]
        else:
            customers = []
    customers = as_list(customers) or []

    seen = set()
    cust = []
    for c in customers:
        try:
            c = int(c)
        except Exception:
            pass
        if c != depot and c not in seen:
            seen.add(c)
            cust.append(c)

    def dem(i):
        if demands is None:
            return 0
        try:
            return demands[i]
        except Exception:
            try:
                return demands[int(i)]
            except Exception:
                return 0

    def coord(i):
        if coords is None:
            return None
        try:
            return coords[i]
        except Exception:
            try:
                return coords[int(i)]
            except Exception:
                return None

    def dist(a, b):
        if a == b:
            return 0.0
        if dist_m is not None:
            try:
                return float(dist_m[a][b])
            except Exception:
                try:
                    return float(dist_m[int(a)][int(b)])
                except Exception:
                    pass
        pa = coord(a)
        pb = coord(b)
        if pa is not None and pb is not None and len(pa) >= 2 and len(pb) >= 2:
            dx = pa[0] - pb[0]
            dy = pa[1] - pb[1]
            return (dx * dx + dy * dy) ** 0.5
        return 0.0

    def load(r):
        s = 0
        for x in r:
            s += dem(x)
        return s

    def cost(r):
        if not r:
            return 0.0
        t = dist(depot, r[0])
        for i in range(len(r) - 1):
            t += dist(r[i], r[i + 1])
        return t + dist(r[-1], depot)

    def insert_pos(r, x):
        best_i, best_d = 0, None
        for i in range(len(r) + 1):
            a = depot if i == 0 else r[i - 1]
            b = depot if i == len(r) else r[i]
            d = dist(a, x) + dist(x, b) - dist(a, b)
            if best_d is None or d < best_d or (d == best_d and i < best_i):
                best_d, best_i = d, i
        return best_i, best_d

    cdep = coord(depot)
    ordered = []
    if cdep is not None and len(cdep) >= 2:
        for c in cust:
            p = coord(c)
            if p is not None and len(p) >= 2:
                dx = p[0] - cdep[0]
                dy = p[1] - cdep[1]
                ang = 0.0
                if dx >= 0 and dy >= 0:
                    ang = dy / (abs(dx) + abs(dy) + 1e-12)
                elif dx < 0 <= dy:
                    ang = 1.0 + abs(dx) / (abs(dx) + abs(dy) + 1e-12)
                elif dx < 0 and dy < 0:
                    ang = 2.0 + abs(dy) / (abs(dx) + abs(dy) + 1e-12)
                else:
                    ang = 3.0 + abs(dx) / (abs(dx) + abs(dy) + 1e-12)
                ordered.append((ang, dist(depot, c), c))
            else:
                ordered.append((9.0, dist(depot, c), c))
        ordered.sort()
        ordered = [x[2] for x in ordered]
    else:
        ordered = sorted(cust, key=lambda x: (-dem(x), x))

    routes, cur, cl = [], [], 0
    for c in ordered:
        d = dem(c)
        if cur and capacity > 0 and cl + d > capacity:
            routes.append(cur)
            cur, cl = [c], d
        else:
            cur.append(c)
            cl += d
    if cur:
        routes.append(cur)

    routes = [r for r in routes if r]

    improved = True
    limit = 50
    while improved and limit > 0:
        improved = False
        limit -= 1

        i = 0
        while i < len(routes) and not improved:
            r = routes[i]
            j = 0
            while j < len(r) and not improved:
                x = r[j]
                dx = dem(x)
                rr = r[:j] + r[j + 1:]
                oldr = cost(r)
                newr = cost(rr)
                k = 0
                while k < len(routes) and not improved:
                    if k != i and (capacity <= 0 or load(routes[k]) + dx <= capacity):
                        pos, add = insert_pos(routes[k], x)
                        if newr + cost(routes[k]) + add + 1e-12 < oldr + cost(routes[k]):
                            routes[i] = rr
                            routes[k] = routes[k][:pos] + [x] + routes[k][pos:]
                            if not routes[i]:
                                routes.pop(i)
                            improved = True
                    k += 1
                j += 1
            i += 1

        i = 0
        while i < len(routes) and not improved:
            j = i + 1
            while j < len(routes) and not improved:
                ri, rj = routes[i], routes[j]
                li, lj = load(ri), load(rj)
                a = 0
                while a < len(ri) and not improved:
                    x = ri[a]
                    dx = dem(x)
                    b = 0
                    while b < len(rj) and not improved:
                        y = rj[b]
                        dy = dem(y)
                        if (capacity <= 0 or (li - dx + dy <= capacity and lj - dy + dx <= capacity)):
                            nri = ri[:a] + [y] + ri[a + 1:]
                            nrj = rj[:b] + [x] + rj[b + 1:]
                            if cost(nri) + cost(nrj) + 1e-12 < cost(ri) + cost(rj):
                                routes[i], routes[j] = nri, nrj
                                improved = True
                        b += 1
                    a += 1
                j += 1
            i += 1

    used = set()
    out = []
    for r in routes:
        nr = []
        cl = 0
        for c in r:
            if c == depot or c in used:
                continue
            d = dem(c)
            if nr and capacity > 0 and cl + d > capacity:
                out.append(nr)
                nr, cl = [c], d
            else:
                nr.append(c)
                cl += d
            used.add(c)
        if nr:
            out.append(nr)

    missing = [c for c in cust if c not in used]
    for c in missing:
        placed = False
        for r in out:
            if capacity <= 0 or load(r) + dem(c) <= capacity:
                p, _ = insert_pos(r, c)
                r.insert(p, c)
                placed = True
                break
        if not placed:
            out.append([c])

    return out
