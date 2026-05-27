def solve_cvrp(instance):
    def fetch(obj, names, default=None):
        if isinstance(obj, dict):
            for n in names:
                if n in obj:
                    return obj[n]
        return default

    def is_num(x):
        return isinstance(x, (int, float))

    def key_list(x):
        try:
            return list(x.keys())
        except Exception:
            return []

    capacity = fetch(instance, ["capacity", "vehicle_capacity", "cap"], None)
    depot = fetch(instance, ["depot", "depot_id", "start"], 0)
    coords = fetch(instance, ["coords", "coordinates", "locations", "xy"], None)
    dist = fetch(instance, ["distance_matrix", "dist_matrix", "distance"], None)
    demands = fetch(instance, ["demands", "demand"], None)

    def demand(i):
        if isinstance(demands, dict):
            v = demands.get(i, 0)
            return v if is_num(v) else 0
        if isinstance(demands, (list, tuple)) and 0 <= i < len(demands):
            v = demands[i]
            return v if is_num(v) else 0
        return 0

    def coord(i):
        if isinstance(coords, dict):
            v = coords.get(i)
            if isinstance(v, (list, tuple)) and len(v) >= 2:
                return float(v[0]), float(v[1])
        elif isinstance(coords, (list, tuple)) and 0 <= i < len(coords):
            v = coords[i]
            if isinstance(v, (list, tuple)) and len(v) >= 2:
                return float(v[0]), float(v[1])
        return None

    def d_ij(i, j):
        if isinstance(dist, (list, tuple)) and 0 <= i < len(dist):
            row = dist[i]
            if isinstance(row, (list, tuple)) and 0 <= j < len(row):
                v = row[j]
                if is_num(v):
                    return float(v)
        ci = coord(i)
        cj = coord(j)
        if ci is not None and cj is not None:
            dx = ci[0] - cj[0]
            dy = ci[1] - cj[1]
            return (dx * dx + dy * dy) ** 0.5
        return 0.0 if i == j else 1.0

    def total_demand(nodes):
        s = 0
        for c in nodes:
            s += demand(c)
        return s

    customers = []
    if isinstance(demands, dict):
        customers = [k for k in key_list(demands) if k != depot]
    elif isinstance(demands, (list, tuple)):
        customers = [i for i in range(len(demands)) if i != depot]
    elif isinstance(coords, dict):
        customers = [k for k in key_list(coords) if k != depot]
    elif isinstance(coords, (list, tuple)):
        customers = [i for i in range(len(coords)) if i != depot]
    elif isinstance(dist, (list, tuple)):
        customers = [i for i in range(len(dist)) if i != depot]

    customers = list(customers)
    if capacity is None:
        capacity = max(1, total_demand(customers))

    depot_c = coord(depot)
    if depot_c is None:
        depot_c = (0.0, 0.0)

    def angle_key(i):
        c = coord(i)
        if c is None:
            return (1, i)
        return (0, c[0] - depot_c[0], c[1] - depot_c[1], i)

    ordered = sorted(customers, key=angle_key)
    unvisited = set(customers)
    routes = []

    while unvisited:
        start = None
        best = None
        for c in ordered:
            if c in unvisited:
                k = (d_ij(depot, c), -demand(c), c)
                if best is None or k > best:
                    best = k
                    start = c
        if start is None:
            break
        route = [start]
        unvisited.remove(start)
        load = demand(start)

        while True:
            last = route[-1]
            best_c = None
            best_k = None
            for c in ordered:
                if c not in unvisited:
                    continue
                dc = demand(c)
                if load + dc > capacity:
                    continue
                k = (d_ij(last, c), d_ij(depot, c), dc, c)
                if best_k is None or k < best_k:
                    best_k = k
                    best_c = c
            if best_c is None:
                break
            route.append(best_c)
            unvisited.remove(best_c)
            load += demand(best_c)
        routes.append(route)

    def route_load(r):
        return total_demand(r)

    def route_cost(r):
        if not r:
            return 0.0
        s = d_ij(depot, r[0])
        for i in range(len(r) - 1):
            s += d_ij(r[i], r[i + 1])
        s += d_ij(r[-1], depot)
        return s

    # Clean duplicates if any and reinsert missing.
    seen = set()
    cleaned = []
    for r in routes:
        nr = []
        load = 0
        for c in r:
            if c in seen:
                continue
            dc = demand(c)
            if load + dc <= capacity:
                nr.append(c)
                load += dc
                seen.add(c)
        if nr:
            cleaned.append(nr)
    routes = cleaned

    for c in customers:
        if c in seen:
            continue
        dc = demand(c)
        best_ri = None
        best_pos = None
        best_delta = None
        for ri, r in enumerate(routes):
            if route_load(r) + dc > capacity:
                continue
            for pos in range(len(r) + 1):
                prev = depot if pos == 0 else r[pos - 1]
                nxt = depot if pos == len(r) else r[pos]
                delta = d_ij(prev, c) + d_ij(c, nxt) - d_ij(prev, nxt)
                if best_delta is None or delta < best_delta:
                    best_delta = delta
                    best_ri = ri
                    best_pos = pos
        if best_ri is None:
            routes.append([c])
        else:
            routes[best_ri] = routes[best_ri][:best_pos] + [c] + routes[best_ri][best_pos:]
        seen.add(c)

    improved = True
    while improved:
        improved = False

        for idx, r in enumerate(routes):
            n = len(r)
            if n < 4:
                continue
            base = route_cost(r)
            best_i = best_j = None
            best_gain = 0.0
            for i in range(n - 2):
                a = depot if i == 0 else r[i - 1]
                b = r[i]
                for j in range(i + 2, n):
                    c1 = r[j]
                    d1 = depot if j + 1 == n else r[j + 1]
                    old = d_ij(a, b) + d_ij(c1, d1)
                    new = d_ij(a, c1) + d_ij(b, d1)
                    gain = old - new
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best_i, best_j = i, j
            if best_i is not None:
                routes[idx] = r[:best_i] + list(reversed(r[best_i:best_j + 1])) + r[best_j + 1:]
                improved = True

        if improved:
            continue

        for i in range(len(routes)):
            if improved:
                break
            for pos in range(len(routes[i])):
                c = routes[i][pos]
                dc = demand(c)
                ri = routes[i][:pos] + routes[i][pos + 1:]
                if not ri:
                    continue
                old_i = route_cost(routes[i])
                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    if route_load(rj) + dc > capacity:
                        continue
                    best_pos = None
                    best_delta = None
                    for k in range(len(rj) + 1):
                        prev = depot if k == 0 else rj[k - 1]
                        nxt = depot if k == len(rj) else rj[k]
                        delta = d_ij(prev, c) + d_ij(c, nxt) - d_ij(prev, nxt)
                        if best_delta is None or delta < best_delta:
                            best_delta = delta
                            best_pos = k
                    if best_pos is None:
                        continue
                    new_j = rj[:best_pos] + [c] + rj[best_pos:]
                    if route_cost(ri) + route_cost(new_j) + 1e-12 < old_i + route_cost(rj):
                        routes[i] = ri
                        routes[j] = new_j
                        improved = True
                        break
                if improved:
                    break

    final_routes = []
    seen = set()
    for r in routes:
        nr = []
        load = 0
        for c in r:
            if c in seen:
                continue
            dc = demand(c)
            if load + dc <= capacity:
                nr.append(c)
                load += dc
                seen.add(c)
        if nr:
            final_routes.append(nr)

    for c in customers:
        if c not in seen:
            final_routes.append([c])
            seen.add(c)

    return final_routes
