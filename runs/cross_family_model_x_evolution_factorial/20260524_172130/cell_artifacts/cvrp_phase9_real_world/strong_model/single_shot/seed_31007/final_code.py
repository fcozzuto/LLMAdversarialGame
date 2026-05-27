def solve_cvrp(instance):
    depot = instance.get("depot", 0)
    capacity = instance.get("capacity", instance.get("vehicle_capacity", None))
    demands = instance.get("demands", {})
    distance_matrix = instance.get("distance_matrix", None)
    coords = instance.get("coords", instance.get("positions", instance.get("locations", None)))

    def is_number(x):
        return isinstance(x, (int, float))

    def get_customer_ids():
        if "customers" in instance and instance["customers"] is not None:
            return [c for c in instance["customers"] if c != depot]
        ids = []
        if isinstance(demands, dict):
            for k in demands:
                if k != depot:
                    ids.append(k)
        elif isinstance(coords, dict):
            for k in coords:
                if k != depot:
                    ids.append(k)
        elif isinstance(coords, list):
            ids = list(range(len(coords)))
            if depot in ids:
                ids.remove(depot)
        elif isinstance(distance_matrix, list):
            ids = list(range(len(distance_matrix)))
            if depot in ids:
                ids.remove(depot)
        return ids

    customer_ids = get_customer_ids()

    def demand_of(c):
        if isinstance(demands, dict):
            return demands.get(c, 0)
        if isinstance(demands, list) and 0 <= c < len(demands):
            return demands[c]
        return 0

    def pos_of(c):
        if coords is None:
            return None
        if isinstance(coords, dict):
            return coords.get(c, None)
        if isinstance(coords, list) and 0 <= c < len(coords):
            return coords[c]
        return None

    def dist(a, b):
        if distance_matrix is not None:
            try:
                return distance_matrix[a][b]
            except Exception:
                pass
        pa = pos_of(a)
        pb = pos_of(b)
        if pa is not None and pb is not None and len(pa) >= 2 and len(pb) >= 2:
            dx = pa[0] - pb[0]
            dy = pa[1] - pb[1]
            return (dx * dx + dy * dy) ** 0.5
        if is_number(a) and is_number(b):
            return abs(a - b)
        return 0

    def route_load(route):
        s = 0
        for c in route:
            s += demand_of(c)
        return s

    def route_cost(route):
        if not route:
            return 0
        total = dist(depot, route[0])
        for i in range(len(route) - 1):
            total += dist(route[i], route[i + 1])
        total += dist(route[-1], depot)
        return total

    def nearest_feasible(current, remaining, load):
        best = None
        best_key = None
        for c in remaining:
            d = demand_of(c)
            if load + d > capacity:
                continue
            key = (dist(current, c), -d, c)
            if best_key is None or key < best_key:
                best_key = key
                best = c
        return best

    remaining = set(customer_ids)
    routes = []

    # Constructive phase: seed with heavy customers, extend by nearest feasible.
    while remaining:
        seed = None
        seed_key = None
        for c in remaining:
            d = demand_of(c)
            if d > capacity:
                continue
            key = (-d, dist(depot, c), c)
            if seed_key is None or key < seed_key:
                seed_key = key
                seed = c
        if seed is None:
            # Fallback: place one customer alone to avoid infinite loop.
            seed = min(remaining, key=lambda c: (demand_of(c), c))
        route = [seed]
        remaining.remove(seed)
        load = demand_of(seed)
        current = seed
        while True:
            nxt = nearest_feasible(current, remaining, load)
            if nxt is None:
                break
            route.append(nxt)
            remaining.remove(nxt)
            load += demand_of(nxt)
            current = nxt
        routes.append(route)

    def improve_within_route(route):
        if len(route) < 4:
            return route[:]
        best = route[:]
        best_cost = route_cost(best)
        improved = True
        while improved:
            improved = False
            n = len(best)
            for i in range(n - 1):
                for k in range(i + 1, n):
                    cand = best[:i] + best[i:k + 1][::-1] + best[k + 1:]
                    c = route_cost(cand)
                    if c + 1e-12 < best_cost:
                        best = cand
                        best_cost = c
                        improved = True
                        break
                if improved:
                    break
        return best

    # Local search: relocate and swap between routes, plus intra-route 2-opt.
    routes = [improve_within_route(r) for r in routes]

    def total_cost(rs):
        s = 0
        for r in rs:
            s += route_cost(r)
        return s

    improved = True
    while improved:
        improved = False

        # Intra-route 2-opt
        for i in range(len(routes)):
            new_r = improve_within_route(routes[i])
            if route_cost(new_r) + 1e-12 < route_cost(routes[i]):
                routes[i] = new_r
                improved = True

        # Inter-route relocate
        outer_break = False
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j:
                    continue
                ri = routes[i]
                rj = routes[j]
                li = route_load(ri)
                lj = route_load(rj)
                for a in range(len(ri)):
                    c = ri[a]
                    dc = demand_of(c)
                    for pos in range(len(rj) + 1):
                        if lj + dc > capacity:
                            continue
                        new_ri = ri[:a] + ri[a + 1:]
                        new_rj = rj[:pos] + [c] + rj[pos:]
                        if not new_ri:
                            continue
                        old = route_cost(ri) + route_cost(rj)
                        new = route_cost(new_ri) + route_cost(new_rj)
                        if new + 1e-12 < old:
                            routes[i] = new_ri
                            routes[j] = improve_within_route(new_rj)
                            improved = True
                            outer_break = True
                            break
                    if outer_break:
                        break
                if outer_break:
                    break
            if outer_break:
                break

        if improved:
            continue

        # Inter-route swap
        outer_break = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                ri = routes[i]
                rj = routes[j]
                li = route_load(ri)
                lj = route_load(rj)
                for a in range(len(ri)):
                    ca = ri[a]
                    da = demand_of(ca)
                    for b in range(len(rj)):
                        cb = rj[b]
                        db = demand_of(cb)
                        if li - da + db > capacity:
                            continue
                        if lj - db + da > capacity:
                            continue
                        new_ri = ri[:a] + [cb] + ri[a + 1:]
                        new_rj = rj[:b] + [ca] + rj[b + 1:]
                        old = route_cost(ri) + route_cost(rj)
                        new = route_cost(new_ri) + route_cost(new_rj)
                        if new + 1e-12 < old:
                            routes[i] = improve_within_route(new_ri)
                            routes[j] = improve_within_route(new_rj)
                            improved = True
                            outer_break = True
                            break
                    if outer_break:
                        break
                if outer_break:
                    break
            if outer_break:
                break

    # Final cleanup: remove any empty routes and ensure all customers appear once.
    final_routes = []
    seen = set()
    for r in routes:
        nr = []
        load = 0
        for c in r:
            if c in seen:
                continue
            if load + demand_of(c) <= capacity:
                nr.append(c)
                seen.add(c)
                load += demand_of(c)
        if nr:
            final_routes.append(nr)

    missing = [c for c in customer_ids if c not in seen]
    for c in missing:
        placed = False
        for r in final_routes:
            if route_load(r) + demand_of(c) <= capacity:
                best_pos = None
                best_inc = None
                base = route_cost(r)
                for pos in range(len(r) + 1):
                    cand = r[:pos] + [c] + r[pos:]
                    inc = route_cost(cand) - base
                    if best_inc is None or inc < best_inc or (inc == best_inc and pos < best_pos):
                        best_inc = inc
                        best_pos = pos
                if best_pos is not None:
                    r[:] = r[:best_pos] + [c] + r[best_pos:]
                    placed = True
                    break
        if not placed:
            final_routes.append([c])

    return final_routes
