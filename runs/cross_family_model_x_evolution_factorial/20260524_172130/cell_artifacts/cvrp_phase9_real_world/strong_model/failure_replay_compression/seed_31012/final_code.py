def solve_cvrp(instance):
    def get_field(names, default=None):
        if isinstance(instance, dict):
            for n in names:
                if n in instance:
                    return instance[n]
        d = instance.__dict__ if hasattr(instance, "__dict__") else None
        if d is not None:
            for n in names:
                if n in d:
                    return d[n]
        return default

    coords = get_field(["coordinates", "coords", "points", "locations", "xy", "nodes"], None)
    demands = get_field(["demands", "demand"], None)
    capacity = get_field(["capacity", "vehicle_capacity", "cap"], None)
    depot = get_field(["depot", "depot_id", "depot_index"], 0)

    if coords is None:
        coords = []
    if len(coords) and isinstance(coords[0], (list, tuple)) and len(coords[0]) >= 2:
        coords = [(p[0], p[1]) for p in coords]
    n = len(coords)
    if demands is None:
        demands = [0] * n
    if len(demands) < n:
        demands = list(demands) + [0] * (n - len(demands))
    if capacity is None:
        s = 0
        for d in demands:
            s += d
        capacity = s if s > 0 else 1

    depot_idx = depot if isinstance(depot, int) and 0 <= depot < n else 0
    customers = [i for i in range(n) if i != depot_idx]
    if not customers:
        return []

    def dist(i, j):
        xi, yi = coords[i]
        xj, yj = coords[j]
        dx = xi - xj
        dy = yi - yj
        return (dx * dx + dy * dy) ** 0.5

    dx0, dy0 = coords[depot_idx]
    def sweep_key(i):
        x, y = coords[i]
        dx = x - dx0
        dy = y - dy0
        quad = 0
        if dy < 0:
            quad += 2
        if dx < 0:
            quad += 1
        ay = -dy if dy < 0 else dy
        ax = -dx if dx < 0 else dx
        t = ay / (ax + ay + 1e-12)
        return (quad, t, dist(depot_idx, i), i)

    customers.sort(key=sweep_key)

    routes = []
    cur = []
    load = 0
    for c in customers:
        d = demands[c]
        if cur and load + d > capacity:
            routes.append(cur)
            cur = []
            load = 0
        if d > capacity:
            if cur:
                routes.append(cur)
                cur = []
                load = 0
            routes.append([c])
        else:
            cur.append(c)
            load += d
    if cur:
        routes.append(cur)

    def rload(rt):
        s = 0
        for c in rt:
            s += demands[c]
        return s

    def rcost(rt):
        if not rt:
            return 0.0
        c = dist(depot_idx, rt[0])
        for i in range(len(rt) - 1):
            c += dist(rt[i], rt[i + 1])
        c += dist(rt[-1], depot_idx)
        return c

    def best_pos(rt, c):
        if not rt:
            return 0, 2 * dist(depot_idx, c)
        best_p = 0
        best_d = dist(depot_idx, c) + dist(c, rt[0]) - dist(depot_idx, rt[0])
        for k in range(len(rt) - 1):
            a = rt[k]
            b = rt[k + 1]
            d = dist(a, c) + dist(c, b) - dist(a, b)
            if d < best_d:
                best_d = d
                best_p = k + 1
        d = dist(rt[-1], c) + dist(c, depot_idx) - dist(rt[-1], depot_idx)
        if d < best_d:
            best_d = d
            best_p = len(rt)
        return best_p, best_d

    seen = {}
    for rt in routes:
        for c in rt:
            seen[c] = seen.get(c, 0) + 1
    clean = []
    used = set()
    for rt in routes:
        nr = []
        for c in rt:
            if c not in used:
                used.add(c)
                nr.append(c)
        if nr:
            clean.append(nr)
    routes = clean

    missing = [c for c in customers if c not in used]
    for c in missing:
        best = None
        best_d = None
        for i, rt in enumerate(routes):
            if rload(rt) + demands[c] > capacity:
                continue
            p, d = best_pos(rt, c)
            if best_d is None or d < best_d or (d == best_d and i < best[0]):
                best = (i, p)
                best_d = d
        if best is None:
            routes.append([c])
        else:
            i, p = best
            routes[i].insert(p, c)

    improved = True
    while improved:
        improved = False
        best = None
        best_gain = 0.0
        loads = [rload(rt) for rt in routes]
        for i in range(len(routes)):
            rt = routes[i]
            li = loads[i]
            for p, c in enumerate(rt):
                dc = demands[c]
                prev = depot_idx if p == 0 else rt[p - 1]
                nex = depot_idx if p == len(rt) - 1 else rt[p + 1]
                rem = dist(prev, c) + dist(c, nex) - dist(prev, nex)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    if loads[j] + dc > capacity:
                        continue
                    pos, ins = best_pos(routes[j], c)
                    gain = rem - ins
                    if gain > best_gain + 1e-12 or (abs(gain - best_gain) <= 1e-12 and best is not None and (i, p, j, pos) < best):
                        best_gain = gain
                        best = (i, p, j, pos, c)
                for j in range(i + 1, len(routes)):
                    rt2 = routes[j]
                    lj = loads[j]
                    for q, c2 in enumerate(rt2):
                        d2 = demands[c2]
                        if li - dc + d2 > capacity or lj - d2 + dc > capacity:
                            continue
                        prev2 = depot_idx if q == 0 else rt2[q - 1]
                        nex2 = depot_idx if q == len(rt2) - 1 else rt2[q + 1]
                        before = dist(prev, c) + dist(c, nex) + dist(prev2, c2) + dist(c2, nex2)
                        after = dist(prev, c2) + dist(c2, nex) + dist(prev2, c) + dist(c, nex2)
                        gain = before - after
                        if gain > best_gain + 1e-12 or (abs(gain - best_gain) <= 1e-12 and best is not None and (i, p, j, q) < best[:4]):
                            best_gain = gain
                            best = (i, p, j, q, c, c2)
        if best_gain > 1e-12 and best is not None:
            if len(best) == 5:
                i, p, j, pos, c = best
                routes[i].pop(p)
                if not routes[i]:
                    routes.pop(i)
                    if j > i:
                        j -= 1
                if j >= len(routes):
                    routes.append([c])
                else:
                    routes[j].insert(pos, c)
            else:
                i, p, j, q, c, c2 = best
                routes[i][p] = c2
                routes[j][q] = c
            routes = [rt for rt in routes if rt]
            improved = True

    used = set()
    final = []
    for rt in routes:
        nr = []
        for c in rt:
            if c not in used:
                used.add(c)
                nr.append(c)
        if nr:
            final.append(nr)
    for c in customers:
        if c not in used:
            best = None
            best_d = None
            for i, rt in enumerate(final):
                if rload(rt) + demands[c] > capacity:
                    continue
                p, d = best_pos(rt, c)
                if best_d is None or d < best_d:
                    best_d = d
                    best = (i, p)
            if best is None:
                final.append([c])
            else:
                i, p = best
                final[i].insert(p, c)

    return final
