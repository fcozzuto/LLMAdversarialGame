def solve_cvrp(instance):
    def fetch(obj, names, default=None):
        try:
            for n in names:
                try:
                    return obj[n]
                except:
                    pass
        except:
            pass
        try:
            d = obj.__dict__
            for n in names:
                try:
                    return d[n]
                except:
                    pass
        except:
            pass
        return default

    def to_list(x):
        if x is None:
            return []
        try:
            return list(x)
        except:
            return [x]

    def as_float(x, default=0.0):
        try:
            return float(x)
        except:
            return default

    def coord_pair(v):
        try:
            a, b = v
            return as_float(a), as_float(b)
        except:
            return None

    def dist(a, b):
        if a is None or b is None:
            return 0.0
        pa = coord_pair(a)
        pb = coord_pair(b)
        if pa is None or pb is None:
            return 0.0
        dx = pa[0] - pb[0]
        dy = pa[1] - pb[1]
        return (dx * dx + dy * dy) ** 0.5

    coords = fetch(instance, ("coords", "coordinates", "locations", "pos", "positions"), None)
    demands = fetch(instance, ("demands", "demand"), None)
    capacity = fetch(instance, ("capacity", "vehicle_capacity"), None)
    depot_id = fetch(instance, ("depot", "depot_id"), 0)

    demand_of = {}
    coord_of = {}
    customer_ids = []

    if demands is not None:
        try:
            for k in demands:
                if k != depot_id:
                    customer_ids.append(k)
                    try:
                        demand_of[k] = as_float(demands[k], 0.0)
                    except:
                        demand_of[k] = 0.0
        except:
            dlist = to_list(demands)
            start = 1 if depot_id == 0 and len(dlist) > 0 else 0
            for i in range(start, len(dlist)):
                customer_ids.append(i)
                demand_of[i] = as_float(dlist[i], 0.0)
    else:
        customers = fetch(instance, ("customers", "nodes"), [])
        customer_ids = [c for c in to_list(customers) if c != depot_id]
        for c in customer_ids:
            demand_of[c] = 0.0

    if coords is not None:
        try:
            for k in coords:
                coord_of[k] = coords[k]
                if k != depot_id and k not in customer_ids:
                    customer_ids.append(k)
        except:
            clist = to_list(coords)
            start = 1 if depot_id == 0 and len(clist) > 0 else 0
            for i in range(start, len(clist)):
                coord_of[i] = clist[i]
                if i not in customer_ids:
                    customer_ids.append(i)

    customer_ids = sorted(set(customer_ids))

    total_demand = 0.0
    for c in customer_ids:
        total_demand += as_float(demand_of.get(c, 0.0), 0.0)

    if capacity is None:
        capacity = total_demand if total_demand > 0 else 1.0
    capacity = as_float(capacity, total_demand if total_demand > 0 else 1.0)
    if capacity <= 0:
        capacity = total_demand if total_demand > 0 else 1.0

    depot_coord = coord_of.get(depot_id, None)

    def route_load(route):
        s = 0.0
        for c in route:
            s += as_float(demand_of.get(c, 0.0), 0.0)
        return s

    def route_cost(route):
        prev = depot_coord
        cst = 0.0
        for c in route:
            cc = coord_of.get(c, None)
            cst += dist(prev, cc)
            prev = cc
        cst += dist(prev, depot_coord)
        return cst

    if not customer_ids:
        return []

    # Deterministic ordering: angle from depot if available, else id.
    order = customer_ids[:]
    if depot_coord is not None:
        def ang_key(c):
            p = coord_of.get(c, None)
            pp = coord_pair(p)
            dp = coord_pair(depot_coord)
            if pp is None or dp is None:
                return (1, c)
            dx = pp[0] - dp[0]
            dy = pp[1] - dp[1]
            ang = 0.0
            if dx != 0.0 or dy != 0.0:
                ang = dy / (abs(dx) + abs(dy))
            return (0, ang, (dx * dx + dy * dy) ** 0.5, c)
        order.sort(key=ang_key)
    else:
        order.sort()

    # Constructive: sweep/cheapest insertion hybrid.
    routes = []
    current = []
    current_load = 0.0
    for c in order:
        d = as_float(demand_of.get(c, 0.0), 0.0)
        if current and current_load + d > capacity + 1e-12:
            routes.append(current)
            current = []
            current_load = 0.0
        current.append(c)
        current_load += d
    if current:
        routes.append(current)

    # Repair: split any overloaded route greedily.
    repaired = []
    for r in routes:
        cur = []
        load = 0.0
        for c in r:
            d = as_float(demand_of.get(c, 0.0), 0.0)
            if cur and load + d > capacity + 1e-12:
                repaired.append(cur)
                cur = [c]
                load = d
            else:
                cur.append(c)
                load += d
        if cur:
            repaired.append(cur)
    routes = repaired

    # Local search: relocate within and across routes if improves.
    def best_insertion_pos(route, c):
        base = route_cost(route)
        best_pos = 0
        best_delta = None
        for k in range(len(route) + 1):
            cand = route[:k] + [c] + route[k:]
            delta = route_cost(cand) - base
            if best_delta is None or delta < best_delta or (delta == best_delta and k < best_pos):
                best_delta = delta
                best_pos = k
        return best_pos, best_delta

    changed = True
    it = 0
    while changed and it < 3:
        changed = False
        it += 1
        # Intra-route 2-opt-like reversal
        for i in range(len(routes)):
            r = routes[i]
            best = r
            best_cost = route_cost(r)
            n = len(r)
            for a in range(n):
                for b in range(a + 2, n + 1):
                    cand = r[:a] + r[a:b][::-1] + r[b:]
                    cc = route_cost(cand)
                    if cc + 1e-12 < best_cost:
                        best = cand
                        best_cost = cc
            if best != r:
                routes[i] = best
                changed = True

        # Inter-route relocate
        for i in range(len(routes)):
            j = 0
            while j < len(routes[i]):
                c = routes[i][j]
                d = as_float(demand_of.get(c, 0.0), 0.0)
                best_move = None
                best_gain = 0.0
                for r2 in range(len(routes)):
                    if r2 == i:
                        continue
                    if route_load(routes[r2]) + d > capacity + 1e-12:
                        continue
                    r1 = routes[i]
                    if len(r1) <= 1:
                        continue
                    for pos in range(len(routes[r2]) + 1):
                        cand2 = routes[r2][:pos] + [c] + routes[r2][pos:]
                        gain = (route_cost(r1) + route_cost(routes[r2])) - (route_cost(r1[:j] + r1[j+1:]) + route_cost(cand2))
                        if gain > best_gain + 1e-12:
                            best_gain = gain
                            best_move = (r2, pos)
                if best_move is not None:
                    r2, pos = best_move
                    routes[r2] = routes[r2][:pos] + [c] + routes[r2][pos:]
                    routes[i] = routes[i][:j] + routes[i][j+1:]
                    changed = True
                    if not routes[i]:
                        del routes[i]
                        i -= 1
                        break
                    continue
                j += 1

    # Final cleanup: remove empties, sort routes by first visit deterministically.
    routes = [r for r in routes if r]
    routes.sort(key=lambda r: (r[0], len(r)))

    # Absolute guarantee: cover all customers once.
    seen = {}
    for r in routes:
        for c in r:
            seen[c] = seen.get(c, 0) + 1

    missing = [c for c in customer_ids if c not in seen]
    if missing:
        # Insert missing customers into feasible routes or new routes.
        for c in missing:
            d = as_float(demand_of.get(c, 0.0), 0.0)
            best_r = None
            best_pos = None
            best_delta = None
            for ri in range(len(routes)):
                if route_load(routes[ri]) + d > capacity + 1e-12:
                    continue
                pos, delta = best_insertion_pos(routes[ri], c)
                if best_delta is None or delta < best_delta:
                    best_delta = delta
                    best_r = ri
                    best_pos = pos
            if best_r is None:
                routes.append([c])
            else:
                routes[best_r] = routes[best_r][:best_pos] + [c] + routes[best_r][best_pos:]

    # If duplicates exist, keep first occurrence and remove later duplicates.
    assigned = {}
    cleaned = []
