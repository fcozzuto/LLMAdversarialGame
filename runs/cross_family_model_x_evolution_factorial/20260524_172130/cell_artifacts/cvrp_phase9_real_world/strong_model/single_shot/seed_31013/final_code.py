def solve_cvrp(instance):
    def get_capacity(inst):
        for k in ("capacity", "vehicle_capacity", "cap"):
            if k in inst:
                return inst[k]
        return 0

    def get_depot_id(inst):
        for k in ("depot_id", "depot", "depot_index"):
            if k in inst:
                d = inst[k]
                if isinstance(d, dict):
                    for kk in ("id", "index", "node", "customer_id"):
                        if kk in d:
                            return d[kk]
                return d
        return 0

    def extract_customers(inst, depot_id):
        if "customers" in inst and inst["customers"] is not None:
            cs = inst["customers"]
            if isinstance(cs, dict):
                ids = list(cs.keys())
            else:
                ids = list(cs)
        elif "demands" in inst and isinstance(inst["demands"], dict):
            ids = [k for k in inst["demands"].keys() if k != depot_id]
        elif "demand" in inst and isinstance(inst["demand"], dict):
            ids = [k for k in inst["demand"].keys() if k != depot_id]
        else:
            ids = []
            n = None
            for k in ("n", "num_nodes", "size", "num_customers"):
                if k in inst:
                    n = inst[k]
                    break
            if n is not None:
                ids = [i for i in range(n) if i != depot_id]
        ids = list(dict.fromkeys(ids))
        ids.sort()
        return ids

    def get_demands(inst, depot_id):
        dem = {}
        for k in ("demands", "demand"):
            if k in inst and isinstance(inst[k], dict):
                dem = dict(inst[k])
                break
        if depot_id not in dem:
            dem[depot_id] = 0
        return dem

    def dist(a, b):
        if dm is not None:
            try:
                return dm[a][b]
            except Exception:
                try:
                    return dm[b][a]
                except Exception:
                    pass
        pa = coords.get(a)
        pb = coords.get(b)
        if pa is None or pb is None:
            return 0
        dx = pa[0] - pb[0]
        dy = pa[1] - pb[1]
        return (dx * dx + dy * dy) ** 0.5

    def route_load(route):
        s = 0
        for c in route:
            s += demands.get(c, 0)
        return s

    def route_cost(route):
        if not route:
            return 0
        c = dist(depot, route[0])
        for i in range(len(route) - 1):
            c += dist(route[i], route[i + 1])
        c += dist(route[-1], depot)
        return c

    def total_cost(routes_):
        return sum(route_cost(r) for r in routes_)

    def best_insertion_pos(route, cust):
        best_pos = 0
        best_delta = None
        if not route:
            return 0, dist(depot, cust) * 2
        prev = depot
        for i in range(len(route) + 1):
            nxt = depot if i == len(route) else route[i]
            delta = dist(prev, cust) + dist(cust, nxt) - dist(prev, nxt)
            if best_delta is None or delta < best_delta - 1e-12 or (abs(delta - best_delta) <= 1e-12 and i < best_pos):
                best_delta = delta
                best_pos = i
            if i < len(route):
                prev = route[i]
        return best_pos, best_delta

    def two_opt_route(route):
        if len(route) < 4:
            return route
        improved = True
        while improved:
            improved = False
            best_i = best_j = None
            best_gain = 0
            n = len(route)
            for i in range(n - 2):
                a = depot if i == 0 else route[i - 1]
                b = route[i]
                for j in range(i + 1, n - 1):
                    c = route[j]
                    d = depot if j == n - 1 else route[j + 1]
                    gain = (dist(a, b) + dist(c, d)) - (dist(a, c) + dist(b, d))
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best_i, best_j = i, j
            if best_gain > 1e-12:
                route = route[:best_i] + list(reversed(route[best_i:best_j + 1])) + route[best_j + 1:]
                improved = True
        return route

    def relocate_between(routes_):
        improved = True
        while improved:
            improved = False
            base_cost = total_cost(routes_)
            best = None
            for r1 in range(len(routes_)):
                for i, cust in enumerate(routes_[r1]):
                    d = demands.get(cust, 0)
                    for r2 in range(len(routes_)):
                        if r1 == r2:
                            continue
                        if route_load(routes_[r2]) + d > capacity:
                            continue
                        for pos in range(len(routes_[r2]) + 1):
                            new_r1 = routes_[r1][:i] + routes_[r1][i + 1:]
                            new_r2 = routes_[r2][:pos] + [cust] + routes_[r2][pos:]
                            cand = routes_[:]
                            cand[r1] = new_r1
                            cand[r2] = new_r2
                            c = total_cost(cand)
                            if c + 1e-12 < base_cost and (best is None or c < best[0] - 1e-12):
                                best = (c, r1, r2, i, pos)
            if best is not None:
                _, r1, r2, i, pos = best
                cust = routes_[r1][i]
                routes_[r1] = routes_[r1][:i] + routes_[r1][i + 1:]
                routes_[r2] = routes_[r2][:pos] + [cust] + routes_[r2][pos:]
                routes_ = [r for r in routes_ if r]
                improved = True
        return routes_

    def swap_between(routes_):
        improved = True
        while improved:
            improved = False
            base_cost = total_cost(routes_)
            best = None
            for r1 in range(len(routes_)):
                for i, a in enumerate(routes_[r1]):
                    da = demands.get(a, 0)
                    for r2 in range(r1 + 1, len(routes_)):
                        for j, b in enumerate(routes_[r2]):
                            db = demands.get(b, 0)
                            if route_load(routes_[r1]) - da + db > capacity:
                                continue
                            if route_load(routes_[r2]) - db + da > capacity:
                                continue
                            cand = routes_[:]
                            nr1 = routes_[r1][:]
                            nr2 = routes_[r2][:]
                            nr1[i], nr2[j] = b, a
                            cand[r1] = nr1
                            cand[r2] = nr2
                            c = total_cost(cand)
                            if c + 1e-12 < base_cost and (best is None or c < best[0] - 1e-12):
                                best = (c, r1, r2, i, j)
            if best is not None:
                _, r1, r2, i, j = best
                routes_[r1][i], routes_[r2][j] = routes_[r2][j], routes_[r1][i]
                improved = True
        return routes_

    depot = get_depot_id(instance)
    capacity = get_capacity(instance)
    demands = get_demands(instance, depot)
    customers = extract_customers(instance, depot)
    coords = {}
    if "coordinates" in instance and isinstance(instance["coordinates"], dict):
        coords = instance["coordinates"]
    elif "coords" in instance and isinstance(instance["coords"], dict):
        coords = instance["coords"]
    elif "positions" in instance and isinstance(instance["positions"], dict):
        coords = instance["positions"]
    dm = None
    for k in ("distance_matrix", "distances", "distance"):
        if k in instance:
            dm = instance[k]
            break

    remaining = customers[:]
    remaining.sort()
    routes = []
    while remaining:
        route = []
        load = 0
        current = depot
        while True:
            best_c = None
            best_key = None
            for c in remaining:
                d = demands.get(c, 0)
                if load + d > capacity:
                    continue
                key = (dist(current, c), d, c)
                if best_key is None or key < best_key:
                    best_key = key
                    best_c = c
            if best_c is None:
                break
            route.append(best_c)
            load += demands.get(best_c, 0)
            remaining.remove(best_c)
            current = best_c
        if not route and remaining:
            c = remaining.pop(0)
            route = [c]
        routes.append(route)

    routes = [r for r in routes if r]

    # Repair any missing customers
    visited = {}
    for r in routes:
        for c in r:
            visited[c] = visited.get(c, 0) + 1
    for c in customers:
        if visited.get(c, 0) == 0:
            best_route = None
            best_pos = None
            best_delta = None
            for ridx, r in enumerate(routes):
                if route_load(r) + demands.get(c, 0) > capacity:
                    continue
                pos, delta = best_insertion_pos(r, c)
                if best_delta is None or delta < best_delta - 1e-12:
                    best_delta = delta
                    best_route = ridx
                    best_pos = pos
            if best_route is None:
                routes.append([c])
            else:
                routes[best_route] = routes[best_route][:best_pos] + [c] + routes[best_route][best_pos:]

    # Local search
    routes = [two_opt_route(r) for r in routes]
    routes = relocate_between(routes)
    routes = swap_between(routes)
    routes = [two_opt_route(r) for r in routes]
    routes = [r for r in routes if r]

    # Final sanity: ensure all customers exactly once; if duplicates/missing, rebuild deterministically
    seen = {}
    for r in routes:
        for c in r:
            seen[c] = seen.get(c, 0) + 1
    ok = True
    for c in customers:
        if seen.get(c, 0) != 1:
            ok = False
