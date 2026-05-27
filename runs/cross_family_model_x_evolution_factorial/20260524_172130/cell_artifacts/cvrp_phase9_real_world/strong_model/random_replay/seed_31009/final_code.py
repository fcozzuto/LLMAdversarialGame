def solve_cvrp(instance):
    def is_dict(x):
        try:
            x.keys
            return True
        except:
            return False

    def get_any(d, keys, default=None):
        try:
            for k in keys:
                try:
                    return d[k]
                except:
                    pass
        except:
            pass
        return default

    def num(x):
        try:
            return x + 0
        except:
            return None

    depot_id = 0
    try:
        depot_id = get_any(instance, ("depot", "depot_id", "depot_index", "depot_node"), 0)
    except:
        depot_id = 0

    capacity = None
    try:
        capacity = get_any(instance, ("capacity", "vehicle_capacity", "cap"), None)
    except:
        capacity = None

    coords = None
    demands = None
    try:
        coords = get_any(instance, ("coords", "coordinates", "locations", "points"), None)
        demands = get_any(instance, ("demands", "demand"), None)
    except:
        coords = None
        demands = None

    customers = []
    if is_dict(demands):
        for k in demands:
            if k != depot_id:
                customers.append(k)
    elif is_dict(coords):
        for k in coords:
            if k != depot_id:
                customers.append(k)
    elif is_dict(instance):
        if "customers" in instance:
            try:
                for c in instance["customers"]:
                    try:
                        cid = c.get("id")
                        if cid != depot_id:
                            customers.append(cid)
                    except:
                        pass
            except:
                pass
        else:
            for k in instance:
                if k != depot_id and num(k) is not None:
                    customers.append(k)

    seen = {}
    uniq = []
    for cid in customers:
        if cid not in seen:
            seen[cid] = 1
            uniq.append(cid)
    customers = uniq

    def demand_of(cid):
        try:
            if is_dict(demands) and cid in demands:
                return demands[cid]
        except:
            pass
        try:
            if is_dict(instance) and "customers" in instance:
                for c in instance["customers"]:
                    try:
                        if c.get("id") == cid:
                            return c.get("demand", 0)
                    except:
                        pass
        except:
            pass
        return 0

    def coord_of(cid):
        try:
            if is_dict(coords) and cid in coords:
                return coords[cid]
        except:
            pass
        try:
            if is_dict(instance) and "customers" in instance:
                for c in instance["customers"]:
                    try:
                        if c.get("id") == cid:
                            if "coord" in c:
                                return c["coord"]
                            if "coords" in c:
                                return c["coords"]
                            if "location" in c:
                                return c["location"]
                    except:
                        pass
        except:
            pass
        return None

    depot_coord = coord_of(depot_id)
    has_coords = depot_coord is not None
    if has_coords:
        for cid in customers:
            if coord_of(cid) is None:
                has_coords = False
                break

    def dist(a, b):
        if not has_coords:
            return 0
        pa = coord_of(a)
        pb = coord_of(b)
        try:
            dx = pa[0] - pb[0]
            dy = pa[1] - pb[1]
            return (dx * dx + dy * dy) ** 0.5
        except:
            return 0

    total_demand = 0
    max_demand = 0
    for cid in customers:
        d = demand_of(cid)
        total_demand += d
        if d > max_demand:
            max_demand = d
    if capacity is None:
        capacity = total_demand if total_demand > 0 else max_demand

    oversized = []
    normal = []
    for cid in customers:
        if demand_of(cid) > capacity:
            oversized.append(cid)
        else:
            normal.append(cid)

    if has_coords:
        dx0, dy0 = depot_coord[0], depot_coord[1]
        ordered = []
        for cid in normal:
            p = coord_of(cid)
            vx = p[0] - dx0
            vy = p[1] - dy0
            if vx >= 0 and vy >= 0:
                q = 0
                key = vy / (vx + 1e-12)
            elif vx < 0 and vy >= 0:
                q = 1
                key = -vx / (vy + 1e-12)
            elif vx < 0 and vy < 0:
                q = 2
                key = vy / (vx - 1e-12)
            else:
                q = 3
                key = -vx / (abs(vy) + 1e-12)
            ordered.append((q, key, dist(depot_id, cid), cid))
        ordered.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
        ordered = [t[3] for t in ordered]
    else:
        ordered = sorted(normal, key=lambda c: (-demand_of(c), c))

    routes = []
    cur = []
    load = 0
    for cid in ordered:
        d = demand_of(cid)
        if cur and load + d > capacity:
            routes.append(cur)
            cur = [cid]
            load = d
        else:
            cur.append(cid)
            load += d
    if cur:
        routes.append(cur)

    for cid in oversized:
        routes.append([cid])

    # Repair: ensure every customer appears exactly once
    present = {}
    repaired = []
    for r in routes:
        rr = []
        rl = 0
        for cid in r:
            if cid not in present:
                present[cid] = 1
                rr.append(cid)
                rl += demand_of(cid)
        if rr:
            repaired.append(rr)
    routes = repaired

    for cid in customers:
        if cid not in present:
            d = demand_of(cid)
            placed = False
            best_i = -1
            best_delta = None
            if has_coords:
                for i in range(len(routes)):
                    r = routes[i]
                    if sum([demand_of(x) for x in r]) + d <= capacity:
                        if len(r) == 0:
                            delta = 0
                        elif len(r) == 1:
                            delta = dist(r[0], cid) + dist(cid, depot_id) - dist(r[0], depot_id)
                        else:
                            delta = None
                            prev = depot_id
                            for j in range(len(r) + 1):
                                nxt = depot_id if j == len(r) else r[j]
                                add = dist(prev, cid) + dist(cid, nxt) - dist(prev, nxt)
                                if delta is None or add < delta:
                                    delta = add
                                prev = nxt
                        if best_delta is None or delta < best_delta:
                            best_delta = delta
                            best_i = i
                if best_i >= 0:
                    routes[best_i].append(cid)
                    present[cid] = 1
                    placed = True
            if not placed:
                routes.append([cid])
                present[cid] = 1

    # Local search: relocate single customer to cheaper feasible positions
    def route_load(r):
        s = 0
        for x in r:
            s += demand_of(x)
        return s

    improved = True
    it = 0
    while improved and it < 2:
        improved = False
        it += 1
        i = 0
        while i < len(routes):
            r = routes[i]
            j = 0
            while j < len(r):
                cid = r[j]
                best_r = i
                best_p = j
                best_score = None
                for k in range(len(routes)):
                    if k != i and route_load(routes[k]) + demand_of(cid) > capacity:
                        continue
                    rr = routes[k]
                    for p in range(len(rr) + 1):
                        if k == i and (p == j or p == j + 1):
                            continue
                        before = depot_id if p == 0 else rr[p - 1]
