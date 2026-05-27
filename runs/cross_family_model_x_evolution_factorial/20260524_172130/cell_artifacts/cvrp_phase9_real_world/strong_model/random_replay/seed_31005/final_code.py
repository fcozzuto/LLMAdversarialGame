def solve_cvrp(instance):
    def get_value(obj, keys, default=None):
        if isinstance(obj, dict):
            for k in keys:
                if k in obj:
                    return obj[k]
        return default

    def as_record(cid, raw):
        if isinstance(raw, dict):
            d = raw.get("demand", raw.get("q", raw.get("load", 1)))
            x = raw.get("x", raw.get("lon", raw.get("long", None)))
            y = raw.get("y", raw.get("lat", None))
            return cid, d, x, y
        if isinstance(raw, (list, tuple)):
            if len(raw) >= 3:
                return cid, raw[2], raw[0], raw[1]
        return cid, 1, None, None

    def parse_instance(inst):
        depot = None
        customers = []

        if isinstance(inst, dict):
            depot = get_value(inst, ["depot", "depot_info", "origin"], None)
            if "customers" in inst:
                raw = inst["customers"]
                if isinstance(raw, dict):
                    for k in sorted(raw.keys()):
                        customers.append(as_record(k, raw[k]))
                else:
                    for i, r in enumerate(raw):
                        cid = r.get("id", i + 1) if isinstance(r, dict) else i + 1
                        customers.append(as_record(cid, r))
            elif "demands" in inst:
                dem = inst["demands"]
                if isinstance(dem, dict):
                    ids = sorted(dem.keys())
                    for cid in ids:
                        rec = inst.get("nodes", {}).get(cid, {}) if isinstance(inst.get("nodes", {}), dict) else {}
                        customers.append(as_record(cid, {"demand": dem[cid], **rec}))
                else:
                    for i, d in enumerate(dem):
                        cid = i + 1
                        rec = inst.get("nodes", {}).get(cid, {}) if isinstance(inst.get("nodes", {}), dict) else {}
                        customers.append(as_record(cid, {"demand": d, **rec}))
            elif "nodes" in inst and isinstance(inst["nodes"], dict):
                for cid in sorted(inst["nodes"].keys()):
                    if depot is not None and cid == get_value(depot, ["id"], None):
                        continue
                    customers.append(as_record(cid, inst["nodes"][cid]))

        if depot is None:
            depot = {"x": 0, "y": 0}
        return depot, customers

    depot, customers = parse_instance(instance)

    if not customers:
        return []

    # Normalize and build lookup
    ids = []
    demand = {}
    pos = {}
    for cid, d, x, y in customers:
        ids.append(cid)
        demand[cid] = 0 if d is None else d
        if x is not None and y is not None:
            pos[cid] = (x, y)

    depot_xy = (get_value(depot, ["x", "lon", "long"], 0), get_value(depot, ["y", "lat"], 0))

    dist_matrix = get_value(instance, ["distance_matrix", "dist_matrix"], None)

    def dist(a, b):
        if dist_matrix is not None:
            ia = a if isinstance(a, int) else a
            ib = b if isinstance(b, int) else b
            try:
                return dist_matrix[ia][ib]
            except Exception:
                try:
                    return dist_matrix[ia - 1][ib - 1]
                except Exception:
                    pass
        if a == 0:
            ax, ay = depot_xy
        else:
            ax, ay = pos.get(a, (0, 0))
        if b == 0:
            bx, by = depot_xy
        else:
            bx, by = pos.get(b, (0, 0))
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    capacity = get_value(instance, ["capacity", "vehicle_capacity", "Q"], None)
    if capacity is None:
        capacity = sum(demand[c] for c in ids)

    # Initial singleton routes
    routes = [[c] for c in sorted(ids)]
    loads = {tuple([c]): demand[c] for c in ids}

    def route_load(route):
        s = 0
        for c in route:
            s += demand[c]
        return s

    def route_cost(route):
        if not route:
            return 0
        total = dist(0, route[0])
        for i in range(len(route) - 1):
            total += dist(route[i], route[i + 1])
        total += dist(route[-1], 0)
        return total

    def reverse_route(r):
        return list(reversed(r))

    def merge_routes(ra, rb, a_end, b_start):
        if a_end == "start":
            ra = reverse_route(ra)
        if b_start == "end":
            rb = reverse_route(rb)
        return ra + rb

    # Clarke-Wright style savings
    savings = []
    for i in range(len(ids)):
        a = ids[i]
        for j in range(i + 1, len(ids)):
            b = ids[j]
            s = dist(0, a) + dist(0, b) - dist(a, b)
            savings.append((s, a, b))
    savings.sort(key=lambda x: (-x[0], x[1], x[2]))

    route_of = {c: i for i, c in enumerate(routes[i][0] for i in range(len(routes)))}
    # route_of above is placeholder-like; rebuild explicitly
    route_of = {routes[i][0]: i for i in range(len(routes))}

    changed = True
    while changed:
        changed = False
        for s, a, b in savings:
            ia = route_of.get(a, None)
            ib = route_of.get(b, None)
            if ia is None or ib is None or ia == ib:
                continue
            ra = routes[ia]
            rb = routes[ib]
            if route_load(ra) + route_load(rb) > capacity:
                continue

            can = False
            merged = None
            if ra[-1] == a and rb[0] == b:
                merged = ra + rb
                can = True
            elif ra[-1] == a and rb[-1] == b:
                merged = ra + reverse_route(rb)
                can = True
            elif ra[0] == a and rb[0] == b:
                merged = reverse_route(ra) + rb
                can = True
            elif ra[0] == a and rb[-1] == b:
                merged = reverse_route(ra) + reverse_route(rb)
                can = True

            if not can:
                continue

            # accept if non-worse
            old = route_cost(ra) + route_cost(rb)
            new = route_cost(merged)
            if new <= old + 1e-9:
                routes[ia] = merged
                routes.pop(ib)
                route_of = {}
                for idx, r in enumerate(routes):
                    for c in r:
                        route_of[c] = idx
                changed = True
                break

    # Repair/Improve: relocate and swap
    def best_insertion_cost(route, c):
        best = None
        best_pos = 0
        base = route_cost(route)
        if not route:
            return dist(0, c) * 2, 0
        for pos in range(len(route) + 1):
            nr = route[:pos] + [c] + route[pos:]
            val = route_cost(nr) - base
            if best is None or val < best:
                best = val
                best_pos = pos
        return best, best_pos

    improved = True
    while improved:
        improved = False
        # relocate
        for i in range(len(routes)):
            for j in range(len(routes[i])):
                c = routes[i][j]
                for k in range(len(routes)):
                    if i == k:
                        continue
                    if route_load(routes[k]) + demand[c] > capacity:
                        continue
                    ri = routes[i]
                    rk = routes[k]
                    rem = ri[:j] + ri[j + 1:]
                    if not rem:
                        continue
                    old = route_cost(ri) + route_cost(rk)
                    # best insertion into rk
                    ins_delta, pos = best_insertion_cost(rk, c)
                    new_rk = rk[:pos] + [c] + rk[pos:]
                    new = route_cost(rem) + route_cost(new_rk)
                    if new + 1e-9 < old:
                        routes[i] = rem
                        routes[k] = new_rk
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break

        if improved:
            continue

        # swap between routes
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                ri = routes[i]
                rj = routes[j]
                for a in range(len(ri)):
                    for b in range(len(rj)):
                        ca = ri[a]
                        cb = rj[b]
                        li = route_load(ri) - demand[ca] + demand[cb]
                        lj = route_load(rj) - demand[cb] + demand[ca]
                        if li > capacity or lj > capacity:
                            continue
                        nri = ri[:a] + [cb] + ri[a + 1:]
                        nrj = rj[:b] + [ca] + rj[b + 1:]
                        old = route_cost(ri) + route_cost(rj)
                        new = route_cost(nri) + route_cost(nrj)
                        if new + 1e-9 < old:
                            routes[i] = nri
                            routes[j] = nrj
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    # Final cleanup: remove empties, deterministic order
    routes = [r for r in routes if r]
    routes.sort(key=lambda r: (r[0], len(r)))
    return routes
