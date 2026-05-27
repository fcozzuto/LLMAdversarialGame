def solve_cvrp(instance):
    def get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj[key] if key in obj else default
        try:
            return obj.__dict__[key]
        except:
            pass
        try:
            return obj[key]
        except:
            pass
        try:
            return object.__getattribute__(obj, key)
        except:
            return default

    capacity = get(instance, "capacity", None)
    if capacity is None:
        capacity = get(instance, "vehicle_capacity", None)

    demands = get(instance, "demands", None)
    if demands is None:
        demands = get(instance, "demand", None)
    if demands is None:
        demands = []

    dist = get(instance, "distance_matrix", None)
    if dist is None:
        dist = get(instance, "distances", None)

    coords = get(instance, "coordinates", None)
    if coords is None:
        coords = get(instance, "coords", None)

    depot = get(instance, "depot", 0)
    if isinstance(depot, (list, tuple)):
        depot = depot[0] if depot else 0

    n = 0
    if demands:
        n = len(demands)
    elif dist is not None:
        n = len(dist)
    elif coords is not None:
        n = len(coords)

    customers = [i for i in range(n) if i != depot]

    if capacity is None:
        capacity = 0
        for i in customers:
            if i < len(demands):
                capacity += demands[i]

    def d(a, b):
        if dist is not None:
            return dist[a][b]
        ax, ay = coords[a]
        bx, by = coords[b]
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    def route_load(route):
        s = 0
        for c in route:
            s += demands[c]
        return s

    def route_cost(route):
        if not route:
            return 0
        c = d(depot, route[0])
        for i in range(len(route) - 1):
            c += d(route[i], route[i + 1])
        c += d(route[-1], depot)
        return c

    remaining = {}
    for c in customers:
        remaining[c] = True

    if coords is not None:
        dx, dy = coords[depot]
        ordered = sorted(customers, key=lambda i: ((coords[i][0] - dx) ** 2 + (coords[i][1] - dy) ** 2, demands[i] if i < len(demands) else 0, i))
    else:
        ordered = sorted(customers, key=lambda i: (demands[i] if i < len(demands) else 0, i))

    routes = []

    while remaining:
        seed = None
        best_key = None
        for c in ordered:
            if c not in remaining:
                continue
            key = (d(depot, c), demands[c] if c < len(demands) else 0, c)
            if best_key is None or key < best_key:
                best_key = key
                seed = c

        if seed is None:
            break

        route = [seed]
        del remaining[seed]
        load = demands[seed] if seed < len(demands) else 0

        while True:
            best_c = None
            best_pos = None
            best_key = None

            for c in ordered:
                if c not in remaining:
                    continue
                dem = demands[c] if c < len(demands) else 0
                if load + dem > capacity:
                    continue

                best_delta_c = None
                best_pos_c = 0
                for idx in range(len(route) + 1):
                    prev = depot if idx == 0 else route[idx - 1]
                    nxt = depot if idx == len(route) else route[idx]
                    delta = d(prev, c) + d(c, nxt) - d(prev, nxt)
                    if best_delta_c is None or delta < best_delta_c or (delta == best_delta_c and idx < best_pos_c):
                        best_delta_c = delta
                        best_pos_c = idx

                key = (best_delta_c, dem, c, best_pos_c)
                if best_key is None or key < best_key:
                    best_key = key
                    best_c = c
                    best_pos = best_pos_c

            if best_c is None:
                break

            route.insert(best_pos, best_c)
            del remaining[best_c]
            load += demands[best_c] if best_c < len(demands) else 0

        routes.append(route)

    seen = {}
    final_routes = []
    for r in routes:
        nr = []
        for c in r:
            if c != depot and c not in seen:
                seen[c] = True
                nr.append(c)
        if nr:
            final_routes.append(nr)

    for c in customers:
        if c in seen:
            continue
        placed = False
        best_r = None
        best_pos = None
        best_delta = None
        for ri in range(len(final_routes)):
            r = final_routes[ri]
            if route_load(r) + demands[c] > capacity:
                continue
            for idx in range(len(r) + 1):
                prev = depot if idx == 0 else r[idx - 1]
                nxt = depot if idx == len(r) else r[idx]
                delta = d(prev, c) + d(c, nxt) - d(prev, nxt)
                if best_delta is None or delta < best_delta or (delta == best_delta and (ri, idx) < (best_r, best_pos)):
                    best_delta = delta
                    best_r = ri
                    best_pos = idx
        if best_r is not None:
            final_routes[best_r].insert(best_pos, c)
            seen[c] = True
            placed = True
        if not placed:
            final_routes.append([c])
            seen[c] = True

    improved = True
    while improved:
        improved = False

        # relocate
        best_move = None
        best_gain = 0
        for i in range(len(final_routes)):
            r1 = final_routes[i]
            for p in range(len(r1)):
                c = r1[p]
                dem_c = demands[c]
                for j in range(len(final_routes)):
                    if i == j:
                        continue
                    r2 = final_routes[j]
                    if route_load(r2) + dem_c > capacity:
                        continue
                    a = depot if p == 0 else r1[p - 1]
                    b = depot if p == len(r1) - 1 else r1[p + 1]
                    removed = d(a, c) + d(c, b) - d(a, b)
                    for q in range(len(r2) + 1):
                        x = depot if q == 0 else r2[q - 1]
                        y = depot if q == len(r2) else r2[q]
                        added = d(x, c) + d(c, y) - d(x, y)
                        gain = removed - added
                        if gain > best_gain:
                            best_gain = gain
                            best_move = (i, p, j, q)

        if best_move is not None:
            i, p, j, q = best_move
            c = final_routes[i][p]
            del final_routes[i][p]
            if i == j and q > p:
                q -= 1
            final_routes[j].insert(q, c)
            if not final_routes[i]:
                del final_routes[i]
            improved = True
            continue

        # 2-opt within routes
        for r in final_routes:
            m = len(r)
            if m < 4:
                continue
            best_i = None
            best_k = None
            best_gain = 0
            for i in range(m - 1):
                a = depot if i == 0 else r[i - 1]
                b = r[i]
                for k in range(i + 1, m):
                    c = r[k]
                    e = depot if k == m - 1 else r[k + 1]
                    gain = (d(a, b) + d(c, e)) - (d(a, c) + d(b, e))
                    if gain > best_gain:
                        best_gain = gain
                        best_i = i
                        best_k = k
            if best_i is not None:
                r[best_i:best_k + 1] = r[best_i:best_k + 1][::-1]
                improved = True
                break

    cleaned = []
    seen = {}
    for r in final_routes:
        nr = []
        load = 0
        for c in r:
            if c == depot or c in seen:
                continue
            seen[c] = True
            nr.append(c)
            load += demands[c]
        if nr:
            cleaned.append(nr)

    for c in customers:
        if c in seen:
            continue
        placed = False
        for r in cleaned:
            if route_load(r) + demands[c] <= capacity:
                r.append(c)
                placed = True
                break
        if not placed:
            cleaned.append([c])

    return cleaned
