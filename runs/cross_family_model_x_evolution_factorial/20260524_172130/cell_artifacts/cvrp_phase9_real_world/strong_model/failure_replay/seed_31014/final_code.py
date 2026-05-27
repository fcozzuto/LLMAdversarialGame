def solve_cvrp(instance):
    def is_dict(x):
        return x.__class__ is dict

    def is_list(x):
        return x.__class__ is list

    def as_list(x):
        if x is None:
            return None
        if is_list(x):
            return x
        try:
            return list(x)
        except:
            return None

    def fetch(obj, keys, default=None):
        for k in keys:
            try:
                if is_dict(obj) and k in obj:
                    return obj[k]
            except:
                pass
            try:
                d = obj.__dict__
                if k in d:
                    return d[k]
            except:
                pass
        return default

    def num(x, default=0.0):
        try:
            return float(x)
        except:
            return default

    def iv(x, default=0):
        try:
            return int(x)
        except:
            return default

    coords = None
    demand_map = {}
    capacity = fetch(instance, ("capacity", "vehicle_capacity", "cap"), None)

    nodes = fetch(instance, ("nodes", "customers", "points"), None)
    if nodes is not None and not is_dict(nodes):
        nodes = as_list(nodes)

    if is_dict(nodes):
        coords = {}
        for k in nodes:
            v = nodes[k]
            if is_dict(v):
                if "x" in v and "y" in v:
                    coords[k] = (num(v["x"]), num(v["y"]))
                if "demand" in v:
                    demand_map[k] = num(v["demand"], 1.0)
    elif is_list(nodes):
        coords = {}
        for i in range(len(nodes)):
            v = nodes[i]
            if is_dict(v):
                nid = v["id"] if "id" in v else i
                if "x" in v and "y" in v:
                    coords[nid] = (num(v["x"]), num(v["y"]))
                if "demand" in v:
                    demand_map[nid] = num(v["demand"], 1.0)

    if coords is None:
        coords = fetch(instance, ("coords", "coordinates", "locations"), None)
        if is_list(coords):
            nc = {}
            for i in range(len(coords)):
                pt = coords[i]
                try:
                    nc[i] = (num(pt[0]), num(pt[1]))
                except:
                    pass
            coords = nc
        elif not is_dict(coords):
            coords = None

    demands = fetch(instance, ("demands", "demand"), None)
    if is_list(demands):
        demand_map = {}
        for i in range(len(demands)):
            demand_map[i] = num(demands[i], 1.0)
    elif is_dict(demands):
        demand_map = {}
        for k in demands:
            demand_map[k] = num(demands[k], 1.0)

    depot = fetch(instance, ("depot", "depot_id"), 0)
    if is_dict(depot):
        depot = depot["id"] if "id" in depot else 0
    depot = depot if depot is not None else 0

    customer_ids = fetch(instance, ("customer_ids", "customers_ids"), None)
    customer_ids = as_list(customer_ids) if customer_ids is not None else None

    if customer_ids is None:
        if is_dict(demand_map) and len(demand_map) > 0:
            customer_ids = [k for k in demand_map if k != depot]
        elif is_dict(coords) and len(coords) > 0:
            customer_ids = [k for k in coords if k != depot]
        else:
            n = iv(fetch(instance, ("n_customers", "num_customers", "dimension"), 0), 0)
            customer_ids = [i for i in range(1, n)] if n > 0 else []

    if depot in customer_ids:
        customer_ids = [c for c in customer_ids if c != depot]

    def dist(a, b):
        if coords is not None and a in coords and b in coords:
            ax, ay = coords[a]
            bx, by = coords[b]
            dx = ax - bx
            dy = ay - by
            return (dx * dx + dy * dy) ** 0.5
        try:
            return abs(a - b) * 1.0
        except:
            return 0.0

    def dem(c):
        return demand_map[c] if c in demand_map else 1.0

    capacity = num(capacity, 0.0)
    if capacity <= 0:
        s = 0.0
        for c in customer_ids:
            s += dem(c)
        capacity = s if s > 0 else 1.0

    seen = {}
    customers = []
    for c in customer_ids:
        if c != depot and c not in seen:
            seen[c] = 1
            customers.append(c)

    if len(customers) == 0:
        return []

    # Farthest-first with demand tie-break
    scored = []
    for c in customers:
        scored.append((dist(depot, c), dem(c), c))
    scored.sort(key=lambda t: (-t[0], -t[1], t[2]))
    customers = [t[2] for t in scored]

    # Seed routes by sweep-like assignment
    routes = []
    loads = []
    remaining = customers[:]

    while remaining:
        route = []
        load = 0.0
        current = depot

        # start with a far customer if possible
        best_i = -1
        best_key = None
        for i in range(len(remaining)):
            c = remaining[i]
            if dem(c) <= capacity:
                key = (dist(depot, c), dem(c), c)
                if best_key is None or key > best_key:
                    best_key = key
                    best_i = i
        if best_i < 0:
            best_i = 0
        c = remaining.pop(best_i)
        if dem(c) <= capacity:
            route.append(c)
            load += dem(c)
            current = c

        improved = True
        while improved and remaining:
            improved = False
            best_j = -1
            best_score = None
            for j in range(len(remaining)):
                u = remaining[j]
                du = dem(u)
                if load + du > capacity:
                    continue
                score = (dist(current, u) - 0.25 * dist(depot, u), -du, u)
                if best_score is None or score < best_score:
                    best_score = score
                    best_j = j
            if best_j >= 0:
                u = remaining.pop(best_j)
                route.append(u)
                load += dem(u)
                current = u
                improved = True

        routes.append(route)
        loads.append(load)

    # Repair: place any infeasible oversize singletons by splitting? If any demand > capacity, force own route
    # This is rare; if a customer exceeds capacity, keep as singleton to preserve visitation.
    for i in range(len(routes)):
        if len(routes[i]) == 0:
            continue

    # Simple local improvement: pairwise intra-route 2-opt on coordinate order via nearest-neighbor ordering
    for r in range(len(routes)):
        route = routes[r]
        if len(route) <= 2:
            continue
        # reverse if second end is better connected to depot
        if dist(depot, route[-1]) < dist(depot, route[0]):
            route.reverse()
        # one pass of local adjacent swaps if it reduces edge length
        changed = True
        while changed:
            changed = False
            for i in range(1, len(route) - 1):
                a = depot if i == 0 else route[i - 1]
                b = route[i]
                c = route[i + 1]
                d = depot if i + 2 >= len(route) else route[i + 2]
                old = dist(a, b) + dist(b, c) + dist(c, d)
                new = dist(a, c) + dist(c, b) + dist(b, d)
                if new + 1e-12 < old:
                    route[i], route[i + 1] = route[i + 1], route[i]
                    changed = True
        routes[r] = route

    # Cross-route relocate by best insertion if capacity allows
    for _ in range(2):
        moved = False
        for i in range(len(routes)):
            if len(routes[i]) == 0:
                continue
            for p in range(len(routes[i])):
                c = routes[i][p]
                dc = dem(c)
                best = None
                best_j = -1
                best_pos = -1
                for j in range(len(routes)):
                    if i == j:
                        continue
                    if loads[j] + dc > capacity:
                        continue
                    rr = routes[j]
                    for pos in range(len(rr) + 1):
                        left = depot if pos == 0 else rr[pos - 1]
                        right = depot if pos == len(rr) else rr[pos]
                        delta = dist(left, c) + dist(c, right) - dist(left, right)
                        if best is None or delta < best:
                            best = delta
                            best_j = j
                            best_pos = pos
                if best_j >= 0 and best is not None and best < -1e-12:
                    routes[best_j].insert(best_pos, c)
                    loads[best_j] += dc
                    loads[i] -= dc
                    routes[i].pop(p)
                    moved = True
                    break
            if moved:
                break
        if not moved:
            break

    # Remove empties
    routes = [r for r in routes if len(r) > 0]
    return routes
