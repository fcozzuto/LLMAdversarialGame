def solve_cvrp(instance):
    # Robust instance parsing
    coords = instance.get("coords", instance.get("coordinates", instance.get("points")))
    demands = instance.get("demands", instance.get("demand"))
    capacity = instance.get("capacity", instance.get("vehicle_capacity"))
    depot_id = instance.get("depot", instance.get("depot_id", 0))

    n = len(demands)

    def dist(i, j):
        xi, yi = coords[i]
        xj, yj = coords[j]
        dx = xi - xj
        dy = yi - yj
        return (dx * dx + dy * dy) ** 0.5

    customers = [i for i in range(n) if i != depot_id]

    # Precompute distance to depot and pairwise distances
    d0 = [0.0] * n
    for i in customers:
        d0[i] = dist(depot_id, i)

    # Initial constructive phase: sweep-like ordering by angle around depot if possible,
    # otherwise by distance to depot. Angles make the solution interpretable.
    dx0, dy0 = coords[depot_id]
    angle_key = []
    for i in customers:
        x, y = coords[i]
        angle = 0.0
        if x != dx0 or y != dy0:
            # Manual atan2-like ordering without imports: use quadrant and slope proxy.
            vx = x - dx0
            vy = y - dy0
            if vx >= 0 and vy >= 0:
                quad = 0
            elif vx < 0 <= vy:
                quad = 1
            elif vx < 0 and vy < 0:
                quad = 2
            else:
                quad = 3
            slope = vy / (abs(vx) + abs(vy) + 1e-12)
            angle_key.append((quad, -slope, d0[i], i))
        else:
            angle_key.append((0, 0.0, d0[i], i))
    angle_key.sort()
    ordered = [t[3] for t in angle_key]

    # Construct routes by greedy capacity fill along ordered customers
    unassigned = set(customers)
    routes = []

    def route_load(route):
        s = 0
        for c in route:
            s += demands[c]
        return s

    # First pass: create seed routes with contiguous ordered customers
    idx = 0
    while unassigned:
        load = 0
        route = []
        start_idx = idx
        # find next unassigned seed
        while start_idx < len(ordered) and ordered[start_idx] not in unassigned:
            start_idx += 1
        if start_idx >= len(ordered):
            # fallback
            seed = min(unassigned, key=lambda i: (d0[i], i))
        else:
            seed = ordered[start_idx]
        route.append(seed)
        unassigned.remove(seed)
        load += demands[seed]
        idx = start_idx + 1

        # Extend route with nearest feasible unassigned customers
        while True:
            last = route[-1]
            best = None
            best_key = None
            for j in unassigned:
                dj = demands[j]
                if load + dj > capacity:
                    continue
                # Prefer nearest to last, then smaller added distance to depot, then id
                key = (dist(last, j), d0[j], j)
                if best is None or key < best_key:
                    best = j
                    best_key = key
            if best is None:
                break
            route.append(best)
            unassigned.remove(best)
            load += demands[best]

        routes.append(route)

    # Repair: if any route exceeds capacity due to bad input or zero capacity weirdness,
    # split greedily; otherwise no-op.
    repaired = []
    for route in routes:
        cur = []
        load = 0
        for c in route:
            if load + demands[c] <= capacity:
                cur.append(c)
                load += demands[c]
            else:
                if cur:
                    repaired.append(cur)
                cur = [c]
                load = demands[c]
        if cur:
            repaired.append(cur)
    routes = repaired

    # Local search: 2-route relocate / swap for deterministic improvement under capacity
    def route_cost(route):
        if not route:
            return 0.0
        c = d0[route[0]]
        for a, b in zip(route, route[1:]):
            c += dist(a, b)
        c += d0[route[-1]]
        return c

    def total_cost(rs):
        s = 0.0
        for r in rs:
            s += route_cost(r)
        return s

    improved = True
    iterations = 0
    while improved and iterations < 40:
        iterations += 1
        improved = False
        best_delta = 0.0
        best_move = None

        # Relocate one customer between routes
        for i in range(len(routes)):
            ri = routes[i]
            li = route_load(ri)
            for pos in range(len(ri)):
                c = ri[pos]
                dc = demands[c]
                ri_prev = depot_id if pos == 0 else ri[pos - 1]
                ri_next = depot_id if pos == len(ri) - 1 else ri[pos + 1]
                remove_gain = dist(ri_prev, c) + dist(c, ri_next) - dist(ri_prev, ri_next)

                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    lj = route_load(rj)
                    if lj + dc > capacity:
                        continue
                    for ins in range(len(rj) + 1):
                        rj_prev = depot_id if ins == 0 else rj[ins - 1]
                        rj_next = depot_id if ins == len(rj) else rj[ins]
                        add_cost = dist(rj_prev, c) + dist(c, rj_next) - dist(rj_prev, rj_next)
                        delta = add_cost - remove_gain
                        if delta < best_delta - 1e-12:
                            best_delta = delta
                            best_move = ("relocate", i, pos, j, ins)

        # Swap between routes
        for i in range(len(routes)):
            ri = routes[i]
            li = route_load(ri)
            for j in range(i + 1, len(routes)):
                rj = routes[j]
                lj = route_load(rj)
                for pi in range(len(ri)):
                    a = ri[pi]
                    da = demands[a]
                    ai_prev = depot_id if pi == 0 else ri[pi - 1]
                    ai_next = depot_id if pi == len(ri) - 1 else ri[pi + 1]
                    rem_a = dist(ai_prev, a) + dist(a, ai_next) - dist(ai_prev, ai_next)
                    for pj in range(len(rj)):
                        b = rj[pj]
                        db = demands[b]
                        if li - da + db > capacity or lj - db + da > capacity:
                            continue
                        bj_prev = depot_id if pj == 0 else rj[pj - 1]
                        bj_next = depot_id if pj == len(rj) - 1 else rj[pj + 1]
                        rem_b = dist(bj_prev, b) + dist(b, bj_next) - dist(bj_prev, bj_next)
                        add_a = dist(ai_prev, b) + dist(b, ai_next) - dist(ai_prev, ai_next)
                        add_b = dist(bj_prev, a) + dist(a, bj_next) - dist(bj_prev, bj_next)
                        delta = (add_a + add_b) - (rem_a + rem_b)
                        if delta < best_delta - 1e-12:
                            best_delta = delta
                            best_move = ("swap", i, pi, j, pj)

        if best_move is not None:
            improved = True
            kind = best_move[0]
            if kind == "relocate":
                _, i, pos, j, ins = best_move
                c = routes[i][pos]
                if i < j:
                    rj = routes[j]
                    ri = routes[i]
                else:
                    ri = routes[i]
                    rj = routes[j]
                routes[i].pop(pos)
                routes[j].insert(ins, c)
            else:
                _, i, pi, j, pj = best_move
                routes[i][pi], routes[j][pj] = routes[j][pj], routes[i][pi]

    # Final cleanup: remove empty routes
    routes = [r for r in routes if r]
    return routes
