def solve_cvrp(instance):
    def read(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        try:
            d = obj.__dict__
            if key in d:
                return d[key]
        except Exception:
            pass
        return default

    depot = read(instance, "depot", 0)
    capacity = read(instance, "capacity", None)
    if capacity is None:
        capacity = read(instance, "vehicle_capacity", None)
    if capacity is None:
        capacity = read(instance, "Q", None)

    customers = read(instance, "customers", None)
    nodes = read(instance, "nodes", None)
    coords = read(instance, "coords", None)
    if coords is None:
        coords = read(instance, "locations", None)
    if coords is None:
        coords = read(instance, "points", None)
    dist_matrix = read(instance, "distance_matrix", None)
    if dist_matrix is None:
        dist_matrix = read(instance, "dist_matrix", None)
    if dist_matrix is None:
        dist_matrix = read(instance, "matrix", None)
    demands = read(instance, "demands", None)

    if customers is None:
        if nodes is not None:
            customers = [n for n in nodes if n != depot]
        elif coords is not None:
            customers = [i for i in range(len(coords)) if i != depot]
        else:
            return []

    demand_of = {}
    if isinstance(demands, dict):
        for k, v in demands.items():
            demand_of[k] = v
    elif isinstance(demands, (list, tuple)):
        for i, v in enumerate(demands):
            demand_of[i] = v

    coord_of = {}
    if isinstance(coords, dict):
        for k, v in coords.items():
            coord_of[k] = v
    elif isinstance(coords, (list, tuple)):
        for i, v in enumerate(coords):
            coord_of[i] = v

    if capacity is None:
        capacity = 0
        for c in customers:
            capacity += demand_of.get(c, 1)

    cust = []
    seen = set()
    for c in customers:
        if c == depot or c in seen:
            continue
        seen.add(c)
        cust.append(c)
    customers = cust
    for c in customers:
        if c not in demand_of:
            demand_of[c] = 1

    def dist(a, b):
        if dist_matrix is not None:
            try:
                return dist_matrix[a][b]
            except Exception:
                try:
                    return dist_matrix[int(a)][int(b)]
                except Exception:
                    pass
        pa = coord_of.get(a)
        pb = coord_of.get(b)
        if pa is None or pb is None:
            return 0
        dx = pa[0] - pb[0]
        dy = pa[1] - pb[1]
        return (dx * dx + dy * dy) ** 0.5

    def route_load(r):
        s = 0
        for x in r:
            s += demand_of.get(x, 1)
        return s

    def route_cost(r):
        if not r:
            return 0
        t = dist(depot, r[0])
        for i in range(len(r) - 1):
            t += dist(r[i], r[i + 1])
        return t + dist(r[-1], depot)

    def best_insertion_pos(r, c):
        best_pos = 0
        best_inc = None
        prev = depot
        for i in range(len(r) + 1):
            nxt = depot if i == len(r) else r[i]
            inc = dist(prev, c) + dist(c, nxt) - dist(prev, nxt)
            if best_inc is None or inc < best_inc:
                best_inc = inc
                best_pos = i
            prev = nxt
        return best_pos, best_inc if best_inc is not None else 0

    def angle_key(c):
        p = coord_of.get(c)
        d = coord_of.get(depot)
        if p is None or d is None:
            return (0, dist(depot, c), c)
        x = p[0] - d[0]
        y = p[1] - d[1]
        quad = 0 if y >= 0 else 1
        denom = abs(x) + abs(y)
        proxy = 0 if denom == 0 else y / denom
        return (quad, proxy, dist(depot, c), c)

    ordered = sorted(customers, key=angle_key)
    routes = []
    cur = []
    load = 0
    for c in ordered:
        d = demand_of.get(c, 1)
        if d > capacity:
            if cur:
                routes.append(cur)
                cur = []
                load = 0
            routes.append([c])
            continue
        if load + d <= capacity:
            cur.append(c)
            load += d
        else:
            if cur:
                routes.append(cur)
            cur = [c]
            load = d
    if cur:
        routes.append(cur)

    cnt = {}
    for r in routes:
        for c in r:
            cnt[c] = cnt.get(c, 0) + 1

    for c in customers:
        if cnt.get(c, 0) == 0:
            best = None
            for ri, r in enumerate(routes):
                if route_load(r) + demand_of.get(c, 1) > capacity:
                    continue
                pos, inc = best_insertion_pos(r, c)
                key = (inc, ri, pos)
                if best is None or key < best[0]:
                    best = (key, ri, pos)
            if best is None:
                routes.append([c])
            else:
                _, ri, pos = best
                routes[ri].insert(pos, c)
            cnt[c] = 1

    routes = [r for r in routes if r]

    improved = True
    rounds = 0
    while improved and rounds < 60:
        rounds += 1
        improved = False

        for r in routes:
            n = len(r)
            if n < 4:
                continue
            best = None
            for i in range(n - 1):
                a = depot if i == 0 else r[i - 1]
                b = r[i]
                for j in range(i + 1, n):
                    c = r[j]
                    d = depot if j == n - 1 else r[j + 1]
                    delta = dist(a, c) + dist(b, d) - dist(a, b) - dist(c, d)
                    if delta < -1e-12 and (best is None or delta < best[0]):
                        best = (delta, i, j)
            if best is not None:
                _, i, j = best
                r[i:j + 1] = list(reversed(r[i:j + 1]))
                improved = True

        if improved:
            continue

        moved = False
        for i in range(len(routes)):
            if moved:
                break
            ri = routes[i]
            for idx, c in enumerate(list(ri)):
                dc = demand_of.get(c, 1)
                a = depot if idx == 0 else ri[idx - 1]
                b = c
                d = depot if idx == len(ri) - 1 else ri[idx + 1]
                removal = dist(a, b) + dist(b, d) - dist(a, d)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    if route_load(rj) + dc > capacity:
                        continue
                    pos, inc = best_insertion_pos(rj, c)
                    gain = removal - inc
                    if gain > 1e-12:
                        rj.insert(pos, c)
                        del ri[idx]
                        if not ri:
                            routes.pop(i)
                        improved = True
                        moved = True
                        break
                if moved:
                    break

    seen = set()
    final = []
    for r in routes:
        nr = []
        load = 0
        for c in r:
            if c in seen:
                continue
            d = demand_of.get(c, 1)
            if load + d <= capacity:
                nr.append(c)
                seen.add(c)
                load += d
        if nr:
            final.append(nr)

    missing = [c for c in customers if c not in seen]
    for c in missing:
        best = None
        for ri, r in enumerate(final):
            if route_load(r) + demand_of.get(c, 1) > capacity:
                continue
            pos, inc = best_insertion_pos(r, c)
            key = (inc, ri, pos)
            if best is None or key < best[0]:
                best = (key, ri, pos)
        if best is None:
            final.append([c])
        else:
            _, ri, pos = best
            final[ri].insert(pos, c)

    return [r for r in final if r]
