def solve_cvrp(instance):
    # ---------- helpers ----------
    def get(obj, *keys, default=None):
        if isinstance(obj, dict):
            for k in keys:
                if k in obj:
                    return obj[k]
        return default

    def sqr(x):
        return x * x

    def dist(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    # ---------- parse instance ----------
    depot = get(instance, "depot", "depot_id", default=0)
    capacity = get(instance, "capacity", "vehicle_capacity", "cap", default=None)

    demands = get(instance, "demands", "demand", default=None)
    coords = get(instance, "coords", "coordinates", "points", default=None)
    dist_matrix = get(instance, "distance_matrix", "dist_matrix", "matrix", default=None)

    # Try to infer customer ids
    customers = None
    if isinstance(instance, dict):
        if "customers" in instance:
            customers = list(instance["customers"])
        elif "nodes" in instance:
            customers = list(instance["nodes"])
        elif demands is not None and isinstance(demands, dict):
            customers = [k for k in demands.keys() if k != depot]
        elif coords is not None and isinstance(coords, dict):
            customers = [k for k in coords.keys() if k != depot]
        elif dist_matrix is not None and isinstance(dist_matrix, dict):
            customers = [k for k in dist_matrix.keys() if k != depot]

    if customers is None:
        # Fallback: try assuming numeric ids 0..n-1 from demand/coords dicts
        if isinstance(demands, dict):
            customers = [k for k in demands.keys() if k != depot]
        elif isinstance(coords, dict):
            customers = [k for k in coords.keys() if k != depot]
        else:
            customers = []

    # Normalize demand accessor
    def demand_of(i):
        if demands is None:
            return 0
        if isinstance(demands, dict):
            return demands.get(i, 0)
        if isinstance(demands, (list, tuple)):
            if isinstance(i, int) and 0 <= i < len(demands):
                return demands[i]
            return 0
        return 0

    # Normalize distance accessor
    def d(i, j):
        if dist_matrix is not None:
            if isinstance(dist_matrix, dict):
                row = dist_matrix.get(i, None)
                if isinstance(row, dict):
                    return row.get(j, 0)
                if isinstance(dist_matrix.get(j, None), dict):
                    return dist_matrix[j].get(i, 0)
            elif isinstance(dist_matrix, (list, tuple)):
                return dist_matrix[i][j]
        if coords is not None:
            if isinstance(coords, dict):
                return dist(coords[i], coords[j])
            return dist(coords[i], coords[j])
        return 0

    # ---------- feasibility guards ----------
    unassigned = [c for c in customers if c != depot]
    # Remove duplicates while preserving order
    seen = set()
    tmp = []
    for c in unassigned:
        if c not in seen:
            seen.add(c)
            tmp.append(c)
    unassigned = tmp

    if capacity is None:
        # If capacity absent, set to total demand so one route is feasible.
        capacity = 0
        for c in unassigned:
            capacity += max(0, demand_of(c))
        if capacity <= 0:
            capacity = 10**18

    # ---------- constructive phase: greedy nearest feasible with route closing ----------
    routes = []
    remaining = unassigned[:]

    # Precompute simple "closeness to depot" ordering for route starts
    remaining.sort(key=lambda c: (d(depot, c), -demand_of(c), c))

    while remaining:
        route = []
        load = 0
        current = depot
        # start route with a good seed: farthest from depot among feasible? use nearest for compactness
        seed_idx = -1
        for idx, c in enumerate(remaining):
            dem = demand_of(c)
            if load + dem <= capacity:
                seed_idx = idx
                break
        if seed_idx == -1:
            # capacity issue due to oversized demand; force the smallest demand customer
            seed_idx = 0
        c = remaining.pop(seed_idx)
        route.append(c)
        load += demand_of(c)
        current = c

        improved = True
        while improved and remaining:
            improved = False
            best_idx = -1
            best_key = None
            for idx, cand in enumerate(remaining):
                dem = demand_of(cand)
                if load + dem > capacity:
                    continue
                # score: nearest next plus mild preference for demand fit
                score = (d(current, cand), d(cand, depot) - d(current, depot), -dem, cand)
                if best_key is None or score < best_key:
                    best_key = score
                    best_idx = idx
            if best_idx != -1:
                c = remaining.pop(best_idx)
                route.append(c)
                load += demand_of(c)
                current = c
                improved = True

        routes.append(route)

    # ---------- local search: intra-route 2-opt (distance only) ----------
    def route_load(rt):
        s = 0
        for x in rt:
            s += demand_of(x)
        return s

    def route_cost(rt):
        if not rt:
            return 0
        total = d(depot, rt[0])
        for i in range(len(rt) - 1):
            total += d(rt[i], rt[i + 1])
        total += d(rt[-1], depot)
        return total

    def two_opt(route):
        n = len(route)
        if n < 4:
            return route
        best = route[:]
        best_cost = route_cost(best)
        changed = True
        while changed:
            changed = False
            for i in range(n - 2):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    cand = best[:i + 1] + best[i + 1:j + 1][::-1] + best[j + 1:]
                    cst = route_cost(cand)
                    if cst + 1e-12 < best_cost:
                        best = cand
                        best_cost = cst
                        changed = True
                        break
                if changed:
                    break
        return best

    routes = [two_opt(rt) for rt in routes]

    # ---------- repair/compression: relocate customers between routes if beneficial ----------
    # deterministic first-improvement, preserving feasibility
    changed = True
    while changed:
        changed = False
        # sort routes by cost descending so we try to improve expensive ones first
        order = list(range(len(routes)))
        order.sort(key=lambda r: (-route_cost(routes[r]), len(routes[r]), r))
        for r_idx in order:
            rt = routes[r_idx]
            if not rt:
                continue
            for pos, cust in enumerate(rt):
                dem = demand_of(cust)
                # try moving cust to another route
                best_move = None
                old_cost_r = route_cost(rt)
                rt_without = rt[:pos] + rt[pos + 1:]
                cost_without = route_cost(rt_without) if rt_without else 0
                for s_idx in range(len(routes)):
                    if s_idx == r_idx:
                        continue
                    target = routes[s_idx]
                    if route_load(target) + dem > capacity:
                        continue
                    # try all insertion positions
                    base_cost_t = route_cost(target)
                    for ins in range(len(target) + 1):
                        new_t = target[:ins] + [cust] + target[ins:]
                        new_cost = cost_without + route_cost(new_t)
                        old_total = old_cost_r + base_cost_t
                        if new_total := new_cost < old_total:
                            pass
                        delta = new_cost - old_total
                        if best_move is None or delta < best_move[0] - 1e-12:
                            best_move = (delta, s_idx, ins)
                if best_move is not None and best_move[0] < -1e-12:
                    _, s_idx, ins = best_move
                    # apply move
                    routes[r_idx] = rt[:pos] + rt[pos + 1:]
                    routes[s_idx] = routes[s_idx][:ins] + [cust] + routes[s_idx][ins:]
                    if not routes[r_idx]:
                        routes.pop(r_idx)
                    changed = True
                    break
            if changed:
                break

    # Remove any empty routes
    routes = [rt for rt in routes if rt]

    # Final pass: ensure all customers present exactly once; if any missing, append in singleton routes
    present = set()
    for rt in routes:
        for c in rt:
            present.add(c)
    missing = [c for c in unassigned if c not in present]
    for c in missing:
        routes.append([c])

    # Deterministic final normalization: sort routes by first customer distance to depot then lexicographically
    routes.sort(key=lambda rt: (d(depot, rt[0]) if rt else 0, len(rt), rt))

    return routes
