def solve_cvrp(instance):
    def g(key_list, default=None):
        if isinstance(instance, dict):
            for k in key_list:
                if k in instance:
                    return instance[k]
        return default

    coords = g(("coords", "coordinates", "points", "xy"))
    demands = g(("demands", "demand", "loads"))
    capacity = g(("capacity", "vehicle_capacity", "veh_capacity", "Q"), 0)
    depot = g(("depot_id", "depot", "depot_index"), 0)

    def all_ids():
        if isinstance(instance, dict) and "customers" in instance and isinstance(instance["customers"], list):
            return [c for c in instance["customers"] if c != depot]
        if isinstance(demands, dict):
            return sorted([k for k in demands.keys() if k != depot])
        if isinstance(coords, dict):
            return sorted([k for k in coords.keys() if k != depot])
        if isinstance(demands, list):
            return [i for i in range(len(demands)) if i != depot]
        if isinstance(coords, list):
            return [i for i in range(len(coords)) if i != depot]
        return []

    customers = all_ids()

    def pt(i):
        if coords is None:
            return (0.0, 0.0)
        p = coords[i] if isinstance(coords, dict) else coords[i]
        return (float(p[0]), float(p[1]))

    depot_pt = pt(depot)

    def dem(i):
        if demands is None:
            return 1
        if isinstance(demands, dict):
            return int(demands.get(i, 0))
        return int(demands[i])

    cache = {}

    def dist(a, b):
        if a == b:
            return 0.0
        k = (a, b)
        if k in cache:
            return cache[k]
        pa = depot_pt if a == depot else pt(a)
        pb = depot_pt if b == depot else pt(b)
        dx = pa[0] - pb[0]
        dy = pa[1] - pb[1]
        d = (dx * dx + dy * dy) ** 0.5
        cache[k] = d
        cache[(b, a)] = d
        return d

    def load(route):
        s = 0
        for c in route:
            s += dem(c)
        return s

    def cost(route):
        if not route:
            return 0.0
        t = dist(depot, route[0])
        for i in range(len(route) - 1):
            t += dist(route[i], route[i + 1])
        return t + dist(route[-1], depot)

    def key(i):
        p = pt(i)
        x = p[0] - depot_pt[0]
        y = p[1] - depot_pt[1]
        return (0 if y >= 0 else 1, x / (abs(y) + abs(x) + 1e-12), x * x + y * y, i)

    customers = sorted(customers, key=key)
    routes = []
    cur = []
    cur_load = 0
    for c in customers:
        d = dem(c)
        if capacity and cur and cur_load + d > capacity:
            routes.append(cur)
            cur = [c]
            cur_load = d
        else:
            cur.append(c)
            cur_load += d
    if cur:
        routes.append(cur)

    if capacity:
        fixed = []
        for r in routes:
            if load(r) <= capacity:
                fixed.append(r)
            else:
                for c in r:
                    fixed.append([c])
        routes = fixed

    def two_opt(route):
        n = len(route)
        if n < 4:
            return route[:]
        best = route[:]
        best_cost = cost(best)
        improved = True
        while improved:
            improved = False
            for i in range(n - 2):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    cand = best[:i + 1] + best[i + 1:j + 1][::-1] + best[j + 1:]
                    cc = cost(cand)
                    if cc + 1e-12 < best_cost:
                        best, best_cost = cand, cc
                        improved = True
                        break
                if improved:
                    break
        return best

    routes = [two_opt(r) for r in routes if r]

    def total(rs):
        s = 0.0
        for r in rs:
            s += cost(r)
        return s

    improved = True
    while improved:
        improved = False
        base = total(routes)

        for a in range(len(routes)):
            for b in range(len(routes)):
                if a == b or not routes[a]:
                    continue
                ra = routes[a]
                rb = routes[b]
                la = load(ra)
                lb = load(rb)
                for i, c in enumerate(ra):
                    dc = dem(c)
                    if capacity and lb + dc > capacity:
                        continue
                    for pos in range(len(rb) + 1):
                        nra = ra[:i] + ra[i + 1:]
                        nrb = rb[:pos] + [c] + rb[pos:]
                        cand = routes[:]
                        cand[a] = nra
                        cand[b] = nrb
                        if total(cand) + 1e-12 < base:
                            routes = [two_opt(r) for r in cand if r]
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

        for a in range(len(routes)):
            for b in range(a + 1, len(routes)):
                ra = routes[a]
                rb = routes[b]
                if not ra or not rb:
                    continue
                la = load(ra)
                lb = load(rb)
                for i, ca in enumerate(ra):
                    da = dem(ca)
                    for j, cb in enumerate(rb):
                        db = dem(cb)
                        if capacity and (la - da + db > capacity or lb - db + da > capacity):
                            continue
                        nra = ra[:]
                        nrb = rb[:]
                        nra[i] = cb
                        nrb[j] = ca
                        cand = routes[:]
                        cand[a] = nra
                        cand[b] = nrb
                        if total(cand) + 1e-12 < base:
                            routes = [two_opt(r) for r in cand if r]
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

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
            placed = False
            for r in out:
                if (not capacity) or load(r) + dem(c) <= capacity:
                    best_pos = 0
                    best_inc = None
                    for pos in range(len(r) + 1):
                        prev = depot if pos == 0 else r[pos - 1]
                        nxt = depot if pos == len(r) else r[pos]
                        inc = dist(prev, c) + dist(c, nxt) - dist(prev, nxt)
                        if best_inc is None or inc < best_inc:
                            best_inc = inc
                            best_pos = pos
                    r.insert(best_pos, c)
                    placed = True
                    break
            if not placed:
                out.append([c])

    return out
