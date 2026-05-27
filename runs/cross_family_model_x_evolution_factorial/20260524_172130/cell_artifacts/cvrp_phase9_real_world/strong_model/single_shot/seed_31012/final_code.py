def solve_cvrp(instance):
    def get_value(obj, key, default=None):
        if isinstance(obj, dict):
            if key in obj:
                return obj[key]
            return default
        d = None
        try:
            d = obj.__dict__
        except Exception:
            d = None
        if isinstance(d, dict) and key in d:
            return d[key]
        return default

    def is_seq(x):
        return isinstance(x, (list, tuple))

    def pick(*vals):
        for v in vals:
            if v is not None:
                return v
        return None

    depot = pick(get_value(instance, "depot"), 0)
    capacity = pick(get_value(instance, "capacity"), get_value(instance, "vehicle_capacity"), get_value(instance, "Q"))
    if capacity is None:
        capacity = 10 ** 18

    coords = pick(get_value(instance, "coords"), get_value(instance, "coordinates"), get_value(instance, "points"), get_value(instance, "xy"))
    demands = pick(get_value(instance, "demands"), get_value(instance, "demand"), get_value(instance, "load"))
    dist_matrix = pick(get_value(instance, "distances"), get_value(instance, "distance_matrix"), get_value(instance, "matrix"), get_value(instance, "costs"))

    def norm_keys(keys):
        out = []
        seen = set()
        for k in keys:
            if k != depot and k not in seen:
                seen.add(k)
                out.append(k)
        return out

    customers = []
    if isinstance(demands, dict):
        customers = norm_keys(demands.keys())
    elif isinstance(coords, dict):
        customers = norm_keys(coords.keys())
    elif is_seq(demands):
        customers = [i for i in range(len(demands)) if i != depot]
    elif is_seq(coords):
        customers = [i for i in range(len(coords)) if i != depot]
    elif is_seq(dist_matrix):
        customers = [i for i in range(len(dist_matrix)) if i != depot]

    def demand_of(c):
        if isinstance(demands, dict):
            return demands[c] if c in demands else 0
        if is_seq(demands) and isinstance(c, int) and 0 <= c < len(demands):
            return demands[c]
        return 0

    def coord_of(c):
        if isinstance(coords, dict):
            return coords[c] if c in coords else None
        if is_seq(coords) and isinstance(c, int) and 0 <= c < len(coords):
            return coords[c]
        return None

    def dist(a, b):
        if a == b:
            return 0
        if is_seq(dist_matrix) and isinstance(a, int) and isinstance(b, int):
            try:
                return dist_matrix[a][b]
            except Exception:
                pass
        pa = coord_of(a)
        pb = coord_of(b)
        if pa is not None and pb is not None:
            dx = pa[0] - pb[0]
            dy = pa[1] - pb[1]
            return dx * dx + dy * dy
        if isinstance(a, int) and isinstance(b, int):
            return abs(a - b)
        return 1

    unserved = set(customers)
    routes = []

    while unserved:
        route = []
        load = 0
        cur = depot
        while True:
            best = None
            best_key = None
            for c in unserved:
                d = demand_of(c)
                if load + d > capacity:
                    continue
                key = (dist(cur, c), d, c)
                if best is None or key < best_key:
                    best = c
                    best_key = key
            if best is None:
                break
            route.append(best)
            unserved.remove(best)
            load += demand_of(best)
            cur = best

        if not route:
            best = None
            best_key = None
            for c in unserved:
                key = (demand_of(c), dist(depot, c), c)
                if best is None or key < best_key:
                    best = c
                    best_key = key
            route = [best]
            unserved.remove(best)

        routes.append(route)

    def route_load(route):
        s = 0
        for c in route:
            s += demand_of(c)
        return s

    def best_insertion_pos(route, c):
        best_pos = 0
        best_delta = None
        for i in range(len(route) + 1):
            left = depot if i == 0 else route[i - 1]
            right = depot if i == len(route) else route[i]
            delta = dist(left, c) + dist(c, right) - dist(left, right)
            if best_delta is None or delta < best_delta or (delta == best_delta and i < best_pos):
                best_delta = delta
                best_pos = i
        return best_pos, best_delta

    def two_opt(route):
        n = len(route)
        if n < 4:
            return route
        improved = True
        while improved:
            improved = False
            for i in range(n - 2):
                a = depot if i == 0 else route[i - 1]
                b = route[i]
                for j in range(i + 2, n):
                    c = route[j - 1]
                    d = depot if j == n else route[j]
                    if dist(a, c) + dist(b, d) < dist(a, b) + dist(c, d):
                        route[i:j] = reversed(route[i:j])
                        improved = True
                        break
                if improved:
                    break
        return route

    for i in range(len(routes)):
        routes[i] = two_opt(routes[i][:])

    changed = True
    while changed:
        changed = False

        for i in range(len(routes)):
            ri = routes[i]
            li = route_load(ri)
            for pos in range(len(ri)):
                c = ri[pos]
                dc = demand_of(c)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    if route_load(rj) + dc > capacity:
                        continue
                    a = depot if pos == 0 else ri[pos - 1]
                    b = depot if pos == len(ri) - 1 else ri[pos + 1]
                    rem = dist(a, c) + dist(c, b) - dist(a, b)
                    ins_pos, ins = best_insertion_pos(rj, c)
                    if ins - rem < 0:
                        new_ri = ri[:pos] + ri[pos + 1:]
                        new_rj = rj[:ins_pos] + [c] + rj[ins_pos:]
                        routes[i] = new_ri
                        routes[j] = new_rj
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break

        if changed:
            for i in range(len(routes)):
                routes[i] = two_opt(routes[i][:])
            continue

        for i in range(len(routes)):
            ri = routes[i]
            li = route_load(ri)
            for j in range(i + 1, len(routes)):
                rj = routes[j]
                lj = route_load(rj)
                for ai, a in enumerate(ri):
                    da = demand_of(a)
                    for bi, b in enumerate(rj):
                        db = demand_of(b)
                        if li - da + db > capacity or lj - db + da > capacity:
                            continue
                        ai_l = depot if ai == 0 else ri[ai - 1]
                        ai_r = depot if ai == len(ri) - 1 else ri[ai + 1]
                        bi_l = depot if bi == 0 else rj[bi - 1]
                        bi_r = depot if bi == len(rj) - 1 else rj[bi + 1]
                        before = dist(ai_l, a) + dist(a, ai_r) + dist(bi_l, b) + dist(b, bi_r)
                        after = dist(ai_l, b) + dist(b, ai_r) + dist(bi_l, a) + dist(a, bi_r)
                        if after < before:
                            ri2 = ri[:]
                            rj2 = rj[:]
                            ri2[ai] = b
                            rj2[bi] = a
                            routes[i] = ri2
                            routes[j] = rj2
                            changed = True
                            break
                    if changed:
                        break
                if changed:
                    break
            if changed:
                break

        if changed:
            for i in range(len(routes)):
                routes[i] = two_opt(routes[i][:])

    seen = set()
    cleaned = []
    for r in routes:
        rr = []
        for c in r:
            if c != depot and c not in seen:
                seen.add(c)
                rr.append(c)
        if rr:
            cleaned.append(rr)

    missing = [c for c in customers if c not in seen]
    for c in missing:
        placed = False
        for r in cleaned:
            if route_load(r) + demand_of(c) <= capacity:
                pos, _ = best_insertion_pos(r, c)
                r.insert(pos, c)
                placed = True
                break
        if not placed:
            cleaned.append([c])

    return cleaned
