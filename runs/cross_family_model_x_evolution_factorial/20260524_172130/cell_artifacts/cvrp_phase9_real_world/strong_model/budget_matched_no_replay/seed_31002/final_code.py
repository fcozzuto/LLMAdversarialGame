def solve_cvrp(instance):
    def get_first(*keys, default=None):
        for k in keys:
            if isinstance(instance, dict) and k in instance:
                return instance[k]
        return default

    def as_dict(x):
        return x if isinstance(x, dict) else None

    def get_capacity():
        cap = get_first("capacity", "vehicle_capacity", "cap")
        if cap is not None:
            return cap
        vc = get_first("vehicle", "vehicles")
        if isinstance(vc, dict):
            for k in ("capacity", "cap"):
                if k in vc:
                    return vc[k]
        return None

    def get_depot_id():
        dep = get_first("depot", "depot_id", "root", default=0)
        if isinstance(dep, dict):
            return dep.get("id", dep.get("index", 0))
        return dep if dep is not None else 0

    def get_coords():
        c = get_first("coords", "coordinates", "locations", "points", "xy")
        if c is not None:
            return c
        nodes = get_first("nodes")
        if isinstance(nodes, dict):
            return nodes
        return None

    def get_demands():
        d = get_first("demands", "demand", "loads")
        return d

    def get_distance_matrix():
        dm = get_first("distance_matrix", "distances", "matrix")
        return dm

    depot = get_depot_id()
    cap = get_capacity()
    coords = get_coords()
    demands = get_demands()
    distmat = get_distance_matrix()

    def all_customer_ids():
        ids = []
        if isinstance(instance, dict):
            if "customers" in instance and instance["customers"] is not None:
                for x in instance["customers"]:
                    if x != depot:
                        ids.append(x)
                return ids
            if isinstance(demands, dict):
                for k in demands.keys():
                    if k != depot:
                        ids.append(k)
                if ids:
                    return sorted(ids)
            if isinstance(coords, dict):
                for k in coords.keys():
                    if k != depot:
                        ids.append(k)
                if ids:
                    return sorted(ids)
            n = get_first("n", "size", "num_nodes", "num_customers")
            if isinstance(n, int) and n > 0:
                return [i for i in range(n) if i != depot]
        return ids

    customers = all_customer_ids()

    def demand(i):
        if demands is None:
            return 1
        if isinstance(demands, dict):
            return demands.get(i, 1)
        try:
            return demands[i]
        except Exception:
            return 1

    def coord(i):
        if coords is None:
            return None
        if isinstance(coords, dict):
            return coords.get(i, None)
        try:
            return coords[i]
        except Exception:
            return None

    def dist(a, b):
        if distmat is not None:
            try:
                return distmat[a][b]
            except Exception:
                try:
                    return distmat[a, b]
                except Exception:
                    pass
        pa = coord(a)
        pb = coord(b)
        if pa is not None and pb is not None:
            ax, ay = pa[0], pa[1]
            bx, by = pb[0], pb[1]
            dx = ax - bx
            dy = ay - by
            return (dx * dx + dy * dy) ** 0.5
        return abs(a - b)

    def route_cost(route):
        if not route:
            return 0
        c = dist(depot, route[0])
        for i in range(len(route) - 1):
            c += dist(route[i], route[i + 1])
        c += dist(route[-1], depot)
        return c

    def route_load(route):
        s = 0
        for x in route:
            s += demand(x)
        return s

    def route_savings_insert(route, cust, pos):
        before = depot if pos == 0 else route[pos - 1]
        after = depot if pos == len(route) else route[pos]
        return dist(before, cust) + dist(cust, after) - dist(before, after)

    unserved = set(customers)
    routes = []

    # Constructive: greedy seeded routes by farthest-from-depot / largest demand
    while unserved:
        seed = None
        best_key = None
        for c in unserved:
            key = (demand(c), dist(depot, c), -c)
            if best_key is None or key > best_key:
                best_key = key
                seed = c
        route = [seed]
        load = demand(seed)
        unserved.remove(seed)
        current = seed
        while True:
            best = None
            best_val = None
            for c in unserved:
                dc = demand(c)
                if cap is not None and load + dc > cap:
                    continue
                val = (dist(current, c), -dc, c)
                if best_val is None or val < best_val:
                    best_val = val
                    best = c
            if best is None:
                break
            route.append(best)
            load += demand(best)
            unserved.remove(best)
            current = best
        routes.append(route)

    # Repair/insertion: try to reduce route count by inserting leftovers if any (safety)
    if unserved:
        leftovers = list(unserved)
        unserved.clear()
        for cust in leftovers:
            best_r = None
            best_p = None
            best_delta = None
            for r_idx, route in enumerate(routes):
                if cap is not None and route_load(route) + demand(cust) > cap:
                    continue
                for p in range(len(route) + 1):
                    delta = route_savings_insert(route, cust, p)
                    if best_delta is None or delta < best_delta:
                        best_delta = delta
                        best_r = r_idx
                        best_p = p
            if best_r is None:
                routes.append([cust])
            else:
                routes[best_r].insert(best_p, cust)

    def two_opt(route):
        if len(route) < 4:
            return route
        improved = True
        while improved:
            improved = False
            best_gain = 0
            best_i = best_j = None
            base = route_cost(route)
            n = len(route)
            for i in range(n - 2):
                a = depot if i == 0 else route[i - 1]
                b = route[i]
                for j in range(i + 2, n):
                    c = route[j - 1]
                    d = depot if j == n else route[j]
                    gain = (dist(a, b) + dist(c, d)) - (dist(a, c) + dist(b, d))
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best_i, best_j = i, j
            if best_i is not None:
                route = route[:best_i] + route[best_i:best_j][::-1] + route[best_j:]
                improved = True
        return route

    # Local search: intra-route 2-opt
    routes = [two_opt(r[:]) for r in routes]

    # Inter-route relocate and swap
    changed = True
    while changed:
        changed = False
        # relocate
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j or not routes[i]:
                    continue
                ri = routes[i]
                rj = routes[j]
                loadj = route_load(rj)
                for idx, cust in enumerate(ri):
                    dc = demand(cust)
                    if cap is not None and loadj + dc > cap:
                        continue
                    best_pos = None
                    best_delta = None
                    for p in range(len(rj) + 1):
                        delta = route_savings_insert(rj, cust, p)
                        if best_delta is None or delta < best_delta:
                            best_delta = delta
                            best_pos = p
                    if best_pos is None:
                        continue
                    old_cost = route_cost(ri) + route_cost(rj)
                    new_ri = ri[:idx] + ri[idx + 1:]
                    new_rj = rj[:best_pos] + [cust] + rj[best_pos:]
                    new_cost = route_cost(new_ri) + route_cost(new_rj)
                    if new_cost + 1e-12 < old_cost:
                        routes[i] = new_ri
                        routes[j] = new_rj
                        if routes[i]:
                            routes[i] = two_opt(routes[i])
                        if routes[j]:
                            routes[j] = two_opt(routes[j])
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break

        if changed:
            continue

        # swap between routes
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                ri = routes[i]
                rj = routes[j]
                if not ri or not rj:
                    continue
                li = route_load(ri)
                lj = route_load(rj)
                for a_idx, a in enumerate(ri):
                    da = demand(a)
                    for b_idx, b in enumerate(rj):
                        db = demand(b)
                        ni = li - da + db
                        nj = lj - db + da
