def solve_cvrp(instance):
    def get_key(d, keys, default=None):
        for k in keys:
            if k in d:
                return d[k]
        return default

    def is_num(x):
        return isinstance(x, (int, float))

    depot_id = get_key(instance, ["depot", "depot_id", "start", "origin"], 0)
    capacity = get_key(instance, ["capacity", "vehicle_capacity", "cap"], None)

    dist = get_key(instance, ["distance_matrix", "dist", "distance"], None)

    coords = {}
    demands = {}
    customer_ids = []

    if "customers" in instance and isinstance(instance["customers"], list):
        for idx, c in enumerate(instance["customers"]):
            if isinstance(c, dict):
                cid = c.get("id", idx if idx != depot_id else idx + 1)
                if cid == depot_id:
                    continue
                customer_ids.append(cid)
                if "demand" in c:
                    demands[cid] = c["demand"]
                if "x" in c and "y" in c:
                    coords[cid] = (c["x"], c["y"])
            else:
                cid = idx + 1
                if cid == depot_id:
                    continue
                customer_ids.append(cid)
    elif "nodes" in instance and isinstance(instance["nodes"], list):
        for idx, n in enumerate(instance["nodes"]):
            if isinstance(n, dict):
                cid = n.get("id", idx)
                if cid == depot_id:
                    continue
                customer_ids.append(cid)
                if "demand" in n:
                    demands[cid] = n["demand"]
                if "x" in n and "y" in n:
                    coords[cid] = (n["x"], n["y"])
    else:
        if isinstance(instance.get("demands"), dict):
            for cid, d in instance["demands"].items():
                if cid != depot_id:
                    customer_ids.append(cid)
                    demands[cid] = d
        elif isinstance(instance.get("demands"), list):
            for cid, d in enumerate(instance["demands"]):
                if cid != depot_id:
                    customer_ids.append(cid)
                    demands[cid] = d
        elif "coords" in instance and isinstance(instance["coords"], dict):
            for cid, xy in instance["coords"].items():
                if cid != depot_id:
                    customer_ids.append(cid)
                    coords[cid] = xy
        elif "coordinates" in instance and isinstance(instance["coordinates"], dict):
            for cid, xy in instance["coordinates"].items():
                if cid != depot_id:
                    customer_ids.append(cid)
                    coords[cid] = xy
        elif "locations" in instance and isinstance(instance["locations"], list):
            for cid, xy in enumerate(instance["locations"]):
                if cid != depot_id:
                    customer_ids.append(cid)
                    if isinstance(xy, (list, tuple)) and len(xy) >= 2:
                        coords[cid] = (xy[0], xy[1])

    customer_ids = sorted(set(customer_ids))

    if capacity is None:
        total_demand = 0
        for cid in customer_ids:
            total_demand += demands.get(cid, 1)
        capacity = total_demand if total_demand > 0 else 1

    depot_coord = None
    if "depot" in instance and isinstance(instance["depot"], (list, tuple)) and len(instance["depot"]) >= 2:
        depot_coord = (instance["depot"][0], instance["depot"][1])
    elif "depot_coord" in instance and isinstance(instance["depot_coord"], (list, tuple)) and len(instance["depot_coord"]) >= 2:
        depot_coord = (instance["depot_coord"][0], instance["depot_coord"][1])
    elif depot_id in coords:
        depot_coord = coords[depot_id]
    elif "depot" in instance and isinstance(instance["depot"], dict):
        d = instance["depot"]
        if "x" in d and "y" in d:
            depot_coord = (d["x"], d["y"])

    def demand_of(cid):
        v = demands.get(cid, 1)
        return v if is_num(v) and v >= 0 else 1

    def coord_of(cid):
        return coords.get(cid, None)

    def d(i, j):
        if dist is not None:
            try:
                return dist[i][j]
            except:
                try:
                    return dist[i][j if isinstance(j, int) else int(j)]
                except:
                    pass
        ci = coord_of(i)
        cj = coord_of(j)
        if ci is not None and cj is not None:
            dx = ci[0] - cj[0]
            dy = ci[1] - cj[1]
            return dx * dx + dy * dy
        if depot_coord is not None and i == depot_id and cj is not None:
            dx = depot_coord[0] - cj[0]
            dy = depot_coord[1] - cj[1]
            return dx * dx + dy * dy
        if depot_coord is not None and j == depot_id and ci is not None:
            dx = ci[0] - depot_coord[0]
            dy = ci[1] - depot_coord[1]
            return dx * dx + dy * dy
        return abs(i - j)

    unrouted = set(customer_ids)
    routes = []

    def feasible_seed_list():
        lst = []
        for cid in unrouted:
            dm = demand_of(cid)
            if dm <= capacity:
                lst.append(cid)
        return lst

    def pick_seed():
        best = None
        best_key = None
        for cid in feasible_seed_list():
            key = (demand_of(cid), d(depot_id, cid), -cid)
            if best is None or key > best_key:
                best = cid
                best_key = key
        return best

    while unrouted:
        seed = pick_seed()
        if seed is None:
            seed = min(unrouted)
        route = [seed]
        unrouted.remove(seed)
        load = demand_of(seed)
        last = seed
        while True:
            best = None
            best_score = None
            for cid in unrouted:
                dem = demand_of(cid)
                if load + dem > capacity:
                    continue
                score = (d(last, cid) + 0.25 * d(depot_id, cid) - 0.05 * dem, d(depot_id, cid), cid)
                if best is None or score < best_score:
                    best = cid
                    best_score = score
            if best is None:
                break
            route.append(best)
            unrouted.remove(best)
            load += demand_of(best)
            last = best
        routes.append(route)

    def route_load(route):
        s = 0
        for cid in route:
            s += demand_of(cid)
        return s

    def route_cost(route):
        if not route:
            return 0
        total = d(depot_id, route[0])
        for i in range(len(route) - 1):
            total += d(route[i], route[i + 1])
        total += d(route[-1], depot_id)
        return total

    def improved_2opt(route):
        n = len(route)
        if n < 4:
            return route
        changed = True
        while changed:
            changed = False
            for i in range(n - 2):
                a = depot_id if i == 0 else route[i - 1]
                b = route[i]
                for k in range(i + 1, n - 1):
                    c = route[k]
                    d2 = depot_id if k == n - 1 else route[k + 1]
                    before = d(a, b) + d(c, d2)
                    after = d(a, c) + d(b, d2)
                    if after + 1e-12 < before:
                        route[i:k + 1] = route[i:k + 1][::-1]
                        changed = True
                        break
                if changed:
                    break
        return route

    for idx in range(len(routes)):
        routes[idx] = improved_2opt(routes[idx])

    def relocate_best():
        best_move = None
        best_delta = 0
        m = len(routes)
        for i in range(m):
            ri = routes[i]
            li = route_load(ri)
            for p in range(len(ri)):
                cust = ri[p]
                dc = demand_of(cust)
                rem_cost = 0
                a = depot_id if p == 0 else ri[p - 1]
                b = depot_id if p == len(ri) - 1 else ri[p + 1]
                rem_cost = d(a, cust) + d(cust, b) - d(a, b)
                for j in range(m):
                    if i == j:
                        continue
                    rj = routes[j]
                    lj = route_load(rj)
                    if lj + dc > capacity:
                        continue
                    for q in range(len(rj) + 1):
                        x = depot_id if q == 0 else rj[q - 1]
                        y = depot_id if q == len(rj) else rj[q]
                        ins_cost = d(x, cust) + d(cust, y) - d(x, y)
                        delta = ins_cost - rem_cost
                        if delta < best_delta - 1e-12:
                            best_delta = delta
                            best_move = (i, p, j, q, cust)
        return best_move

    def apply_reloc(move):
        i, p, j, q, cust = move
        c = routes[i].pop(p)
