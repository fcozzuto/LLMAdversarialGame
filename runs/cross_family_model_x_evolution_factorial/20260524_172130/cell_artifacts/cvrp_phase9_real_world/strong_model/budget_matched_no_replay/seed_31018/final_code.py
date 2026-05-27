def solve_cvrp(instance):
    def safe_get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        try:
            d = obj.__dict__
            if key in d:
                return d[key]
        except Exception:
            pass
        try:
            return obj[key]
        except Exception:
            return default

    def as_point(x):
        if isinstance(x, dict):
            return (x.get("x", 0.0), x.get("y", 0.0))
        if isinstance(x, (list, tuple)) and len(x) >= 2:
            return (x[0], x[1])
        try:
            d = x.__dict__
            if "x" in d and "y" in d:
                return (d["x"], d["y"])
        except Exception:
            pass
        return (0.0, 0.0)

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    depot = safe_get(instance, "depot", None)
    customers = safe_get(instance, "customers", None)
    if customers is None:
        customers = safe_get(instance, "nodes", None)
    if customers is None:
        customers = safe_get(instance, "points", None)
    if customers is None:
        customers = []

    cap = safe_get(instance, "capacity", None)
    if cap is None:
        cap = safe_get(instance, "vehicle_capacity", None)
    if cap is None:
        cap = safe_get(instance, "Q", None)

    depot_point = (0.0, 0.0)
    depot_id = 0

    items = []
    if isinstance(customers, dict):
        for cid in sorted(customers.keys()):
            c = customers[cid]
            if cid == depot_id:
                depot_point = as_point(c)
                continue
            p = as_point(c)
            dmd = safe_get(c, "demand", 0)
            items.append((cid, p, dmd))
    else:
        for idx, c in enumerate(customers):
            cid = safe_get(c, "id", None)
            if cid is None:
                cid = idx
            if depot is not None:
                if cid == depot_id:
                    depot_point = as_point(c)
                    continue
            else:
                is_depot = safe_get(c, "is_depot", False)
                dmd0 = safe_get(c, "demand", None)
                if idx == 0 and (is_depot or dmd0 is None):
                    depot_point = as_point(c)
                    depot_id = cid
                    continue
            p = as_point(c)
            dmd = safe_get(c, "demand", 0)
            items.append((cid, p, dmd))

    if depot is not None:
        depot_point = as_point(depot)

    pos = {}
    demand = {}
    for cid, p, dmd in items:
        pos[cid] = p
        demand[cid] = dmd if dmd is not None else 0

    if not cap:
        total = 0
        for cid in demand:
            total += demand[cid]
        cap = total if total > 0 else 1

    unserved = set(pos.keys())
    routes = []

    def route_cost(route):
        if not route:
            return 0.0
        c = dist(depot_point, pos[route[0]])
        for i in range(len(route) - 1):
            c += dist(pos[route[i]], pos[route[i + 1]])
        c += dist(pos[route[-1]], depot_point)
        return c

    def route_load(route):
        s = 0
        for cid in route:
            s += demand[cid]
        return s

    def feasible_customers(load):
        feas = []
        for cid in unserved:
            if load + demand[cid] <= cap:
                feas.append(cid)
        return feas

    while unserved:
        route = []
        load = 0
        current = depot_point

        while True:
            feas = feasible_customers(load)
            if not feas:
                break
            best = None
            best_score = None
            for cid in sorted(feas):
                p = pos[cid]
                extra = dist(current, p) + dist(p, depot_point) - dist(current, depot_point)
                score = (extra, dist(depot_point, p), -demand[cid], cid)
                if best_score is None or score < best_score:
                    best_score = score
                    best = cid
            if best is None:
                break
            route.append(best)
            load += demand[best]
            current = pos[best]
            unserved.remove(best)

        if not route:
            best = None
            best_score = None
            for cid in sorted(unserved):
                if demand[cid] <= cap:
                    p = pos[cid]
                    score = (dist(depot_point, p), -demand[cid], cid)
                    if best_score is None or score < best_score:
                        best_score = score
                        best = cid
            if best is None:
                best = min(unserved)
            route = [best]
            unserved.remove(best)

        routes.append(route)

    improved = True
    while improved:
        improved = False

        for i in range(len(routes)):
            ri = routes[i]
            li = route_load(ri)
            for a in range(len(ri)):
                cid = ri[a]
                for j in range(len(routes)):
                    rj = routes[j]
                    if i == j:
                        for b in range(len(rj) + 1):
                            if b == a or b == a + 1:
                                continue
                            new_r = ri[:a] + ri[a + 1:]
                            new_r = new_r[:b] + [cid] + new_r[b:]
                            if route_cost(new_r) + 1e-12 < route_cost(ri):
                                routes[i] = new_r
                                improved = True
                                break
                        if improved:
                            break
                    else:
                        if route_load(rj) + demand[cid] > cap:
                            continue
                        for b in range(len(rj) + 1):
                            new_ri = ri[:a] + ri[a + 1:]
                            new_rj = rj[:b] + [cid] + rj[b:]
                            if route_cost(new_ri) + route_cost(new_rj) + 1e-12 < route_cost(ri) + route_cost(rj):
                                routes[i] = new_ri
                                routes[j] = new_rj
                                improved = True
                                break
                        if improved:
                            break
                if improved:
                    break
            if improved:
                break

        if improved:
            continue

        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                ri = routes[i]
                rj = routes[j]
                li = route_load(ri)
                lj = route_load(rj)
                for a in range(len(ri)):
                    for b in range(len(rj)):
                        ci = ri[a]
                        cj = rj[b]
                        if li - demand[ci] + demand[cj] > cap:
                            continue
                        if lj - demand[cj] + demand[ci] > cap:
                            continue
                        nri = ri[:a] + [cj] + ri[a + 1:]
                        nrj = rj[:b] + [ci] + rj[b + 1:]
                        if route_cost(nri) + route_cost(nrj) + 1e-12 < route_cost(ri) + route_cost(rj):
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

    seen = set()
    cleaned = []
    for r in routes:
        nr = []
        for cid in r:
            if cid not in seen:
                seen.add(cid)
                nr.append(cid)
        if nr:
            cleaned.append(nr)

    missing = [cid for cid in sorted(pos.keys()) if cid not in seen]
    for cid in missing:
        placed = False
        for r in cleaned:
            if route_load(r) + demand[cid] <= cap:
                r.append(cid)
                placed = True
                break
        if not placed:
            cleaned.append([cid])

    return cleaned
