def solve_cvrp(instance):
    def get(obj, *names, default=None):
        if isinstance(obj, dict):
            for n in names:
                if n in obj:
                    return obj[n]
            return default
        for n in names:
            try:
                return obj[n]
            except:
                pass
            try:
                d = obj.__dict__
                if n in d:
                    return d[n]
            except:
                pass
        return default

    depot = get(instance, "depot", "depot_id", default=0)
    demands = get(instance, "demands", "demand", default=None)
    capacity = get(instance, "capacity", "vehicle_capacity", "cap", default=None)
    dist = get(instance, "distance_matrix", "distances", "distance", default=None)
    coords = get(instance, "coords", "coordinates", "points", "locations", default=None)
    customers = get(instance, "customers", "customer_ids", default=None)

    if customers is None:
        if demands is not None:
            if isinstance(demands, dict):
                customers = [k for k in demands.keys() if k != depot]
            else:
                customers = [i for i in range(len(demands)) if i != depot]
        elif coords is not None:
            customers = [i for i in range(len(coords)) if i != depot]
        elif dist is not None:
            customers = [i for i in range(len(dist)) if i != depot]
        else:
            customers = []

    customers = [c for c in customers if c != depot]

    def demand_of(c):
        if demands is None:
            return 1
        if isinstance(demands, dict):
            return demands.get(c, 0)
        if 0 <= c < len(demands):
            return demands[c]
        return 0

    def distance(a, b):
        if dist is not None:
            try:
                return dist[a][b]
            except:
                try:
                    return dist[a, b]
                except:
                    pass
        if coords is not None:
            ax, ay = coords[a]
            bx, by = coords[b]
            dx = ax - bx
            dy = ay - by
            return (dx * dx + dy * dy) ** 0.5
        return 0 if a == b else 1

    if capacity is None:
        total = 0
        for c in customers:
            total += demand_of(c)
        capacity = max(total, 1)

    customers.sort(key=lambda c: (distance(depot, c), demand_of(c), c))

    unserved = customers[:]
    routes = []

    while unserved:
        route = []
        load = 0
        current = depot
        while True:
            best = None
            best_key = None
            for c in unserved:
                d = demand_of(c)
                if load + d > capacity:
                    continue
                key = (distance(current, c), -d, c)
                if best is None or key < best_key:
                    best = c
                    best_key = key
            if best is None:
                break
            route.append(best)
            load += demand_of(best)
            current = best
            unserved.remove(best)
        if not route:
            c = min(unserved, key=lambda x: (demand_of(x), distance(depot, x), x))
            route = [c]
            unserved.remove(c)
        routes.append(route)

    def route_load(route):
        s = 0
        for c in route:
            s += demand_of(c)
        return s

    def route_cost(route):
        if not route:
            return 0
        cost = distance(depot, route[0])
        for i in range(len(route) - 1):
            cost += distance(route[i], route[i + 1])
        cost += distance(route[-1], depot)
        return cost

    def two_opt_route(route):
        n = len(route)
        if n < 4:
            return route[:]
        best = route[:]
        best_cost = route_cost(best)
        improved = True
        while improved:
            improved = False
            for i in range(n - 1):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    cand = best[:i + 1] + best[i + 1:j + 1][::-1] + best[j + 1:]
                    c = route_cost(cand)
                    if c + 1e-12 < best_cost or (abs(c - best_cost) <= 1e-12 and cand < best):
                        best = cand
                        best_cost = c
                        improved = True
                        break
                if improved:
                    break
        return best

    def try_merge_routes(routes):
        changed = True
        while changed:
            changed = False
            best = None
            best_delta = 0
            for i in range(len(routes)):
                for j in range(len(routes)):
                    if i == j:
                        continue
                    ri = routes[i]
                    rj = routes[j]
                    if route_load(ri) + route_load(rj) > capacity:
                        continue
                    for rev_i in (False, True):
                        a = ri[::-1] if rev_i else ri
                        for rev_j in (False, True):
                            b = rj[::-1] if rev_j else rj
                            delta = route_cost(a + b) - route_cost(a) - route_cost(b)
                            key = (delta, i, j, rev_i, rev_j)
                            if best is None or key < best:
                                best = key
                                best_delta = delta
            if best is not None and best_delta < -1e-12:
                _, i, j, rev_i, rev_j = best
                ri = routes[i][::-1] if rev_i else routes[i]
                rj = routes[j][::-1] if rev_j else routes[j]
                new_route = ri + rj
                if i > j:
                    i, j = j, i
                routes[i] = new_route
                routes.pop(j)
                changed = True
        return routes

    routes = [two_opt_route(r) for r in routes if r]
    routes = try_merge_routes(routes)

    seen = set()
    cleaned = []
    for r in routes:
        nr = []
        load = 0
        for c in r:
            if c in seen:
                continue
            d = demand_of(c)
            if load + d <= capacity:
                nr.append(c)
                seen.add(c)
                load += d
        if nr:
            cleaned.append(nr)
    routes = cleaned

    missing = [c for c in customers if c not in seen]
    for c in missing:
        best = None
        best_key = None
        for ri, r in enumerate(routes):
            if route_load(r) + demand_of(c) > capacity:
                continue
            for pos in range(len(r) + 1):
                prev = depot if pos == 0 else r[pos - 1]
                nxt = depot if pos == len(r) else r[pos]
                delta = distance(prev, c) + distance(c, nxt) - distance(prev, nxt)
                key = (delta, ri, pos, c)
                if best is None or key < best_key:
                    best = (ri, pos)
                    best_key = key
        if best is None:
            routes.append([c])
        else:
            ri, pos = best
            routes[ri].insert(pos, c)

    routes = [two_opt_route(r) for r in routes if r]
    routes.sort(key=lambda r: (r[0], len(r), route_cost(r)))
    return routes
