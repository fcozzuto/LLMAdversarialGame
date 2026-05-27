def solve_cvrp(instance):
    def get_value(obj, names, default=None):
        if isinstance(names, str):
            names = (names,)
        if isinstance(obj, dict):
            for n in names:
                if n in obj:
                    return obj[n]
            return default
        d = None
        try:
            d = obj.__dict__
        except Exception:
            d = None
        if d is not None:
            for n in names:
                if n in d:
                    return d[n]
        return default

    coords = get_value(instance, ("coordinates", "coords", "locations", "points", "nodes"), None)
    demands = get_value(instance, ("demands", "demand"), None)
    capacity = get_value(instance, ("capacity", "vehicle_capacity", "cap", "Q", "vehicle_cap"), None)

    n = None
    if demands is not None:
        n = len(demands) - 1
    elif coords is not None:
        n = len(coords) - 1
    else:
        n = int(get_value(instance, ("n_customers", "customers", "num_customers"), 0))

    if capacity is None:
        capacity = int(get_value(instance, ("capacity", "vehicle_capacity", "cap", "Q", "vehicle_cap"), 0))

    if demands is None:
        demands = [0] + [1] * n

    def point(i):
        if coords is None:
            return (0.0, 0.0)
        p = coords[i]
        if isinstance(p, dict):
            return (float(p.get("x", 0.0)), float(p.get("y", 0.0)))
        return (float(p[0]), float(p[1]))

    def dist(i, j):
        if coords is None:
            return 0.0
        a = point(i)
        b = point(j)
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    customers = list(range(1, n + 1))

    if capacity <= 0:
        capacity = 1

    # Build initial routes by deterministic sweep/savings hybrid.
    routes = []
    if coords is not None and n > 0:
        polar = []
        depot = point(0)
        for c in customers:
            p = point(c)
            angle = 0.0
            dx = p[0] - depot[0]
            dy = p[1] - depot[1]
            if dx == 0.0 and dy == 0.0:
                angle = 0.0
            else:
                if dx >= 0 and dy >= 0:
                    angle = dy / (abs(dx) + abs(dy) + 1e-12)
                elif dx < 0 <= dy:
                    angle = 2.0 - dy / (abs(dx) + abs(dy) + 1e-12)
                elif dx < 0 and dy < 0:
                    angle = 4.0 - dy / (abs(dx) + abs(dy) + 1e-12)
                else:
                    angle = 6.0 + dy / (abs(dx) + abs(dy) + 1e-12)
            polar.append((angle, dist(0, c), c))
        polar.sort()
        ordered = [c for _, _, c in polar]

        cur = []
        load = 0
        for c in ordered:
            d = demands[c]
            if cur and load + d > capacity:
                routes.append(cur)
                cur = []
                load = 0
            cur.append(c)
            load += d
        if cur:
            routes.append(cur)

        # Limited savings-based merge to reduce route count.
        changed = True
        while changed:
            changed = False
            best_gain = 0.0
            best_pair = None
            best_merged = None
            for i in range(len(routes)):
                if not routes[i]:
                    continue
                a = routes[i]
                load_a = 0
                for x in a:
                    load_a += demands[x]
                for j in range(i + 1, len(routes)):
                    if not routes[j]:
                        continue
                    b = routes[j]
                    load_b = 0
                    for x in b:
                        load_b += demands[x]
                    if load_a + load_b > capacity:
                        continue
                    candidates = []
                    candidates.append((a + b, dist(0, a[0]) + dist(a[-1], 0) + dist(0, b[0]) + dist(b[-1], 0) - (dist(0, a[0]) + dist(a[-1], b[0]) + dist(b[-1], 0))))
                    candidates.append((a + b[::-1], dist(0, a[0]) + dist(a[-1], 0) + dist(0, b[-1]) + dist(b[0], 0) - (dist(0, a[0]) + dist(a[-1], b[-1]) + dist(b[0], 0))))
                    candidates.append((a[::-1] + b, dist(0, a[-1]) + dist(a[0], 0) + dist(0, b[0]) + dist(b[-1], 0) - (dist(0, a[-1]) + dist(a[0], b[0]) + dist(b[-1], 0))))
                    candidates.append((a[::-1] + b[::-1], dist(0, a[-1]) + dist(a[0], 0) + dist(0, b[-1]) + dist(b[0], 0) - (dist(0, a[-1]) + dist(a[0], b[-1]) + dist(b[0], 0))))
                    for merged, gain in candidates:
                        if gain > best_gain + 1e-12:
                            best_gain = gain
                            best_pair = (i, j)
                            best_merged = merged
            if best_pair is not None:
                i, j = best_pair
                routes[i] = best_merged
                routes[j] = []
                changed = True
        routes = [r for r in routes if r]
    else:
        customers_sorted = sorted(customers, key=lambda c: (-demands[c], c))
        cur = []
        load = 0
        for c in customers_sorted:
            d = demands[c]
            if cur and load + d > capacity:
                routes.append(cur)
                cur = []
                load = 0
            cur.append(c)
            load += d
        if cur:
            routes.append(cur)

    # Ensure all customers appear exactly once.
    seen = set()
    cleaned = []
    for r in routes:
        nr = []
        load = 0
        for c in r:
            if c not in seen:
                if load + demands[c] <= capacity or not nr:
                    nr.append(c)
                    seen.add(c)
                    load += demands[c]
        if nr:
            cleaned.append(nr)
    routes = cleaned

    missing = []
    for c in customers:
        if c not in seen:
            missing.append(c)

    for c in missing:
        placed = False
        for r in routes:
            load = 0
            for x in r:
                load += demands[x]
            if load + demands[c] <= capacity:
                r.append(c)
                placed = True
                break
        if not placed:
            routes.append([c])

    # Simple intra-route improvement for geometric instances.
    if coords is not None:
        def route_cost(r):
            if not r:
                return 0.0
            total = dist(0, r[0]) + dist(r[-1], 0)
            k = 0
            while k + 1 < len(r):
                total += dist(r[k], r[k + 1])
                k += 1
            return total

        improved = True
        while improved:
            improved = False
            for idx in range(len(routes)):
                r = routes[idx]
                if len(r) < 4:
                    continue
                best = r
                best_cost = route_cost(r)
                m = len(r)
                i = 0
                while i < m - 1:
                    j = i + 2
                    while j < m:
                        cand = r[:i + 1] + r[i + 1:j + 1][::-1] + r[j + 1:]
                        cc = route_cost(cand)
                        if cc + 1e-12 < best_cost:
                            best = cand
                            best_cost = cc
                        j += 1
                    i += 1
                if best is not r:
                    routes[idx] = best
                    improved = True

    # Final validation and repair.
    seen = set()
    final_routes = []
    for r in routes:
        nr = []
        load = 0
        for c in r:
            if c in seen:
                continue
            d = demands[c]
            if nr and load + d > capacity:
                final_routes.append(nr)
                nr = [c]
                load = d
            else:
                nr.append(c)
                load += d
            seen.add(c)
        if nr:
            final_routes.append(nr)

    for c in customers:
        if c not in seen:
            final_routes.append([c])

    return final_routes
