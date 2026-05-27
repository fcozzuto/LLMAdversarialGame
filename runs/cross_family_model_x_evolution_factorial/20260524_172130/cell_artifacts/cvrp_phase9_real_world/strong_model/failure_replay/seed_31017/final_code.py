def solve_cvrp(instance):
    def get(obj, names, default=None):
        try:
            if obj.__class__.__name__ == "dict":
                for n in names:
                    if n in obj:
                        return obj[n]
                return default
        except Exception:
            pass
        for n in names:
            try:
                return obj[n]
            except Exception:
                pass
            try:
                d = obj.__dict__
                if n in d:
                    return d[n]
            except Exception:
                pass
        return default

    depot = get(instance, ("depot",), 0)
    capacity = get(instance, ("capacity", "vehicle_capacity"), None)
    demand = get(instance, ("demand", "demands"), None)
    coords = get(instance, ("coords", "coordinates", "points", "xy"), None)
    dist = get(instance, ("distance_matrix", "distances", "matrix"), None)
    customers = get(instance, ("customers", "nodes", "vertices"), None)

    def is_dict_like(x):
        try:
            return x.__class__.__name__ == "dict"
        except Exception:
            return False

    def seq_len(x):
        try:
            return len(x)
        except Exception:
            return 0

    if customers is None:
        if demand is not None:
            if is_dict_like(demand):
                customers = [k for k in demand.keys()]
            else:
                customers = list(range(seq_len(demand)))
        elif coords is not None:
            if is_dict_like(coords):
                customers = [k for k in coords.keys()]
            else:
                customers = list(range(seq_len(coords)))
        elif dist is not None:
            customers = list(range(seq_len(dist)))
        else:
            return []

    customers = [c for c in customers if c != depot]

    def dem(i):
        if demand is None:
            return 1
        if is_dict_like(demand):
            v = demand.get(i, 1)
            return v if v is not None else 1
        try:
            if 0 <= i < len(demand):
                v = demand[i]
                return v if v is not None else 1
        except Exception:
            pass
        return 1

    def coord(i):
        if coords is None:
            return None
        if is_dict_like(coords):
            return coords.get(i)
        try:
            if 0 <= i < len(coords):
                return coords[i]
        except Exception:
            pass
        return None

    def dist_f(i, j):
        if dist is not None:
            try:
                return dist[i][j]
            except Exception:
                pass
        ci = coord(i)
        cj = coord(j)
        if ci is None or cj is None:
            return abs(i - j)
        dx = ci[0] - cj[0]
        dy = ci[1] - cj[1]
        return (dx * dx + dy * dy) ** 0.5

    if capacity is None:
        total = 0
        for c in customers:
            total += dem(c)
        capacity = total if total > 0 else 1

    dc = coord(depot)
    if dc is not None:
        def order_key(c):
            p = coord(c)
            if p is None:
                return (2, c)
            x, y = p[0], p[1]
            dx = x - dc[0]
            dy = y - dc[1]
            return (0 if dy >= 0 else 1, 0 if dx >= 0 else 1, abs(dy) / (abs(dx) + 1e-12), dx * dx + dy * dy, c)
        customers = sorted(customers, key=order_key)
    else:
        customers = sorted(customers, key=lambda c: (dist_f(depot, c), -dem(c), c))

    routes = []
    cur = []
    load = 0

    for c in customers:
        x = dem(c)
        if x > capacity:
            if cur:
                routes.append(cur)
                cur = []
                load = 0
            routes.append([c])
            continue
        if load + x <= capacity:
            cur.append(c)
            load += x
        else:
            if cur:
                routes.append(cur)
            cur = [c]
            load = x
    if cur:
        routes.append(cur)

    def rload(r):
        s = 0
        for c in r:
            s += dem(c)
        return s

    def route_cost(r):
        if not r:
            return 0
        cost = dist_f(depot, r[0])
        for i in range(len(r) - 1):
            cost += dist_f(r[i], r[i + 1])
        cost += dist_f(r[-1], depot)
        return cost

    def ins_delta(r, pos, c):
        a = depot if pos == 0 else r[pos - 1]
        b = depot if pos == len(r) else r[pos]
        return dist_f(a, c) + dist_f(c, b) - dist_f(a, b)

    def rem_delta(r, pos):
        c = r[pos]
        a = depot if pos == 0 else r[pos - 1]
        b = depot if pos + 1 == len(r) else r[pos + 1]
        return dist_f(a, b) - dist_f(a, c) - dist_f(c, b)

    seen = {}
    for i in range(len(routes)):
        for c in routes[i]:
            seen[c] = 1

    missing = [c for c in customers if c not in seen]
    for c in missing:
        best = None
        best_ri = -1
        best_pos = -1
        for ri in range(len(routes)):
            if rload(routes[ri]) + dem(c) > capacity:
                continue
            r = routes[ri]
            for pos in range(len(r) + 1):
                val = (ins_delta(r, pos, c), ri, pos)
                if best is None or val < best:
                    best = val
                    best_ri = ri
                    best_pos = pos
        if best_ri < 0:
            routes.append([c])
        else:
            r = routes[best_ri]
            routes[best_ri] = r[:best_pos] + [c] + r[best_pos:]

    for _ in range(6):
        improved = False
        loads = [rload(r) for r in routes]

        # relocate
        for i in range(len(routes)):
            if not routes[i]:
                continue
            for p in range(len(routes[i])):
                c = routes[i][p]
                dc = dem(c)
                rem = rem_delta(routes[i], p)
                best_j = -1
                best_q = -1
                best_gain = 0
                for j in range(len(routes)):
                    if i == j:
                        continue
                    if loads[j] + dc > capacity:
                        continue
                    r2 = routes[j]
                    for q in range(len(r2) + 1):
                        gain = rem - ins_delta(r2, q, c)
                        if gain > best_gain + 1e-12 or (gain > -1e-12 and abs(gain - best_gain) <= 1e-12 and (best_j < 0 or (j, q) < (best_j, best_q))):
                            best_gain = gain
                            best_j = j
                            best_q = q
                if best_j >= 0 and best_gain > 1e-12:
                    r1 = routes[i]
                    c2 = r1[p]
                    del r1[p]
                    if best_j > i:
                        best_j -= 1
                    routes[best_j] = routes[best_j][:best_q] + [c2] + routes[best_j][best_q:]
                    improved = True
                    break
            if improved:
                break
        if improved:
            continue

        # swap
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                r1 = routes[i]
                r2 = routes[j]
                if not r1 or not r2:
                    continue
                for p in range(len(r1)):
                    a = r1[p]
                    da = dem(a)
                    for q in range(len(r2)):
                        b = r2[q]
                        db = dem(b)
                        if loads[i] - da + db > capacity or loads[j] - db + da > capacity:
                            continue
                        gain = rem_delta(r1, p) + rem_delta(r2, q)
                        gain -= ins_delta(r1[:p] + r1[p + 1:], p, b)
                        gain -= ins_delta(r2[:q] + r2[q + 1:], q, a)
                        if gain > 1e-12:
                            r1[p], r2[q] = b, a
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break
        if not improved:
            break

    # cleanup empty routes and final repair
    routes = [r for r in routes if r]
    seen = {}
    for r in routes:
        for c in r:
            seen[c] = 1

    missing = [c for c in customers if c not in seen]
    for c in missing:
        placed = False
        best = None
        bj = bp = -1
        for j in range(len(routes)):
            if rload(routes[j]) + dem(c) > capacity:
                continue
