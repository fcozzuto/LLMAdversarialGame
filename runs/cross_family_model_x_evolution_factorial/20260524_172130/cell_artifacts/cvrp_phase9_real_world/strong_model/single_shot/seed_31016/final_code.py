def solve_cvrp(instance):
    # Robust extraction helpers
    def get_any(obj, names, default=None):
        if isinstance(obj, dict):
            for n in names:
                if n in obj:
                    return obj[n]
        return default

    # Parse customers, depot, demands, coordinates, capacity
    customers = get_any(instance, ["customers", "nodes", "customer_ids"], None)
    coords = get_any(instance, ["coords", "coordinates", "locations", "points"], None)
    demands = get_any(instance, ["demands", "demand"], None)
    capacity = get_any(instance, ["capacity", "vehicle_capacity", "cap"], None)
    depot = get_any(instance, ["depot", "depot_id", "source"], 0)

    if customers is None:
        if coords is not None:
            customers = list(range(len(coords)))
        elif demands is not None:
            customers = list(range(len(demands)))
        else:
            customers = []

    if coords is None:
        # Fallback: if no coordinates, use ids as 1D positions for deterministic ordering.
        coords = [(float(i), 0.0) for i in range(max(customers + [depot]) + 1 if customers else 1)]

    if demands is None:
        demands = [0] * (max(customers + [depot]) + 1 if customers else 1)

    if capacity is None:
        capacity = sum(demands[c] for c in customers) if customers else 0

    # Distance function
    def dist(i, j):
        xi, yi = coords[i]
        xj, yj = coords[j]
        dx = xi - xj
        dy = yi - yj
        return (dx * dx + dy * dy) ** 0.5

    # Clean customer list
    customers = [c for c in customers if c != depot]
    customers = sorted(customers)

    # Initial construction: sweep by polar angle around depot, then greedy fill
    dx0, dy0 = coords[depot]
    angles = []
    for c in customers:
        x, y = coords[c]
        ang = 0.0
        if x != dx0 or y != dy0:
            # Deterministic pseudo-angle without imports: quadrant + slope ordering
            vx = x - dx0
            vy = y - dy0
            if vx >= 0 and vy >= 0:
                quad = 0
                key = vy / (abs(vx) + abs(vy) + 1e-12)
            elif vx < 0 <= vy:
                quad = 1
                key = abs(vx) / (abs(vx) + abs(vy) + 1e-12)
            elif vx < 0 and vy < 0:
                quad = 2
                key = vy / (abs(vx) + abs(vy) + 1e-12)
            else:
                quad = 3
                key = abs(vx) / (abs(vx) + abs(vy) + 1e-12)
            ang = quad + key
        angles.append((ang, c))
    angles.sort()

    ordered = [c for _, c in angles]
    unassigned = set(ordered)
    routes = []

    while unassigned:
        route = []
        load = 0
        cur = depot

        # Start with the closest feasible unassigned customer to depot
        feasible = [c for c in unassigned if load + demands[c] <= capacity]
        if not feasible:
            # If demands are inconsistent, force one customer
            c = min(unassigned)
            route.append(c)
            unassigned.remove(c)
            routes.append(route)
            continue

        def best_start():
            best = None
            best_key = None
            for c in feasible:
                key = (dist(depot, c), demands[c], c)
                if best_key is None or key < best_key:
                    best_key = key
                    best = c
            return best

        c = best_start()
        route.append(c)
        load += demands[c]
        cur = c
        unassigned.remove(c)

        while True:
            best = None
            best_key = None
            for n in unassigned:
                if load + demands[n] > capacity:
                    continue
                key = (dist(cur, n), dist(depot, n), demands[n], n)
                if best_key is None or key < best_key:
                    best_key = key
                    best = n
            if best is None:
                break
            route.append(best)
            load += demands[best]
            cur = best
            unassigned.remove(best)

        routes.append(route)

    # Local search utilities
    def route_load(route):
        s = 0
        for c in route:
            s += demands[c]
        return s

    def route_cost(route):
        if not route:
            return 0.0
        total = dist(depot, route[0])
        for i in range(len(route) - 1):
            total += dist(route[i], route[i + 1])
        total += dist(route[-1], depot)
        return total

    def total_cost(rs):
        return sum(route_cost(r) for r in rs)

    # Intra-route 2-opt improvement
    def improve_2opt(route):
        n = len(route)
        if n < 4:
            return route
        improved = True
        while improved:
            improved = False
            best_gain = 0.0
            best_i = best_j = None
            for i in range(n - 1):
                a = depot if i == 0 else route[i - 1]
                b = route[i]
                for j in range(i + 1, n):
                    c = route[j]
                    d = depot if j == n - 1 else route[j + 1]
                    gain = (dist(a, b) + dist(c, d)) - (dist(a, c) + dist(b, d))
                    if gain > best_gain + 1e-12 or (abs(gain - best_gain) <= 1e-12 and (best_i is None or (i, j) < (best_i, best_j))):
                        best_gain = gain
                        best_i, best_j = i, j
            if best_i is not None and best_gain > 1e-12:
                route = route[:best_i] + list(reversed(route[best_i:best_j + 1])) + route[best_j + 1:]
                improved = True
                n = len(route)
        return route

    # Relocate and swap between routes
    def try_relocate(rs):
        best_delta = 0.0
        best_move = None
        m = len(rs)
        loads = [route_load(r) for r in rs]
        for i in range(m):
            ri = rs[i]
            if not ri:
                continue
            for p, c in enumerate(ri):
                prev_c = depot if p == 0 else ri[p - 1]
                next_c = depot if p == len(ri) - 1 else ri[p + 1]
                remove_delta = dist(prev_c, c) + dist(c, next_c) - dist(prev_c, next_c)
                for j in range(m):
                    if i == j:
                        continue
                    rj = rs[j]
                    if loads[j] + demands[c] > capacity:
                        continue
                    for q in range(len(rj) + 1):
                        prev_n = depot if q == 0 else rj[q - 1]
                        next_n = depot if q == len(rj) else rj[q]
                        insert_delta = dist(prev_n, c) + dist(c, next_n) - dist(prev_n, next_n)
                        delta = remove_delta + insert_delta
                        if delta < best_delta - 1e-12:
                            best_delta = delta
                            best_move = (i, p, j, q)
        if best_move is None:
            return False
        i, p, j, q = best_move
        c = rs[i][p]
        if i < j:
            rs[j].insert(q, c)
            rs[i].pop(p)
        else:
            rs[i].pop(p)
            rs[j].insert(q, c)
        return True

    def try_swap(rs):
        best_delta = 0.0
        best_move = None
        m = len(rs)
        loads = [route_load(r) for r in rs]
        for i in range(m):
            ri = rs[i]
            for p, a in enumerate(ri):
                prev_a = depot if p == 0 else ri[p - 1]
                next_a = depot if p == len(ri) - 1 else ri[p + 1]
                rem_a = dist(prev_a, a) + dist(a, next_a) - dist(prev_a, next_a)
                for j in range(i + 1, m):
                    rj = rs[j]
                    for q, b in enumerate(rj):
                        if loads[i] - demands[a] + demands[b] > capacity:
                            continue
                        if loads[j] - demands[b] + demands[a] > capacity:
                            continue
                        prev_b = depot if q == 0 else rj[q - 1]
                        next_b = depot if q == len(rj) - 1 else rj[q + 1]
                        rem_b = dist(prev_b, b) + dist(b, next_b) - dist(prev_b, next_b)

                        add_a = dist(prev_b, a) + dist(a, next_b) - dist(prev_b, next_b)
                        add_b = dist(prev_a, b) + dist(b, next_a) - dist(prev_a, next_a)
                        delta = (add_a + add_b) - (rem_a + rem_b)
                        if delta < best_delta - 1e-12:
                            best_delta = delta
                            best_move = (i, p, j, q)
        if best_move is None:
            return False
        i, p, j, q = best_move
        a = rs[i][p]
        b = rs[j][q]
        rs[i][p] = b
        rs[j][q] = a
        return True

    # Optimize routes
    routes = [improve_2opt(r) for r in routes]

    improved = True
    iter_limit = 2000
    it = 0
    while improved and it < iter_limit:
        improved = False
        it += 1
        if try_relocate(routes):
            routes = [improve_2opt(r) for r in routes]
            improved = True
            continue
        if try_swap(routes):
            routes = [improve_2opt(r) for r in routes]
            improved = True
            continue

    # Final repair: remove empties and ensure all customers present exactly once
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
    if missing:
        # Deterministically insert missing customers into best feasible position
        for c in missing:
            best = None
            best_key = None
