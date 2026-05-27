def solve_cvrp(instance):
    def fetch(obj, keys, default=None):
        if isinstance(keys, str):
            keys = (keys,)
        if isinstance(obj, dict):
            for k in keys:
                if k in obj:
                    return obj[k]
            return default
        d = obj.__dict__ if hasattr(obj, "__dict__") else None
        if d is not None:
            for k in keys:
                if k in d:
                    return d[k]
        return default

    cap = fetch(instance, ("capacity", "vehicle_capacity", "cap"), None)
    depot = fetch(instance, ("depot", "depot_id"), 0)
    demands = fetch(instance, ("demands", "demand"), None)
    coords = fetch(instance, ("coordinates", "coords", "locations", "points"), None)
    n = fetch(instance, ("n_customers", "n", "num_customers"), None)

    def to_map(x):
        if x is None:
            return None
        if isinstance(x, dict):
            return x
        if isinstance(x, list) or isinstance(x, tuple):
            return {i: x[i] for i in range(len(x))}
        return None

    dm = to_map(demands)
    cm = to_map(coords)

    customers = []
    if dm is not None:
        customers = [k for k in dm.keys() if k != depot]
    elif cm is not None:
        customers = [k for k in cm.keys() if k != depot]
    elif n is not None:
        customers = list(range(1, int(n) + 1))
        if depot in customers:
            customers.remove(depot)
    customers = sorted(customers)

    def demand(i):
        if dm is None:
            return 0
        return dm.get(i, 0)

    def coord(i):
        if cm is None:
            return None
        return cm.get(i, None)

    def dist(a, b):
        ca = coord(a)
        cb = coord(b)
        if ca is None or cb is None:
            return 0.0
        dx = ca[0] - cb[0]
        dy = ca[1] - cb[1]
        return (dx * dx + dy * dy) ** 0.5

    if cap is None:
        cap = sum(max(0, demand(c)) for c in customers) or 1

    depot_xy = coord(depot)
    if depot_xy is not None:
        dx0, dy0 = depot_xy[0], depot_xy[1]
        items = []
        for c in customers:
            x, y = coord(c)
            dx = x - dx0
            dy = y - dy0
            q = 0 if dx >= 0 and dy >= 0 else 1 if dx < 0 <= dy else 2 if dx < 0 and dy < 0 else 3
            s = dy / (dx + 1e-12) if q == 0 else (-dx) / (dy + 1e-12) if q == 1 else (-dy) / (-dx + 1e-12) if q == 2 else dx / (-dy + 1e-12)
            items.append((q, s, dx * dx + dy * dy, c))
        items.sort()
        ordered = [c for _, _, _, c in items]
    else:
        ordered = sorted(customers, key=lambda c: (-demand(c), c))

    routes = []
    cur = []
    load = 0
    for c in ordered:
        dc = demand(c)
        if cur and load + dc > cap:
            routes.append(cur)
            cur = []
            load = 0
        cur.append(c)
        load += dc
    if cur:
        routes.append(cur)

    def rload(r):
        s = 0
        for c in r:
            s += demand(c)
        return s

    def rcost(r):
        if not r:
            return 0.0
        t = dist(depot, r[0])
        for i in range(len(r) - 1):
            t += dist(r[i], r[i + 1])
        return t + dist(r[-1], depot)

    def two_opt(r):
        n = len(r)
        if n < 4:
            return r
        improved = True
        while improved:
            improved = False
            for i in range(n - 3):
                a = depot if i == 0 else r[i - 1]
                b = r[i]
                for j in range(i + 2, n - 1):
                    c = r[j]
                    d = depot if j == n - 1 else r[j + 1]
                    if dist(a, b) + dist(c, d) > dist(a, c) + dist(b, d) + 1e-12:
                        r = r[:i] + r[i:j + 1][::-1] + r[j + 1:]
                        improved = True
                        break
                if improved:
                    break
        return r

    routes = [two_opt(r[:]) for r in routes if r]

    def ins_delta(r, pos, c):
        a = depot if pos == 0 else r[pos - 1]
        b = depot if pos == len(r) else r[pos]
        return dist(a, c) + dist(c, b) - dist(a, b)

    def best_pos(r, c):
        bp = 0
        bd = ins_delta(r, 0, c)
        for p in range(1, len(r) + 1):
            d = ins_delta(r, p, c)
            if d < bd - 1e-12 or (abs(d - bd) <= 1e-12 and p < bp):
                bp, bd = p, d
        return bp, bd

    improved = True
    while improved:
        improved = False
        best = None
        best_gain = 0.0
        loads = [rload(r) for r in routes]
        for i, ri in enumerate(routes):
            li = loads[i]
            for pi, a in enumerate(ri):
                da = demand(a)
                pa = depot if pi == 0 else ri[pi - 1]
                na = depot if pi == len(ri) - 1 else ri[pi + 1]
                rem_a = dist(pa, a) + dist(a, na) - dist(pa, na)
                for j, rj in enumerate(routes):
                    if i == j or loads[j] + da > cap:
                        continue
                    pos, add_a = best_pos(rj, a)
                    gain = rem_a - add_a
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best = (i, pi, j, pos, a)
        if best is not None:
            i, pi, j, pos, a = best
            ri = routes[i][:]
            rj = routes[j][:]
            ri.pop(pi)
            rj = rj[:pos] + [a] + rj[pos:]
            if ri:
                routes[i] = two_opt(ri)
            else:
                routes.pop(i)
                if j > i:
                    j -= 1
            routes[j] = two_opt(rj)
            improved = True
            continue

        best = None
        best_gain = 0.0
        loads = [rload(r) for r in routes]
        for i in range(len(routes)):
            ri = routes[i]
            for pi, a in enumerate(ri):
                da = demand(a)
                pa = depot if pi == 0 else ri[pi - 1]
                na = depot if pi == len(ri) - 1 else ri[pi + 1]
                rem_a = dist(pa, a) + dist(a, na) - dist(pa, na)
                for j in range(i + 1, len(routes)):
                    rj = routes[j]
                    for pj, b in enumerate(rj):
                        db = demand(b)
                        if loads[i] - da + db > cap or loads[j] - db + da > cap:
                            continue
                        pb = depot if pj == 0 else rj[pj - 1]
                        nb = depot if pj == len(rj) - 1 else rj[pj + 1]
                        rem_b = dist(pb, b) + dist(b, nb) - dist(pb, nb)
                        ai = ri[:pi] + ri[pi + 1:]
                        bj = rj[:pj] + rj[pj + 1:]
                        gain = (rem_a + rem_b) - (ins_delta(bj, pj, a) + ins_delta(ai, pi, b))
                        if gain > best_gain + 1e-12:
                            best_gain = gain
                            best = (i, pi, j, pj, a, b)
        if best is not None:
            i, pi, j, pj, a, b = best
            ri = routes[i][:]
            rj = routes[j][:]
            ri[pi] = b
            rj[pj] = a
            routes[i] = two_opt(ri)
            routes[j] = two_opt(rj)
            improved = True

    seen = set()
    out = []
    for r in routes:
        rr = []
        for c in r:
            if c != depot and c not in seen:
                seen.add(c)
                rr.append(c)
        if rr:
            out.append(rr)
    for c in customers:
        if c not in seen:
            best_i = -1
            best_p = 0
            best_d = None
            dc = demand(c)
            for i, r in enumerate(out):
                if rload(r) + dc > cap:
                    continue
                p, d = best_pos(r, c)
                if best_d is None or d < best_d - 1e-12:
                    best_i, best_p, best_d = i, p, d
            if best_i < 0:
                out.append([c])
            else:
                r = out[best_i]
                out[best_i] = r[:best_p] + [c] + r[best_p:]
    return out
