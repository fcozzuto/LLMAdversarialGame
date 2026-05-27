def solve_cvrp(instance):
    def is_num(x):
        return isinstance(x, (int, float)) and not isinstance(x, bool)

    def as_point(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2 and is_num(v[0]) and is_num(v[1]):
            return (float(v[0]), float(v[1]))
        if isinstance(v, dict):
            for a, b in (("x", "y"), ("X", "Y"), ("lon", "lat"), ("long", "lat")):
                if a in v and b in v and is_num(v[a]) and is_num(v[b]):
                    return (float(v[a]), float(v[b]))
        return None

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    def get_capacity():
        for k in ("capacity", "vehicle_capacity", "cap"):
            if isinstance(instance, dict) and k in instance and is_num(instance[k]):
                return float(instance[k])
        return float("inf")

    def extract_depot():
        if isinstance(instance, dict):
            for k in ("depot", "depot_coord", "depot_location"):
                if k in instance:
                    p = as_point(instance[k])
                    if p is not None:
                        return p
                    if isinstance(instance[k], dict):
                        for kk in ("coord", "location", "point"):
                            if kk in instance[k]:
                                p = as_point(instance[k][kk])
                                if p is not None:
                                    return p
            for k in ("coords", "coordinates", "locations", "nodes"):
                if k in instance and isinstance(instance[k], (list, tuple)) and instance[k]:
                    p = as_point(instance[k][0])
                    if p is not None:
                        return p
        return (0.0, 0.0)

    def get_data():
        depot = extract_depot()
        cap = get_capacity()
        coords = {}
        demands = {}
        ids = []

        if isinstance(instance, dict):
            # Common explicit structures
            if "customers" in instance:
                c = instance["customers"]
                if isinstance(c, dict):
                    for cid, val in c.items():
                        if cid == 0 or cid == "0" or cid == "depot":
                            continue
                        p = None
                        d = None
                        if isinstance(val, dict):
                            p = as_point(val)
                            if p is None:
                                for kk in ("coord", "location", "point"):
                                    if kk in val:
                                        p = as_point(val[kk])
                                        if p is not None:
                                            break
                            for kk in ("demand", "dem", "q"):
                                if kk in val and is_num(val[kk]):
                                    d = float(val[kk])
                                    break
                        elif isinstance(val, (list, tuple)):
                            if len(val) >= 2:
                                p = as_point(val)
                            if len(val) >= 3 and is_num(val[2]):
                                d = float(val[2])
                        if p is not None:
                            coords[cid] = p
                        if d is not None:
                            demands[cid] = d
                        ids.append(cid)
                elif isinstance(c, (list, tuple)):
                    for cid, val in enumerate(c):
                        if cid == 0:
                            continue
                        p = None
                        d = None
                        if isinstance(val, dict):
                            p = as_point(val)
                            if p is None:
                                for kk in ("coord", "location", "point"):
                                    if kk in val:
                                        p = as_point(val[kk])
                                        if p is not None:
                                            break
                            for kk in ("demand", "dem", "q"):
                                if kk in val and is_num(val[kk]):
                                    d = float(val[kk])
                                    break
                        elif isinstance(val, (list, tuple)):
                            if len(val) >= 2:
                                p = as_point(val)
                            if len(val) >= 3 and is_num(val[2]):
                                d = float(val[2])
                        if p is not None:
                            coords[cid] = p
                        if d is not None:
                            demands[cid] = d
                        ids.append(cid)

            # Fallback: coordinates + demands arrays/dicts
            if not ids:
                coord_src = None
                for k in ("coords", "coordinates", "locations", "points"):
                    if k in instance:
                        coord_src = instance[k]
                        break
                dem_src = None
                for k in ("demands", "demand", "q"):
                    if k in instance:
                        dem_src = instance[k]
                        break

                if isinstance(coord_src, dict):
                    for cid, val in coord_src.items():
                        if cid == 0 or cid == "0" or cid == "depot":
                            continue
                        p = as_point(val)
                        if p is not None:
                            coords[cid] = p
                            ids.append(cid)
                elif isinstance(coord_src, (list, tuple)):
                    for cid, val in enumerate(coord_src):
                        if cid == 0:
                            continue
                        p = as_point(val)
                        if p is not None:
                            coords[cid] = p
                        ids.append(cid)

                if isinstance(dem_src, dict):
                    for cid, val in dem_src.items():
                        if cid == 0 or cid == "0" or cid == "depot":
                            continue
                        if is_num(val):
                            demands[cid] = float(val)
                elif isinstance(dem_src, (list, tuple)):
                    for cid, val in enumerate(dem_src):
                        if cid == 0:
                            continue
                        if is_num(val):
                            demands[cid] = float(val)

        if not ids:
            n = 0
            for k in ("n", "num_customers", "customers_count"):
                if isinstance(instance, dict) and k in instance and isinstance(instance[k], int):
                    n = instance[k]
                    break
            ids = list(range(1, n + 1))

        ids = sorted(set(ids), key=lambda x: (str(type(x)), x))
        if depot is None:
            depot = (0.0, 0.0)

        # Fill missing demands with 1
        for cid in ids:
            if cid not in demands:
                demands[cid] = 1.0

        # Fill missing coords with deterministic pseudo layout if absent
        missing = [cid for cid in ids if cid not in coords]
        if missing:
            for i, cid in enumerate(missing):
                coords[cid] = (float(i), 0.0)

        return depot, cap, ids, coords, demands

    depot, cap, customers, coords, demands = get_data()

    def route_load(route):
        s = 0.0
        for c in route:
            s += demands.get(c, 1.0)
        return s

    # Sweep order around depot for constructive seed
    ordered = sorted(customers, key=lambda c: ((coords[c][1] - depot[1]) and 0) or 0)

    def angle_key(c):
        x, y = coords[c]
        dx = x - depot[0]
        dy = y - depot[1]
        # quadrant-aware deterministic ordering
        if dx == 0 and dy == 0:
            return (-10.0, 0.0)
        ang = dy / (abs(dx) + abs(dy) + 1e-12)
        quad = 0
        if dx >= 0 and dy >= 0:
            quad = 0
        elif dx < 0 <= dy:
            quad = 1
        elif dx < 0 and dy < 0:
            quad = 2
        else:
            quad = 3
        return (quad, ang, dist(depot, coords[c]))

    ordered = sorted(customers, key=angle_key)

    # Construct by cheapest feasible insertion into existing routes
    routes = []

    def route_cost(rt):
        if not rt:
            return 0.0
        cst = dist(depot, coords[rt[0]]) + dist(coords[rt[-1]], depot)
        for i in range(len(rt) - 1):
            cst += dist(coords[rt[i]], coords[rt[i + 1]])
        return cst

    for c in ordered:
        best = None
        best_delta = None
        d = demands.get(c, 1.0)
        for r_idx, rt in enumerate(routes):
            if route_load(rt) + d > cap:
                continue
            if not rt:
                delta = 2 * dist(depot, coords[c])
                pos = 0
            else:
                # best insertion position in route
                prev = depot
                for i in range(len(rt) + 1):
                    nxt = depot if i == len(rt) else coords[rt[i]]
                    delta = dist(prev, coords[c]) + dist(coords[c], nxt) - dist(prev, nxt)
                    if best_delta is None or delta < best_delta - 1e-12 or (abs(delta - best_delta) <= 1e-12 and (r_idx, i) < best[:2]):
                        best_delta = delta
                        best = (r_idx, i)
                    if i < len(rt):
                        prev = coords[rt[i]]
        if best is None:
            routes.append([c])
        else:
            r_idx, pos = best
            routes[r_idx].insert(pos, c)

    # Repair: if any route exceeds cap due to numeric issue, split off last customers
    repaired = []
    for rt in routes:
        cur = []
        load = 0.0
        for c in rt:
            d = demands.get(c, 1.0)
            if load + d <= cap or not cur:
                cur.append(c)
                load += d
            else:
                repaired.append(cur)
                cur = [c]
                load = d
        if cur:
            repaired.append(cur)
    routes = repaired

    # Local search: intra-route 2-opt
    def two_opt_best(rt):
        n = len(rt)
        if n < 4:
            return rt
        improved = True
        while improved:
            improved = False
            best_gain = 1e-12
            best_i = best_j = None
            for i in range(n - 2):
                a = depot if i == 0 else coords[rt[i - 1]]
                b = coords[rt[i]]
                for j in range(i + 2, n):
                    c = coords[rt[j - 1]]
                    d = depot if j == n else coords[rt[j]]
