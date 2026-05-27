def solve_cvrp(instance):
    depot = 0

    def iget(obj, key, default=None):
        try:
            return obj.get(key, default)
        except:
            return default

    depot = iget(instance, "depot", 0)

    demands = iget(instance, "demands", None)
    capacity = iget(instance, "capacity", None)
    if capacity is None:
        capacity = iget(instance, "vehicle_capacity", iget(instance, "cap", 0))

    dist = iget(instance, "distance_matrix", iget(instance, "distances", None))
    coords = iget(instance, "coords", iget(instance, "coordinates", None))

    customers = iget(instance, "customers", None)
    if customers is None:
        if "customer_ids" in instance:
            customers = instance["customer_ids"]
        elif "nodes" in instance:
            customers = [x for x in instance["nodes"] if x != depot]
        elif demands is not None:
            try:
                customers = [k for k in demands if k != depot]
            except:
                customers = []
        else:
            customers = []

    def demand_of(c):
        if demands is None:
            return 0
        try:
            return demands[c]
        except:
            try:
                return demands.get(c, 0)
            except:
                return 0

    def dist_of(i, j):
        if dist is not None:
            try:
                return dist[i][j]
            except:
                try:
                    return dist[i, j]
                except:
                    pass
        if coords is not None:
            try:
                ax, ay = coords[i]
                bx, by = coords[j]
                dx = ax - bx
                dy = ay - by
                return (dx * dx + dy * dy) ** 0.5
            except:
                return 0
        return 0

    seen = {}
    clean = []
    for c in customers:
        if c == depot:
            continue
        if c not in seen:
            seen[c] = 1
            clean.append(c)
    customers = clean

    if not customers:
        return []

    if not capacity:
        total = 0
        for c in customers:
            total += demand_of(c)
        capacity = total if total > 0 else 1

    # Precompute deterministic ordering
    arr = []
    for c in customers:
        arr.append((dist_of(depot, c), demand_of(c), c))
    arr.sort(key=lambda x: (-x[0], -x[1], x[2]))
    unrouted = [x[2] for x in arr]

    routes = []
    loads = []

    # Phase 1: farthest-first greedy route building
    while unrouted:
        seed_i = 0
        seed = unrouted[0]
        best_seed_key = None
        for i in range(len(unrouted)):
            c = unrouted[i]
            dc = demand_of(c)
            if dc > capacity:
                dc = capacity
            key = (-dist_of(depot, c), -dc, c)
            if best_seed_key is None or key < best_seed_key:
                best_seed_key = key
                seed_i = i
                seed = c
        route = [seed]
        load = demand_of(seed)
        unrouted.pop(seed_i)

        while True:
            last = route[-1]
            best_i = -1
            best_c = None
            best_key = None
            for i in range(len(unrouted)):
                c = unrouted[i]
                dc = demand_of(c)
                if load + dc > capacity:
                    continue
                inc = dist_of(last, c) + dist_of(c, depot) - dist_of(last, depot)
                key = (inc, -dc, c)
                if best_key is None or key < best_key:
                    best_key = key
                    best_i = i
                    best_c = c
            if best_c is None:
                break
            route.append(best_c)
            load += demand_of(best_c)
            unrouted.pop(best_i)

        routes.append(route)
        loads.append(load)

    # Phase 2: relocate/improve within and between routes
    def route_cost(route):
        if not route:
            return 0
        cost = dist_of(depot, route[0])
        for i in range(len(route) - 1):
            cost += dist_of(route[i], route[i + 1])
        cost += dist_of(route[-1], depot)
        return cost

    improved = True
    iters = 0
    while improved and iters < 4:
        improved = False
        iters += 1

        # intra-route 2-opt
        for r in range(len(routes)):
            route = routes[r]
            n = len(route)
            if n < 4:
                continue
            best_gain = 0
            best_a = -1
            best_b = -1
            for a in range(n - 2):
                prev = depot if a == 0 else route[a - 1]
                for b in range(a + 2, n):
                    nxt = depot if b == n - 1 else route[b + 1]
                    gain = (dist_of(prev, route[a]) + dist_of(route[b], nxt)) - (dist_of(prev, route[b]) + dist_of(route[a], nxt))
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best_a = a
                        best_b = b
            if best_gain > 1e-12:
                route[best_a:best_b + 1] = route[best_a:best_b + 1][::-1]
                improved = True

        # relocate single customer between routes if beneficial
        for a in range(len(routes)):
            ra = routes[a]
            ia = 0
            while ia < len(ra):
                c = ra[ia]
                dc = demand_of(c)
                best_move = None
                cur_delta_remove = 0
                prevc = depot if ia == 0 else ra[ia - 1]
                nextc = depot if ia == len(ra) - 1 else ra[ia + 1]
                cur_delta_remove = dist_of(prevc, c) + dist_of(c, nextc) - dist_of(prevc, nextc)
                for b in range(len(routes)):
                    if b == a:
                        continue
                    if loads[b] + dc > capacity:
                        continue
                    rb = routes[b]
                    prev = depot
                    for p in range(len(rb) + 1):
                        nxt = depot if p == len(rb) else rb[p]
                        add = dist_of(prev, c) + dist_of(c, nxt) - dist_of(prev, nxt)
                        delta = add - cur_delta_remove
                        if best_move is None or delta < best_move[0] or (delta == best_move[0] and (b, p) < (best_move[1], best_move[2])):
                            best_move = (delta, b, p)
                        if p < len(rb):
                            prev = rb[p]
                if best_move is not None and best_move[0] < -1e-12:
                    b, p = best_move[1], best_move[2]
                    routes[a].pop(ia)
                    loads[a] -= dc
                    if a == b:
                        if p > ia:
                            p -= 1
                    routes[b].insert(p, c)
                    loads[b] += dc
                    improved = True
                    if len(routes[a]) == 0:
                        routes.pop(a)
                        loads.pop(a)
                        break
                else:
                    ia += 1
            if a >= len(routes):
                break

    # Phase 3: cleanup empty routes
    final_routes = []
    for r in routes:
        if r:
            final_routes.append(r)

    # Final deterministic safeguard: ensure all customers are present once
    present = {}
    for r in final_routes:
        for c in r:
            present[c] = present.get(c, 0) + 1

    missing = []
    for c in customers:
        if present.get(c, 0) == 0:
            missing.append(c)

    if missing:
        for c in missing:
            dc = demand_of(c)
            best_r = -1
            best_p = -1
            best_key = None
            for r in range(len(final_routes)):
                load = 0
                for x in final_routes[r]:
                    load += demand_of(x)
                if load + dc > capacity:
                    continue
                route = final_routes[r]
                prev = depot
                for p in range(len(route) + 1):
                    nxt = depot if p == len(route) else route[p]
                    cost = dist_of(prev, c) + dist_of(c, nxt) - dist_of(prev, nxt)
                    key = (cost, r, p)
                    if best_key is None or key < best_key:
                        best_key = key
                        best_r = r
                        best_p = p
                    if p < len(route):
                        prev = route[p]
            if best_r == -1:
                final_routes.append([c])
            else:
                final_routes[best_r].insert(best_p, c)

    return final_routes
