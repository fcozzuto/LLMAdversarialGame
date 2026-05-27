def solve_cvrp(instance):
    def get_item(obj, keys, default=None):
        if isinstance(obj, dict):
            for k in keys:
                if k in obj:
                    return obj[k]
        return default

    def is_num(x):
        return isinstance(x, (int, float)) and not isinstance(x, bool)

    # --- Parse instance ---
    cap = get_item(instance, ["capacity", "vehicle_capacity", "Q", "cap"], None)
    depot_id = get_item(instance, ["depot_id", "depot", "depot_index"], 0)

    coords = get_item(instance, ["coords", "coordinates", "locations", "points", "xy"], None)
    dist_matrix = get_item(instance, ["distance_matrix", "distances", "cost_matrix"], None)

    demands_raw = get_item(instance, ["demands", "demand"], None)
    customers = get_item(instance, ["customers", "customer_ids", "nodes"], None)

    # Build node set
    if customers is None:
        if isinstance(demands_raw, dict):
            customers = [k for k in demands_raw.keys() if k != depot_id]
        elif isinstance(coords, dict):
            customers = [k for k in coords.keys() if k != depot_id]
        elif isinstance(dist_matrix, list):
            customers = list(range(len(dist_matrix)))
            if depot_id in customers:
                customers.remove(depot_id)
        else:
            customers = []
    else:
        customers = [c for c in customers if c != depot_id]

    # Demands accessor
    if isinstance(demands_raw, dict):
        demand = lambda i: demands_raw.get(i, 0)
    elif isinstance(demands_raw, list):
        demand = lambda i: demands_raw[i] if 0 <= i < len(demands_raw) else 0
    else:
        demand = lambda i: 0

    # Coordinates accessor
    if isinstance(coords, dict):
        def xy(i):
            p = coords.get(i, None)
            if p is None:
                return (0.0, 0.0)
            return (float(p[0]), float(p[1]))
    elif isinstance(coords, list):
        def xy(i):
            p = coords[i]
            return (float(p[0]), float(p[1]))
    else:
        def xy(i):
            return (0.0, 0.0)

    def dist(i, j):
        if isinstance(dist_matrix, dict):
            row = dist_matrix.get(i, None)
            if row is not None:
                if isinstance(row, dict):
                    v = row.get(j, None)
                    if v is not None:
                        return float(v)
        elif isinstance(dist_matrix, list):
            if 0 <= i < len(dist_matrix) and 0 <= j < len(dist_matrix[i]):
                return float(dist_matrix[i][j])
        xi, yi = xy(i)
        xj, yj = xy(j)
        dx = xi - xj
        dy = yi - yj
        return (dx * dx + dy * dy) ** 0.5

    if cap is None:
        total = 0
        for c in customers:
            total += demand(c)
        cap = total if total > 0 else 1

    # Filter customers with positive demand and deterministic ordering
    customers = [c for c in customers if demand(c) > 0]
    if not customers:
        return []

    # --- Clarke-Wright savings (interpretable constructive phase) ---
    routes = [[c] for c in customers]
    route_of = {c: idx for idx, c in enumerate(customers)}
    route_load = [demand(c) for c in customers]
    active = [True] * len(routes)

    # Precompute savings
    savings = []
    for i in range(len(customers)):
        a = customers[i]
        for j in range(i + 1, len(customers)):
            b = customers[j]
            s = dist(depot_id, a) + dist(depot_id, b) - dist(a, b)
            savings.append((s, a, b))
    savings.sort(key=lambda x: (-x[0], x[1], x[2]))

    def route_ends(rt):
        return rt[0], rt[-1]

    def merge_routes(ra, rb, a, b):
        # Join route containing a with route containing b if a/b are endpoints
        if not active[ra] or not active[rb] or ra == rb:
            return False
        A = routes[ra]
        B = routes[rb]
        la = route_load[ra]
        lb = route_load[rb]
        if la + lb > cap:
            return False
        a_first, a_last = route_ends(A)
        b_first, b_last = route_ends(B)

        # Four possible endpoint orientations
        if a_last == a and b_first == b:
            newr = A + B
        elif a_first == a and b_last == b:
            newr = B + A
        elif a_first == a and b_first == b:
            newr = list(reversed(A)) + B
        elif a_last == a and b_last == b:
            newr = A + list(reversed(B))
        else:
            return False

        routes[ra] = newr
        route_load[ra] = la + lb
        active[rb] = False
        for c in newr:
            route_of[c] = ra
        return True

    for s, a, b in savings:
        ra = route_of[a]
        rb = route_of[b]
        if ra != rb:
            merge_routes(ra, rb, a, b)

    routes = [routes[i] for i in range(len(routes)) if active[i]]

    # --- Repair/pack leftovers if any customer missing (defensive) ---
    assigned = {}
    for rt in routes:
        for c in rt:
            assigned[c] = True
    missing = [c for c in customers if c not in assigned]
    for c in missing:
        placed = False
        for rt in routes:
            load = 0
            for x in rt:
                load += demand(x)
            if load + demand(c) <= cap:
                rt.append(c)
                placed = True
                break
        if not placed:
            routes.append([c])

    # --- Local search: route-internal 2-opt ---
    def route_cost(rt):
        if not rt:
            return 0.0
        cost = dist(depot_id, rt[0])
        for i in range(len(rt) - 1):
            cost += dist(rt[i], rt[i + 1])
        cost += dist(rt[-1], depot_id)
        return cost

    def two_opt(rt):
        n = len(rt)
        if n < 4:
            return rt
        improved = True
        best = rt[:]
        best_cost = route_cost(best)
        while improved:
            improved = False
            for i in range(n - 2):
                for k in range(i + 2, n):
                    if i == 0 and k == n - 1:
                        continue
                    cand = best[:i + 1] + best[i + 1:k + 1][::-1] + best[k + 1:]
                    c = route_cost(cand)
                    if c + 1e-12 < best_cost:
                        best = cand
                        best_cost = c
                        improved = True
                        break
                if improved:
                    break
        return best

    # Small deterministic inter-route repair: swap tail/insert if it helps and keeps capacity.
    def route_load_of(rt):
        s = 0
        for c in rt:
            s += demand(c)
        return s

    changed = True
    while changed:
        changed = False
        for i in range(len(routes)):
            routes[i] = two_opt(routes[i])

        # relocate one customer if it improves total cost
        best_delta = 0.0
        best_move = None
        loads = [route_load_of(rt) for rt in routes]
        for i in range(len(routes)):
            ri = routes[i]
            for p in range(len(ri)):
                c = ri[p]
                dc = demand(c)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    if loads[j] + dc > cap:
                        continue
                    base = route_cost(ri) + route_cost(rj)
                    ri2 = ri[:p] + ri[p + 1:]
                    if len(ri2) == 0:
                        continue
                    for ins in range(len(rj) + 1):
                        rj2 = rj[:ins] + [c] + rj[ins:]
                        newc = route_cost(ri2) + route_cost(rj2)
                        delta = newc - base
                        if delta < best_delta:
                            best_delta = delta
                            best_move = (i, j, p, ins, ri2, rj2)
        if best_move is not None:
            i, j, p, ins, ri2, rj2 = best_move
            routes[i] = ri2
            routes[j] = rj2
            changed = True
            routes = [rt for rt in routes if len(rt) > 0]

    # Final cleanup: remove empty routes and ensure all customers appear once
    seen = {}
    final_routes = []
    for rt in routes:
        clean = []
        for c in rt:
            if c not in seen:
                seen[c] = True
                clean.append(c)
        if clean:
            final_routes.append(clean)

    for c in customers:
        if c not in seen:
            placed = False
            for rt in final_routes:
                if route_load_of(rt) + demand(c) <= cap:
                    rt.append(c)
                    placed = True
                    break
            if not placed:
                final_routes.append([c])

    return final_routes
