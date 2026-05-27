def solve_cvrp(instance):
    def is_dict(x):
        return x.__class__ is dict

    def has_attr(obj, name):
        try:
            d = obj.__dict__
            return name in d
        except:
            return False

    def get_field(obj, names, default=None):
        if obj is None:
            return default
        if is_dict(obj):
            for n in names:
                if n in obj:
                    return obj[n]
            return default
        try:
            d = obj.__dict__
            for n in names:
                if n in d:
                    return d[n]
        except:
            pass
        for n in names:
            if has_attr(obj, n):
                try:
                    return obj.__dict__[n]
                except:
                    pass
        return default

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    capacity = get_field(instance, ["capacity", "vehicle_capacity", "cap"], None)
    demands = get_field(instance, ["demands", "demand"], None)
    coords = get_field(instance, ["coords", "coordinates", "nodes", "points"], None)
    depot = get_field(instance, ["depot", "depot_id", "depot_index"], 0)
    n = get_field(instance, ["n", "num_nodes", "size", "dimension"], None)

    if demands is not None:
        if is_dict(demands):
            nodes = [k for k in demands if k != depot]
            def demand_of(i):
                v = demands[i] if i in demands else 0
                return v if v > 0 else 0
        else:
            nodes = [i for i in range(len(demands)) if i != depot]
            def demand_of(i):
                v = demands[i]
                return v if v > 0 else 0
    else:
        if coords is not None:
            if is_dict(coords):
                nodes = [k for k in coords if k != depot]
            else:
                nodes = [i for i in range(len(coords)) if i != depot]
        else:
            if n is None:
                n = 1
            nodes = [i for i in range(n) if i != depot]
        def demand_of(i):
            return 1

    if coords is None:
        def coord_of(i):
            return (float(i), 0.0)
    elif is_dict(coords):
        def coord_of(i):
            return coords[i]
    else:
        def coord_of(i):
            return coords[i]

    depot_xy = coord_of(depot)

    seen = {}
    uniq = []
    for i in nodes:
        if i != depot and i not in seen:
            seen[i] = 1
            uniq.append(i)
    nodes = uniq

    if capacity is None:
        s = 0
        for i in nodes:
            s += demand_of(i)
        capacity = s if s > 0 else max(1, len(nodes))

    def route_load(r):
        s = 0
        for c in r:
            s += demand_of(c)
        return s

    def route_cost(r):
        if not r:
            return 0.0
        t = dist(depot_xy, coord_of(r[0]))
        for i in range(len(r) - 1):
            t += dist(coord_of(r[i]), coord_of(r[i + 1]))
        t += dist(coord_of(r[-1]), depot_xy)
        return t

    def insert_best(routes, c):
        d = demand_of(c)
        best_i = -1
        best_p = 0
        best_delta = None
        for i in range(len(routes)):
            r = routes[i]
            if route_load(r) + d > capacity:
                continue
            for p in range(len(r) + 1):
                left = depot_xy if p == 0 else coord_of(r[p - 1])
                right = depot_xy if p == len(r) else coord_of(r[p])
                delta = dist(left, coord_of(c)) + dist(coord_of(c), right) - dist(left, right)
                if best_delta is None or delta < best_delta or (delta == best_delta and (i < best_i or (i == best_i and p < best_p))):
                    best_delta = delta
                    best_i = i
                    best_p = p
        if best_i == -1:
            routes.append([c])
        else:
            routes[best_i] = routes[best_i][:best_p] + [c] + routes[best_i][best_p:]

    def sweep_key(i):
        x, y = coord_of(i)
        dx = x - depot_xy[0]
        dy = y - depot_xy[1]
        q = 0
        if dx >= 0 and dy >= 0:
            q = 0
        elif dx < 0 <= dy:
            q = 1
        elif dx < 0 and dy < 0:
            q = 2
        else:
            q = 3
        return (q, dy * dy + dx * dx, i)

    ordered = sorted(nodes, key=sweep_key)
    routes = []
    cur = []
    load = 0
    for c in ordered:
        d = demand_of(c)
        if cur and load + d > capacity:
            routes.append(cur)
            cur = [c]
            load = d
        else:
            cur.append(c)
            load += d
    if cur:
        routes.append(cur)

    def two_opt(r):
        if len(r) < 4:
            return r[:]
        rr = r[:]
        changed = True
        while changed:
            changed = False
            m = len(rr)
            for i in range(m - 2):
                a = depot_xy if i == 0 else coord_of(rr[i - 1])
                b = coord_of(rr[i])
                for k in range(i + 1, m - 1):
                    c = coord_of(rr[k])
                    d = depot_xy if k + 1 == m else coord_of(rr[k + 1])
                    if dist(a, c) + dist(b, d) + 1e-12 < dist(a, b) + dist(c, d):
                        rr[i:k + 1] = rr[i:k + 1][::-1]
                        changed = True
                        break
                if changed:
                    break
        return rr

    routes = [two_opt(r) for r in routes if r]

    improved = True
    limit = (len(nodes) + 1) * 4
    steps = 0
    while improved and steps < limit:
        steps += 1
        improved = False
        loads = [route_load(r) for r in routes]
        best = None
        best_delta = 0.0
        for i in range(len(routes)):
            ri = routes[i]
            for p in range(len(ri)):
                c = ri[p]
                dc = demand_of(c)
                pre = depot_xy if p == 0 else coord_of(ri[p - 1])
                nxt = depot_xy if p + 1 == len(ri) else coord_of(ri[p + 1])
                rem = dist(pre, coord_of(c)) + dist(coord_of(c), nxt) - dist(pre, nxt)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    if loads[j] + dc > capacity:
                        continue
                    rj = routes[j]
                    for q in range(len(rj) + 1):
                        left = depot_xy if q == 0 else coord_of(rj[q - 1])
                        right = depot_xy if q == len(rj) else coord_of(rj[q])
                        add = dist(left, coord_of(c)) + dist(coord_of(c), right) - dist(left, right)
                        delta = add - rem
                        if delta < best_delta - 1e-12 or (best is None and delta <= 0.0):
                            best_delta = delta
                            best = (i, p, j, q)
        if best is not None:
            i, p, j, q = best
            c = routes[i][p]
            routes[i] = routes[i][:p] + routes[i][p + 1:]
            if i < j:
                j -= 0
            routes[j] = routes[j][:q] + [c] + routes[j][q:]
            routes = [r for r in routes if r]
            routes = [two_opt(r) for r in routes]
            improved = True

    used = {}
    final_routes = []
    for r in routes:
        rr = []
        ld = 0
        for c in r:
            if c != depot and c not in used:
                d = demand_of(c)
                if ld + d <= capacity:
                    rr.append(c)
                    ld += d
                    used[c] = 1
        if rr:
            final_routes.append(rr)

    for c in nodes:
        if c not in used:
            insert_best(final_routes, c)
            used[c] = 1

    cleaned = []
    seen2 = {}
    for r in final_routes:
        rr = []
        ld = 0
        for c in r:
            if c != depot and c not in seen2:
                d = demand_of(c)
                if ld + d <= capacity:
                    rr.append(c)
                    ld += d
                    seen2[c] = 1
        if rr:
            cleaned.append(rr)

    for c in nodes:
        if c not in seen2:
            cleaned.append([c])

    return cleaned
