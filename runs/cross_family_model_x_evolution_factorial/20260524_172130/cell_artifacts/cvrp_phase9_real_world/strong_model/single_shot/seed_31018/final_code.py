def solve_cvrp(instance):
    def _get(d, keys, default=None):
        if isinstance(d, dict):
            for k in keys:
                if k in d:
                    return d[k]
        return default

    def _is_num(x):
        return isinstance(x, (int, float))

    def _as_list_ids(ids):
        return list(ids) if ids is not None else []

    depot = _get(instance, ["depot", "depot_id", "start", "origin"], 0)
    capacity = _get(instance, ["capacity", "vehicle_capacity", "Q"], None)

    coords = _get(instance, ["coordinates", "coords", "locations", "points"], None)
    demands = _get(instance, ["demands", "demand"], None)

    coord_map = {}
    demand_map = {}

    if isinstance(coords, dict):
        for k, v in coords.items():
            coord_map[k] = (v[0], v[1])
    elif isinstance(coords, (list, tuple)):
        for i, v in enumerate(coords):
            if v is not None:
                coord_map[i] = (v[0], v[1])

    if isinstance(demands, dict):
        for k, v in demands.items():
            demand_map[k] = v
    elif isinstance(demands, (list, tuple)):
        for i, v in enumerate(demands):
            demand_map[i] = v

    if depot not in coord_map:
        if isinstance(instance, dict):
            if depot in instance and isinstance(instance[depot], (list, tuple)) and len(instance[depot]) >= 2:
                coord_map[depot] = (instance[depot][0], instance[depot][1])

    if capacity is None:
        capacity = 0
        if demand_map:
            capacity = max(demand_map.values()) if demand_map else 0

    customer_ids = _get(instance, ["customers", "customer_ids", "nodes"], None)
    if customer_ids is None:
        customer_ids = []
        for k in coord_map.keys():
            if k != depot:
                customer_ids.append(k)
        if not customer_ids and isinstance(instance, dict):
            for k in instance.keys():
                if k != depot and k not in ("depot", "depot_id", "start", "origin", "capacity", "vehicle_capacity", "Q", "coordinates", "coords", "locations", "points", "demands", "demand"):
                    if _is_num(k):
                        customer_ids.append(k)

    customer_ids = list(customer_ids)
    if depot in customer_ids:
        customer_ids = [c for c in customer_ids if c != depot]

    def coord(n):
        return coord_map[n]

    def demand(n):
        return demand_map.get(n, 0)

    def dist(a, b):
        ax, ay = coord(a)
        bx, by = coord(b)
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    all_customers = sorted(customer_ids, key=lambda x: (demand(x), x))

    # Initial constructive phase: greedy route growing from nearest feasible customer
    unassigned = set(all_customers)
    routes = []

    if not unassigned:
        return []

    while unassigned:
        start = min(unassigned, key=lambda c: (dist(depot, c), demand(c), c))
        route = [start]
        load = demand(start)
        unassigned.remove(start)
        last = start

        while True:
            best = None
            best_key = None
            for c in unassigned:
                dc = demand(c)
                if load + dc > capacity:
                    continue
                key = (dist(last, c), dist(depot, c), dc, c)
                if best is None or key < best_key:
                    best = c
                    best_key = key
            if best is None:
                break
            route.append(best)
            load += demand(best)
            unassigned.remove(best)
            last = best

        routes.append(route)

    def route_load(route):
        s = 0
        for c in route:
            s += demand(c)
        return s

    def route_distance(route):
        if not route:
            return 0.0
        total = dist(depot, route[0])
        for i in range(len(route) - 1):
            total += dist(route[i], route[i + 1])
        total += dist(route[-1], depot)
        return total

    def two_opt_route(route):
        n = len(route)
        if n < 4:
            return route[:]
        best = route[:]
        best_cost = route_distance(best)
        improved = True
        while improved:
            improved = False
            for i in range(n - 2):
                for k in range(i + 2, n):
                    if i == 0 and k == n - 1:
                        continue
                    cand = best[:i + 1] + best[i + 1:k + 1][::-1] + best[k + 1:]
                    cand_cost = route_distance(cand)
                    if cand_cost + 1e-12 < best_cost:
                        best = cand
                        best_cost = cand_cost
                        improved = True
                        break
                if improved:
                    break
        return best

    def total_cost(rs):
        return sum(route_distance(r) for r in rs)

    # Local search: intra-route 2-opt
    for i in range(len(routes)):
        routes[i] = two_opt_route(routes[i])

    # Inter-route relocate and swap
    def try_relocate(rs):
        base = total_cost(rs)
        for i in range(len(rs)):
            r1 = rs[i]
            l1 = route_load(r1)
            for pos in range(len(r1)):
                c = r1[pos]
                dc = demand(c)
                for j in range(len(rs)):
                    if i == j:
                        continue
                    r2 = rs[j]
                    l2 = route_load(r2)
                    if l2 + dc > capacity:
                        continue
                    for ins in range(len(r2) + 1):
                        nr1 = r1[:pos] + r1[pos + 1:]
                        nr2 = r2[:ins] + [c] + r2[ins:]
                        new_rs = rs[:]
                        new_rs[i] = nr1
                        new_rs[j] = nr2
                        new_cost = total_cost(new_rs)
                        if new_cost + 1e-12 < base:
                            return new_rs
        return None

    def try_swap(rs):
        base = total_cost(rs)
        for i in range(len(rs)):
            r1 = rs[i]
            l1 = route_load(r1)
            for p1 in range(len(r1)):
                a = r1[p1]
                da = demand(a)
                for j in range(i + 1, len(rs)):
                    r2 = rs[j]
                    l2 = route_load(r2)
                    for p2 in range(len(r2)):
                        b = r2[p2]
                        db = demand(b)
                        if l1 - da + db > capacity:
                            continue
                        if l2 - db + da > capacity:
                            continue
                        nr1 = r1[:]
                        nr2 = r2[:]
                        nr1[p1] = b
                        nr2[p2] = a
                        new_rs = rs[:]
                        new_rs[i] = nr1
                        new_rs[j] = nr2
                        new_cost = total_cost(new_rs)
                        if new_cost + 1e-12 < base:
                            return new_rs
        return None

    # Improvement loop
    changed = True
    while changed:
        changed = False
        for i in range(len(routes)):
            routes[i] = two_opt_route(routes[i])

        new_routes = try_relocate(routes)
        if new_routes is not None:
            routes = new_routes
            changed = True
            continue

        new_routes = try_swap(routes)
        if new_routes is not None:
            routes = new_routes
            changed = True
            continue

    # Final cleanup: remove any empty routes
    routes = [r for r in routes if r]
    return routes
