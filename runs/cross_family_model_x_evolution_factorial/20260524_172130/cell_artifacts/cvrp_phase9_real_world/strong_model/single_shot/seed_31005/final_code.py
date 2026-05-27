def solve_cvrp(instance):
    def get_value(obj, name, default=None):
        if isinstance(obj, dict):
            return obj.get(name, default)
        try:
            return obj.__dict__.get(name, default)
        except:
            try:
                return obj[name]
            except:
                return default

    def as_list(x):
        if x is None:
            return []
        if isinstance(x, list):
            return x
        if isinstance(x, tuple):
            return list(x)
        try:
            return list(x)
        except:
            return [x]

    depot = get_value(instance, "depot", 0)
    capacity = get_value(instance, "capacity", get_value(instance, "vehicle_capacity", None))

    demands = get_value(instance, "demands", get_value(instance, "demand", None))
    coords = get_value(instance, "coordinates", get_value(instance, "coords", get_value(instance, "points", None)))
    dist = get_value(instance, "distance_matrix", get_value(instance, "distances", get_value(instance, "matrix", None)))

    customers = get_value(instance, "customers", None)
    if customers is None:
        if isinstance(demands, dict):
            customers = [k for k in demands.keys() if k != depot]
        elif isinstance(demands, (list, tuple)):
            customers = [i for i in range(len(demands)) if i != depot]
        elif isinstance(coords, dict):
            customers = [k for k in coords.keys() if k != depot]
        else:
            customers = []
    customers = [c for c in as_list(customers) if c != depot]

    def demand_of(c):
        if demands is None:
            return 1
        if isinstance(demands, dict):
            return demands.get(c, 0)
        try:
            return demands[c]
        except:
            return 0

    def point_of(n):
        if coords is None:
            return None
        if isinstance(coords, dict):
            return coords.get(n, None)
        try:
            return coords[n]
        except:
            return None

    def dist_lookup(a, b):
        if dist is not None:
            try:
                if isinstance(dist, dict):
                    da = dist.get(a, None)
                    if isinstance(da, dict):
                        return da.get(b, 0)
                    db = dist.get(b, None)
                    if isinstance(db, dict):
                        return db.get(a, 0)
                else:
                    return dist[a][b]
            except:
                pass
        pa = point_of(a)
        pb = point_of(b)
        if pa is not None and pb is not None and len(pa) >= 2 and len(pb) >= 2:
            dx = pa[0] - pb[0]
            dy = pa[1] - pb[1]
            return dx * dx + dy * dy
        return 0 if a == b else 1

    if capacity is None:
        capacity = 10 ** 18

    unserved = set(customers)
    routes = []

    while unserved:
        route = []
        load = 0
        current = depot

        feasible = [c for c in unserved if load + demand_of(c) <= capacity]
        if not feasible:
            feasible = list(unserved)
        start = min(feasible, key=lambda c: (dist_lookup(depot, c), -demand_of(c), c))
        route.append(start)
        unserved.remove(start)
        load += demand_of(start)
        current = start

        while True:
            feasible = [c for c in unserved if load + demand_of(c) <= capacity]
            if not feasible:
                break
            nxt = min(feasible, key=lambda c: (dist_lookup(current, c), dist_lookup(depot, c), c))
            route.append(nxt)
            unserved.remove(nxt)
            load += demand_of(nxt)
            current = nxt

        routes.append(route)

    def route_load(route):
        s = 0
        for c in route:
            s += demand_of(c)
        return s

    def route_cost(route):
        if not route:
            return 0
        total = dist_lookup(depot, route[0])
        for i in range(len(route) - 1):
            total += dist_lookup(route[i], route[i + 1])
        total += dist_lookup(route[-1], depot)
        return total

    def two_opt(route):
        n = len(route)
        if n < 4:
            return route[:]
        best = route[:]
        best_cost = route_cost(best)
        improved = True
        while improved:
            improved = False
            for i in range(n - 2):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    cand = best[:i + 1] + best[i + 1:j + 1][::-1] + best[j + 1:]
                    c = route_cost(cand)
                    if c < best_cost:
                        best = cand
                        best_cost = c
                        improved = True
                        break
                if improved:
                    break
        return best

    routes = [two_opt(r) for r in routes]

    improved = True
    while improved:
        improved = False

        best_delta = 0
        best_move = None
        for i in range(len(routes)):
            ri = routes[i]
            for p, c in enumerate(ri):
                dc = demand_of(c)
                base_i = route_cost(ri)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    if route_load(rj) + dc > capacity:
                        continue
                    base_j = route_cost(rj)
                    ri2 = ri[:p] + ri[p + 1:]
                    if ri2:
                        ri2 = two_opt(ri2)
                    for q in range(len(rj) + 1):
                        rj2 = rj[:q] + [c] + rj[q:]
                        rj2 = two_opt(rj2)
                        delta = (route_cost(ri2) + route_cost(rj2)) - (base_i + base_j)
                        if delta < best_delta:
                            best_delta = delta
                            best_move = (i, j, ri2, rj2)
        if best_move is not None:
            i, j, ri2, rj2 = best_move
            routes[i] = ri2
            routes[j] = rj2
            routes = [r for r in routes if r]
            improved = True
            continue

        best_delta = 0
        best_swap = None
        m = len(routes)
        for i in range(m):
            for j in range(i + 1, m):
                ri = routes[i]
                rj = routes[j]
                li = route_load(ri)
                lj = route_load(rj)
                base = route_cost(ri) + route_cost(rj)
                for p, a in enumerate(ri):
                    da = demand_of(a)
                    for q, b in enumerate(rj):
                        db = demand_of(b)
                        if li - da + db > capacity or lj - db + da > capacity:
                            continue
                        ri2 = ri[:p] + [b] + ri[p + 1:]
                        rj2 = rj[:q] + [a] + rj[q + 1:]
                        ri2 = two_opt(ri2)
                        rj2 = two_opt(rj2)
                        delta = (route_cost(ri2) + route_cost(rj2)) - base
                        if delta < best_delta:
                            best_delta = delta
                            best_swap = (i, j, ri2, rj2)
        if best_swap is not None:
            i, j, ri2, rj2 = best_swap
            routes[i] = ri2
            routes[j] = rj2
            routes = [r for r in routes if r]
            improved = True

    seen = set()
    cleaned = []
    for r in routes:
        rr = []
        for c in r:
            if c != depot and c not in seen:
                rr.append(c)
                seen.add(c)
        if rr:
            cleaned.append(rr)

    missing = [c for c in customers if c not in seen]
    for c in missing:
        placed = False
        for r in cleaned:
            if route_load(r) + demand_of(c) <= capacity:
                best_pos = 0
                best_inc = None
                base = route_cost(r)
                for pos in range(len(r) + 1):
                    cand = r[:pos] + [c] + r[pos:]
                    inc = route_cost(cand) - base
                    if best_inc is None or inc < best_inc or (inc == best_inc and pos < best_pos):
                        best_inc = inc
                        best_pos = pos
                r.insert(best_pos, c)
                placed = True
                break
        if not placed:
            cleaned.append([c])

    return cleaned
