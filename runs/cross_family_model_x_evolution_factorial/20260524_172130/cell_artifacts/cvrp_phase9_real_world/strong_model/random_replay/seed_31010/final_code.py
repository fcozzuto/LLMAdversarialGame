def solve_cvrp(instance):
    def get(obj, keys, default=None):
        try:
            for k in keys:
                try:
                    return obj[k]
                except:
                    pass
        except:
            pass
        try:
            d = obj.__dict__
            for k in keys:
                try:
                    return d[k]
                except:
                    pass
        except:
            pass
        return default

    depot = get(instance, ["depot", "depot_id", "start", "origin"], 0)
    cap = get(instance, ["capacity", "vehicle_capacity", "Q"], 0)
    coords = get(instance, ["coords", "locations", "xy", "points"], None)
    demands = get(instance, ["demands", "demand"], None)
    customers = get(instance, ["customers", "nodes", "customer_ids"], None)

    try:
        cap = float(cap)
    except:
        cap = 0.0

    def is_seq(x):
        try:
            len(x)
            return True
        except:
            return False

    def dem(i):
        v = 0
        try:
            v = demands.get(i, 0)
        except:
            try:
                if is_seq(demands) and i >= 0 and i < len(demands):
                    v = demands[i]
            except:
                v = 0
        if v is None:
            return 0
        try:
            return float(v)
        except:
            return 0

    def pt(i):
        try:
            return coords.get(i)
        except:
            pass
        try:
            if is_seq(coords) and i >= 0 and i < len(coords):
                return coords[i]
        except:
            pass
        return None

    if customers is None:
        try:
            keys = list(demands.keys())
            customers = [k for k in keys if k != depot]
        except:
            try:
                keys = list(coords.keys())
                customers = [k for k in keys if k != depot]
            except:
                n = get(instance, ["n", "num_nodes", "size"], 0)
                try:
                    n = int(n)
                except:
                    n = 0
                customers = list(range(1, n))

    customers = [c for c in customers if c != depot]
    customers = sorted(customers)

    depot_pt = pt(depot)

    def dist(a, b):
        pa = pt(a)
        pb = pt(b)
        try:
            if pa is not None and pb is not None and len(pa) >= 2 and len(pb) >= 2:
                dx = pa[0] - pb[0]
                dy = pa[1] - pb[1]
                return (dx * dx + dy * dy) ** 0.5
        except:
            pass
        if a == b:
            return 0.0
        return abs(a - b) + 1e-6 * (dem(a) + dem(b))

    def route_load(r):
        s = 0.0
        for c in r:
            s += dem(c)
        return s

    def route_cost(r):
        if not r:
            return 0.0
        t = dist(depot, r[0])
        for i in range(len(r) - 1):
            t += dist(r[i], r[i + 1])
        t += dist(r[-1], depot)
        return t

    def angle_key(c):
        p = pt(c)
        if depot_pt is None or p is None:
            return (0, c)
        try:
            x = p[0] - depot_pt[0]
            y = p[1] - depot_pt[1]
            q = 0 if x >= 0 and y >= 0 else 1 if x < 0 <= y else 2 if x < 0 and y < 0 else 3
            return (q, y / (abs(x) + abs(y) + 1e-12), c)
        except:
            return (0, c)

    def best_insertion_position(route, c):
        best_pos = 0
        best_delta = None
        if not route:
            return 0, 0.0
        for i in range(len(route) + 1):
            prevn = depot if i == 0 else route[i - 1]
            nextn = depot if i == len(route) else route[i]
            delta = dist(prevn, c) + dist(c, nextn) - dist(prevn, nextn)
            if best_delta is None or delta < best_delta or (delta == best_delta and i < best_pos):
                best_delta = delta
                best_pos = i
        return best_pos, best_delta

    # Initial constructive solution: sweep or nearest-feasible
    routes = []
    remaining = customers[:]

    if depot_pt is not None:
        ordered = sorted(remaining, key=angle_key)
        cur = []
        cur_load = 0.0
        for c in ordered:
            d = dem(c)
            if cur and cur_load + d > cap:
                routes.append(cur)
                cur = [c]
                cur_load = d
            else:
                cur.append(c)
                cur_load += d
        if cur:
            routes.append(cur)
    else:
        while remaining:
            route = []
            load = 0.0
            last = depot
            while True:
                best = None
                best_key = None
                for c in remaining:
                    d = dem(c)
                    if route and load + d > cap:
                        continue
                    k = (dist(last, c), d, c)
                    if best_key is None or k < best_key:
                        best_key = k
                        best = c
                if best is None:
                    break
                route.append(best)
                load += dem(best)
                last = best
                remaining.remove(best)
            if not route:
                route = [remaining.pop(0)]
            routes.append(route)

    # Repair any accidental overloads by splitting
    repaired = []
    for r in routes:
        if route_load(r) <= cap:
            repaired.append(r)
        else:
            cur = []
            s = 0.0
            for c in r:
                d = dem(c)
                if cur and s + d > cap:
                    repaired.append(cur)
                    cur = [c]
                    s = d
                else:
                    cur.append(c)
                    s += d
            if cur:
                repaired.append(cur)
    routes = [r for r in repaired if r]

    # Build customer -> route index map
    def rebuild_map():
        mp = {}
        for ri in range(len(routes)):
            for c in routes[ri]:
                mp[c] = ri
        return mp

    # Local improvement: intra-route 2-opt and inter-route relocate / swap
    def two_opt_route(r):
        best = r[:]
        best_cost = route_cost(best)
        n = len(best)
        improved = True
        while improved and n >= 4:
            improved = False
            for i in range(n - 2):
                for j in range(i + 2, n):
                    cand = best[:i + 1] + best[i + 1:j + 1][::-1] + best[j + 1:]
                    cst = route_cost(cand)
                    if cst + 1e-12 < best_cost or (cst == best_cost and cand < best):
                        best = cand
                        best_cost = cst
                        improved = True
                        n = len(best)
                        break
                if improved:
                    break
        return best

    changed = True
    it = 0
    while changed and it < 4:
        it += 1
        changed = False

        # Intra-route improvement
        for i in range(len(routes)):
            nr = two_opt_route(routes[i])
            if nr != routes[i]:
                routes[i] = nr
                changed = True

        # Inter-route relocation
        mp = rebuild_map()
        best_move = None
        best_gain = 0.0
        for a in range(len(routes)):
            ra = routes[a]
            la = route_load(ra)
            for idx in range(len(ra)):
                c = ra[idx]
                dc = dem(c)
                for b in range(len(routes)):
                    if a == b:
                        continue
                    rb = routes[b]
                    lb = route_load(rb)
                    if lb + dc > cap + 1e-12:
                        continue
                    ra2 = ra[:idx] + ra[idx + 1:]
                    if not ra2:
                        continue
                    old = route_cost(ra) + route_cost(rb)
                    pos, _ = best_insertion_position(rb, c)
                    rb2 = rb[:pos] + [c] + rb[pos:]
                    new = route_cost(ra2) + route_cost(rb2)
                    gain = old - new
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best_move = (a, b, idx, pos, ra2, rb2)
