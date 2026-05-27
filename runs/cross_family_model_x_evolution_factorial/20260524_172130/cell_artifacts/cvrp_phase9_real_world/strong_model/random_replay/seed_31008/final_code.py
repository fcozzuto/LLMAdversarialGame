def solve_cvrp(instance):
    def get_dict(*keys):
        if isinstance(instance, dict):
            for k in keys:
                if k in instance:
                    return instance[k]
        return None

    depot = 0
    dpt = get_dict("depot", "depot_id", "start_depot", "origin")
    if isinstance(dpt, dict) and "id" in dpt:
        depot = dpt["id"]
    elif dpt is not None:
        depot = dpt

    capacity = get_dict("capacity", "vehicle_capacity", "Q")
    demands = get_dict("demands", "demand") or {}
    coords = get_dict("coords", "coordinates", "locations", "xy")
    dm = get_dict("distance_matrix", "distances")

    def node_ids():
        if isinstance(instance, dict):
            for k in ("customers", "nodes"):
                if k in instance:
                    v = instance[k]
                    if isinstance(v, dict):
                        return [x for x in v.keys() if x != depot]
                    return [x for x in v if x != depot]
        if isinstance(demands, dict) and demands:
            return [x for x in demands.keys() if x != depot]
        if isinstance(dm, list):
            return [i for i in range(len(dm)) if i != depot]
        if isinstance(dm, dict) and dm:
            ids = set(dm.keys())
            for v in dm.values():
                if isinstance(v, dict):
                    ids.update(v.keys())
            ids.discard(depot)
            return sorted(ids)
        return []

    customers = node_ids()

    def coord(i):
        if coords is None:
            return None
        if isinstance(coords, dict):
            v = coords.get(i)
        else:
            v = coords[i] if isinstance(i, int) and 0 <= i < len(coords) else None
        if isinstance(v, dict) and "x" in v and "y" in v:
            return (v["x"], v["y"])
        return v

    def dist(a, b):
        if a == b:
            return 0
        if isinstance(dm, list):
            try:
                return dm[a][b]
            except Exception:
                pass
        elif isinstance(dm, dict):
            row = dm.get(a)
            if isinstance(row, dict) and b in row:
                return row[b]
        ca, cb = coord(a), coord(b)
        if ca is not None and cb is not None:
            ax, ay = ca[0], ca[1]
            bx, by = cb[0], cb[1]
            return ((ax - bx) * (ax - bx) + (ay - by) * (ay - by)) ** 0.5
        if isinstance(a, int) and isinstance(b, int):
            return abs(a - b)
        return 1

    def dem(i):
        if isinstance(demands, dict):
            return demands.get(i, 0)
        if isinstance(demands, list) and isinstance(i, int) and 0 <= i < len(demands):
            return demands[i]
        return 0

    def route_demand(r):
        s = 0
        for c in r:
            s += dem(c)
        return s

    def route_cost(r):
        if not r:
            return 0
        c = dist(depot, r[0]) + dist(r[-1], depot)
        for i in range(len(r) - 1):
            c += dist(r[i], r[i + 1])
        return c

    def best_insert_pos(route, c):
        if not route:
            return dist(depot, c) * 2, 0
        best = dist(depot, c) + dist(c, depot)
        pos = 0
        x = dist(depot, c) + dist(c, route[0]) - dist(depot, route[0])
        if x < best:
            best, pos = x, 0
        for i in range(len(route) - 1):
            x = dist(route[i], c) + dist(c, route[i + 1]) - dist(route[i], route[i + 1])
            if x < best:
                best, pos = x, i + 1
        x = dist(route[-1], c) + dist(c, depot) - dist(route[-1], depot)
        if x < best:
            best, pos = x, len(route)
        return best, pos

    def two_opt(route):
        n = len(route)
        if n < 4:
            return route
        improved = True
        while improved:
            improved = False
            base = route_cost(route)
            best_gain = 0
            best_i = best_j = -1
            for i in range(n - 2):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    cand = route[:i + 1] + route[i + 1:j + 1][::-1] + route[j + 1:]
                    gain = base - route_cost(cand)
                    if gain > best_gain:
                        best_gain = gain
                        best_i, best_j = i, j
            if best_gain > 0:
                route = route[:best_i + 1] + route[best_i + 1:best_j + 1][::-1] + route[best_j + 1:]
                improved = True
        return route

    unassigned = set(customers)
    routes = []

    while unassigned:
        seed = None
        seed_key = None
        for c in unassigned:
            key = (-dem(c), -dist(depot, c), c)
            if seed is None or key < seed_key:
                seed, seed_key = c, key
        route = [seed]
        load = dem(seed)
        unassigned.remove(seed)
        while True:
            best_key = None
            best_c = None
            best_p = 0
            for c in unassigned:
                if capacity is not None and load + dem(c) > capacity:
                    continue
                delta, pos = best_insert_pos(route, c)
                key = (delta, -dem(c), dist(depot, c), c)
                if best_key is None or key < best_key:
                    best_key, best_c, best_p = key, c, pos
            if best_c is None:
                break
            route.insert(best_p, best_c)
            load += dem(best_c)
            unassigned.remove(best_c)
        if route_cost(route[::-1]) < route_cost(route):
            route = route[::-1]
        routes.append(two_opt(route))

    changed = True
    rounds = 0
    while changed and rounds < 15:
        changed = False
        rounds += 1
        loads = [route_demand(r) for r in routes]
        costs = [route_cost(r) for r in routes]
        best = None
        best_delta = 0
        for i in range(len(routes)):
            ri = routes[i]
            for p, c in enumerate(ri):
                dc = dem(c)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    if capacity is not None and loads[j] + dc > capacity:
                        continue
                    rem = ri[:p] + ri[p + 1:]
                    ins_delta, pos = best_insert_pos(routes[j], c)
                    new_cost = (route_cost(rem) if rem else 0) + (costs[j] + ins_delta)
                    delta = new_cost - costs[i] - costs[j]
                    if delta < best_delta:
                        best_delta = delta
                        best = (i, j, p, pos)
        if best is not None:
            i, j, p, pos = best
            c = routes[i][p]
            routes[i].pop(p)
            routes[j].insert(pos, c)
            if routes[i]:
                routes[i] = two_opt(routes[i])
            routes[j] = two_opt(routes[j])
            if not routes[i]:
                routes.pop(i)
            changed = True

    cleaned = []
    for r in routes:
        rr = [c for c in r if c != depot]
        if rr:
            cleaned.append(rr)
    return cleaned
