def solve_cvrp(instance):
    def get_field(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        d = None
        try:
            d = obj.__dict__
        except Exception:
            d = None
        if isinstance(d, dict):
            return d.get(key, default)
        return default

    depot = get_field(instance, "depot", 0)
    capacity = get_field(instance, "capacity", get_field(instance, "vehicle_capacity", None))

    customers_raw = get_field(instance, "customers", None)
    demands_raw = get_field(instance, "demands", None)
    coords_raw = get_field(instance, "coords", get_field(instance, "locations", None))
    dist_matrix = get_field(instance, "distance_matrix", get_field(instance, "distances", None))

    demand = {}
    coord = {}

    if customers_raw is not None:
        if isinstance(customers_raw, dict):
            for cid, data in customers_raw.items():
                if isinstance(data, dict):
                    demand[cid] = data.get("demand", data.get("d", 0))
                    if "coord" in data:
                        coord[cid] = tuple(data["coord"])
                    elif "location" in data:
                        coord[cid] = tuple(data["location"])
                elif isinstance(data, (list, tuple)):
                    if len(data) >= 2:
                        demand[cid] = data[1]
                    else:
                        demand[cid] = 0
        else:
            for item in customers_raw:
                if isinstance(item, dict):
                    cid = item.get("id", item.get("customer_id"))
                    if cid is None:
                        continue
                    demand[cid] = item.get("demand", item.get("d", 0))
                    if "coord" in item:
                        coord[cid] = tuple(item["coord"])
                    elif "location" in item:
                        coord[cid] = tuple(item["location"])
                elif isinstance(item, (list, tuple)):
                    if len(item) >= 2:
                        cid = item[0]
                        demand[cid] = item[1]
    elif demands_raw is not None:
        if isinstance(demands_raw, dict):
            for cid, d in demands_raw.items():
                demand[cid] = d
        else:
            for cid, d in enumerate(demands_raw):
                if cid != depot:
                    demand[cid] = d

    if coords_raw is not None:
        if isinstance(coords_raw, dict):
            for cid, p in coords_raw.items():
                coord[cid] = tuple(p)
        else:
            for cid, p in enumerate(coords_raw):
                coord[cid] = tuple(p)

    if depot not in coord:
        dep = get_field(instance, "depot_coord", None)
        if dep is not None:
            coord[depot] = tuple(dep)

    customers = [cid for cid in demand.keys() if cid != depot]

    if capacity is None:
        total_demand = 0
        for cid in customers:
            total_demand += demand.get(cid, 0)
        capacity = max(total_demand, 1)

    dist_cache = {}

    def dist(a, b):
        if a == b:
            return 0.0
        key = (a, b)
        if key in dist_cache:
            return dist_cache[key]
        key2 = (b, a)
        if key2 in dist_cache:
            return dist_cache[key2]
        if dist_matrix is not None:
            v = None
            try:
                v = dist_matrix[a][b]
            except Exception:
                try:
                    v = dist_matrix[a - 1][b - 1]
                except Exception:
                    v = None
            if v is not None:
                dist_cache[key] = v
                return v
        pa = coord.get(a, None)
        pb = coord.get(b, None)
        if pa is None or pb is None:
            v = abs(a - b)
        else:
            dx = pa[0] - pb[0]
            dy = pa[1] - pb[1]
            v = (dx * dx + dy * dy) ** 0.5
        dist_cache[key] = v
        return v

    def route_demand(route):
        s = 0
        for c in route:
            s += demand.get(c, 0)
        return s

    def route_cost(route):
        if not route:
            return 0.0
        c = dist(depot, route[0])
        for i in range(len(route) - 1):
            c += dist(route[i], route[i + 1])
        c += dist(route[-1], depot)
        return c

    def angle_key(cid):
        p = coord.get(cid, None)
        d = coord.get(depot, (0.0, 0.0))
        if p is None:
            return (0.0, float(cid))
        return ((p[1] - d[1]), (p[0] - d[0]))

    unassigned = set(customers)
    routes = []
    ordered = sorted(customers, key=lambda c: (-demand.get(c, 0), angle_key(c)[0], angle_key(c)[1], c))

    while unassigned:
        seed = None
        for c in ordered:
            if c in unassigned:
                seed = c
                break
        if seed is None:
            break
        route = [seed]
        unassigned.remove(seed)
        load = demand.get(seed, 0)

        while True:
            last = route[-1]
            best = None
            best_key = None
            for c in unassigned:
                d = demand.get(c, 0)
                if load + d > capacity:
                    continue
                key = (dist(last, c), dist(depot, c), -d, c)
                if best is None or key < best_key:
                    best = c
                    best_key = key
            if best is None:
                break
            route.append(best)
            unassigned.remove(best)
            load += demand.get(best, 0)

        routes.append(route)

    def two_opt_route(route):
        if len(route) < 4:
            return route[:]
        route = route[:]
        improved = True
        while improved:
            improved = False
            base = route_cost(route)
            n = len(route)
            for i in range(n - 2):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    cand = route[:i + 1] + route[i + 1:j + 1][::-1] + route[j + 1:]
                    if route_cost(cand) + 1e-12 < base:
                        route = cand
                        improved = True
                        break
                if improved:
                    break
        return route

    for idx in range(len(routes)):
        routes[idx] = two_opt_route(routes[idx])

    changed = True
    while changed:
        changed = False
        for i in range(len(routes)):
            ri = routes[i]
            if not ri:
                continue
            ci = route_cost(ri)
            for pos in range(len(ri)):
                c = ri[pos]
                dc = demand.get(c, 0)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    if route_demand(rj) + dc > capacity:
                        continue
                    old_cost = ci + route_cost(rj)
                    new_ri = ri[:pos] + ri[pos + 1:]
                    for ins in range(len(rj) + 1):
                        new_rj = rj[:ins] + [c] + rj[ins:]
                        a = two_opt_route(new_ri) if new_ri else []
                        b = two_opt_route(new_rj)
                        new_cost = route_cost(a) + route_cost(b)
                        if new_cost + 1e-12 < old_cost:
                            routes[i] = a
                            routes[j] = b
                            changed = True
                            break
                    if changed:
                        break
                if changed:
                    break
            if changed:
                break

    routes = [r for r in routes if r]

    seen = set()
    final_routes = []
    for r in routes:
        nr = []
        for c in r:
            if c != depot and c not in seen:
                nr.append(c)
                seen.add(c)
        if nr:
            final_routes.append(nr)

    missing = [c for c in customers if c not in seen]
    for c in missing:
        placed = False
        for r in final_routes:
            if route_demand(r) + demand.get(c, 0) <= capacity:
                best_pos = 0
                best_delta = None
                base = route_cost(r)
                for pos in range(len(r) + 1):
                    cand = r[:pos] + [c] + r[pos:]
                    delta = route_cost(cand) - base
                    if best_delta is None or delta < best_delta or (delta == best_delta and pos < best_pos):
                        best_pos = pos
                        best_delta = delta
                r[:] = r[:best_pos] + [c] + r[best_pos:]
                placed = True
                break
        if not placed:
            final_routes.append([c])

    for idx in range(len(final_routes)):
        final_routes[idx] = two_opt_route(final_routes[idx])

    return final_routes
