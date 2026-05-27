def solve_cvrp(instance):
    def get(obj, key, default=None):
        try:
            return obj[key]
        except:
            return default

    # --- Parse instance ---
    capacity = get(instance, "capacity", get(instance, "vehicle_capacity", None))
    depot = get(instance, "depot", 0)

    coords = get(instance, "coords", get(instance, "locations", get(instance, "points", None)))
    dist = get(instance, "distance_matrix", get(instance, "distances", None))
    demands = get(instance, "demands", get(instance, "demand", None))

    customers = get(instance, "customers", None)
    if customers is None:
        n = 0
        if demands is not None:
            n = len(demands)
        elif coords is not None:
            n = len(coords)
        elif dist is not None:
            n = len(dist)
        customers = [i for i in range(n) if i != depot]
    else:
        customers = [c for c in customers if c != depot]

    if capacity is None:
        capacity = sum(demands[c] for c in customers) if demands is not None else 1

    # --- Distance function ---
    def d(i, j):
        if dist is not None:
            return dist[i][j]
        pi = coords[i]
        pj = coords[j]
        return abs(pi[0] - pj[0]) + abs(pi[1] - pj[1])

    def dem(c):
        if demands is None:
            return 1
        return demands[c]

    # --- Initial route construction: savings-style greedy insertion ---
    unvisited = {}
    for c in customers:
        unvisited[c] = 1

    routes = []

    # Seed with largest-demand customers first for stability
    ordered = list(customers)
    ordered.sort(key=lambda c: (-dem(c), c))

    for seed in ordered:
        if seed not in unvisited:
            continue
        route = [seed]
        load = dem(seed)
        del unvisited[seed]

        improved = True
        while improved and unvisited:
            improved = False
            best_c = None
            best_pos = None
            best_gain = None

            route_len = len(route)
            for c in list(unvisited.keys()):
                dc = dem(c)
                if load + dc > capacity:
                    continue

                # Try all insertion positions
                for pos in range(route_len + 1):
                    prev_node = depot if pos == 0 else route[pos - 1]
                    next_node = depot if pos == route_len else route[pos]
                    gain = d(prev_node, c) + d(c, next_node) - d(prev_node, next_node)
                    if best_gain is None or gain < best_gain or (gain == best_gain and (c < best_c or (c == best_c and pos < best_pos))):
                        best_gain = gain
                        best_c = c
                        best_pos = pos

            if best_c is not None:
                route.insert(best_pos, best_c)
                load += dem(best_c)
                del unvisited[best_c]
                improved = True

        routes.append(route)

    # If any remain due to pathological seeding, assign greedily to best existing route or new route
    while unvisited:
        c = next(iter(unvisited))
        best_r = None
        best_pos = None
        best_cost = None

        for r_idx, route in enumerate(routes):
            load = 0
            for x in route:
                load += dem(x)
            if load + dem(c) > capacity:
                continue
            for pos in range(len(route) + 1):
                prev_node = depot if pos == 0 else route[pos - 1]
                next_node = depot if pos == len(route) else route[pos]
                cost = d(prev_node, c) + d(c, next_node) - d(prev_node, next_node)
                if best_cost is None or cost < best_cost:
                    best_cost = cost
                    best_r = r_idx
                    best_pos = pos

        if best_r is None:
            routes.append([c])
        else:
            routes[best_r].insert(best_pos, c)
        del unvisited[c]

    # --- Local search: relocate, swap, 2-opt within routes ---
    def route_load(route):
        s = 0
        for x in route:
            s += dem(x)
        return s

    def route_cost(route):
        if not route:
            return 0
        total = d(depot, route[0])
        for i in range(len(route) - 1):
            total += d(route[i], route[i + 1])
        total += d(route[-1], depot)
        return total

    def total_cost(rs):
        s = 0
        for rt in rs:
            s += route_cost(rt)
        return s

    def swap_gain(route, i, j):
        if i == j:
            return 0
        a = route[i]
        b = route[j]
        prev_a = depot if i == 0 else route[i - 1]
        next_a = depot if i == len(route) - 1 else route[i + 1]
        prev_b = depot if j == 0 else route[j - 1]
        next_b = depot if j == len(route) - 1 else route[j + 1]
        if i + 1 == j:
            before = d(prev_a, a) + d(a, b) + d(b, next_b)
            after = d(prev_a, b) + d(b, a) + d(a, next_b)
            return after - before
        before = d(prev_a, a) + d(a, next_a) + d(prev_b, b) + d(b, next_b)
        after = d(prev_a, b) + d(b, next_a) + d(prev_b, a) + d(a, next_b)
        return after - before

    changed = True
    passes = 0
    while changed and passes < 50:
        changed = False
        passes += 1

        # Relocate between routes
        best_move = None
        best_delta = 0
        for ri in range(len(routes)):
            r1 = routes[ri]
            if not r1:
                continue
            load1 = route_load(r1)
            for i, c in enumerate(r1):
                dc = dem(c)
                prev1 = depot if i == 0 else r1[i - 1]
                next1 = depot if i == len(r1) - 1 else r1[i + 1]
                remove_delta = d(prev1, next1) - d(prev1, c) - d(c, next1)
                for rj in range(len(routes)):
                    if ri == rj:
                        continue
                    r2 = routes[rj]
                    load2 = route_load(r2)
                    if load2 + dc > capacity:
                        continue
                    for pos in range(len(r2) + 1):
                        prev2 = depot if pos == 0 else r2[pos - 1]
                        next2 = depot if pos == len(r2) else r2[pos]
                        add_delta = d(prev2, c) + d(c, next2) - d(prev2, next2)
                        delta = remove_delta + add_delta
                        if delta < best_delta:
                            best_delta = delta
                            best_move = ("relocate", ri, i, rj, pos)
        if best_move is not None:
            _, ri, i, rj, pos = best_move
            c = routes[ri][i]
            routes[ri].pop(i)
            if ri < rj:
                rj -= 1
            routes[rj].insert(pos, c)
            if not routes[ri]:
                routes.pop(ri)
            changed = True
            continue

        # Swap between routes
        best_move = None
        best_delta = 0
        for ri in range(len(routes)):
            for rj in range(ri + 1, len(routes)):
                r1 = routes[ri]
                r2 = routes[rj]
                l1 = route_load(r1)
                l2 = route_load(r2)
                for i, a in enumerate(r1):
                    da = dem(a)
                    for j, b in enumerate(r2):
                        db = dem(b)
                        if l1 - da + db > capacity or l2 - db + da > capacity:
                            continue
                        prev_a = depot if i == 0 else r1[i - 1]
                        next_a = depot if i == len(r1) - 1 else r1[i + 1]
                        prev_b = depot if j == 0 else r2[j - 1]
                        next_b = depot if j == len(r2) - 1 else r2[j + 1]
                        delta = (d(prev_a, b) + d(b, next_a) + d(prev_b, a) + d(a, next_b)) - (d(prev_a, a) + d(a, next_a) + d(prev_b, b) + d(b, next_b))
                        if delta < best_delta:
                            best_delta = delta
                            best_move = ("swap", ri, i, rj, j)
        if best_move is not None:
            _, ri, i, rj, j = best_move
            routes[ri][i], routes[rj][j] = routes[rj][j], routes[ri][i]
            changed = True
            continue

        # 2-opt within routes
        for r_idx in range(len(routes)):
            r = routes[r_idx]
            n = len(r)
            best = None
            best_delta = 0
            for i in range(n - 1):
                a = depot if i == 0 else r[i - 1]
                b = r[i]
                for j in range(i + 1, n):
                    c = r[j]
                    dnext = depot if j == n - 1 else r[j + 1]
                    delta = (d(a, c) + d(b, dnext)) - (d(a, b) + d(c, dnext))
                    if delta < best_delta:
                        best_delta = delta
                        best = (i, j)
            if best is not None:
                i, j = best
                r[i:j + 1] = r[i:j + 1][::-1]
                changed = True
                break

    # Final sanity: ensure all customers appear exactly once
    seen = {}
    for r in routes:
        for c in r:
            seen[c] = seen.get(c, 0) + 1

    missing = [c for c in customers if c not in seen]
    if missing:
        # Repair by inserting missing customers greedily
        for c in missing:
            best_r = None
            best_pos = None
            best_cost = None
            for r_idx, r in enumerate(routes):
                load = route_load(r)
                if load + dem(c) > capacity:
                    continue
                for pos in range(len(r) + 1):
                    prev_node = depot if pos == 0 else r[pos - 1]
                    next_node = depot if pos == len(r) else r[pos]
                    cost = d(prev_node, c) + d(c, next_node) - d(prev_node, next_node)
                    if best_cost is None or cost < best_cost:
                        best_cost = cost
                        best_r = r_idx
                        best_pos = pos
            if best_r is None:
                routes.append([c])
            else:
                routes[best_r].insert(best_pos, c)

    # Remove accidental duplicates by keeping first occurrence only, then repair missing if needed
    seen = {}
