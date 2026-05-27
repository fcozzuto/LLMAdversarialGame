def solve_cvrp(instance):
    depot = instance["depot_index"]
    customer_ids = list(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    D = instance["distance_matrix"]

    def dist(a, b):
        return D[a][b]

    def route_cost(route):
        if not route:
            return 0
        c = dist(depot, route[0])
        for i in range(len(route) - 1):
            c += dist(route[i], route[i + 1])
        c += dist(route[-1], depot)
        return c

    def route_load(route):
        s = 0
        for n in route:
            s += demands[n]
        return s

    def insertion_delta(route, pos, node):
        prev = depot if pos == 0 else route[pos - 1]
        nxt = depot if pos == len(route) else route[pos]
        return dist(prev, node) + dist(node, nxt) - dist(prev, nxt)

    # Deterministic constructive phase: greedy route growth with capacity
    unassigned = {}
    for c in customer_ids:
        unassigned[c] = 1

    routes = []
    total_demand = 0
    for c in customer_ids:
        total_demand += demands[c]
    if total_demand == 0:
        return [[] for _ in customer_ids]

    while unassigned:
        # choose seed: farthest from depot, tie by higher demand then id
        seed = None
        best_seed_key = None
        for n in unassigned:
            key = (dist(depot, n), demands[n], -n)
            if best_seed_key is None or key > best_seed_key:
                best_seed_key = key
                seed = n

        route = [seed]
        load = demands[seed]
        del unassigned[seed]
        current = seed

        while True:
            best = None
            best_key = None
            for n in unassigned:
                d = demands[n]
                if load + d > capacity:
                    continue
                # bias toward short continuation, but prefer nodes that are awkward/far from depot
                key = (dist(current, n) - 0.15 * dist(depot, n), -d, n)
                if best_key is None or key < best_key:
                    best_key = key
                    best = n
            if best is None:
                break
            route.append(best)
            load += demands[best]
            del unassigned[best]
            current = best

        routes.append(route)

    # Repair: ensure every customer appears exactly once
    seen = {}
    cleaned = []
    for r in routes:
        nr = []
        ld = 0
        for n in r:
            if n in seen:
                continue
            seen[n] = 1
            nr.append(n)
            ld += demands[n]
        if nr:
            cleaned.append(nr)
    routes = cleaned

    missing = []
    for c in customer_ids:
        if c not in seen:
            missing.append(c)

    # If any missing, insert them greedily into feasible routes or make singleton routes
    for node in missing:
        best_r = -1
        best_p = None
        best_inc = None
        for ri in range(len(routes)):
            r = routes[ri]
            if route_load(r) + demands[node] > capacity:
                continue
            for p in range(len(r) + 1):
                inc = insertion_delta(r, p, node)
                key = (inc, p, ri)
                if best_inc is None or key < best_inc:
                    best_inc = key
                    best_r = ri
                    best_p = p
        if best_r == -1:
            routes.append([node])
        else:
            routes[best_r].insert(best_p, node)

    # Local search: relocate improving moves between routes
    improved = True
    passes = 0
    while improved and passes < 4:
        improved = False
        passes += 1

        # Intra-route 2-opt
        for ri in range(len(routes)):
            r = routes[ri]
            n = len(r)
            if n < 4:
                continue
            changed = True
            while changed:
                changed = False
                base = route_cost(r)
                for i in range(n - 2):
                    for j in range(i + 2, n):
                        nr = r[:i + 1] + r[i + 1:j + 1][::-1] + r[j + 1:]
                        if route_cost(nr) + 1e-12 < base:
                            r = nr
                            routes[ri] = r
                            n = len(r)
                            base = route_cost(r)
                            changed = True
                            improved = True
                            break
                    if changed:
                        break

        # Inter-route relocate
        outer_break = False
        for a in range(len(routes)):
            if outer_break:
                break
            ra = routes[a]
            for ia in range(len(ra)):
                node = ra[ia]
                for b in range(len(routes)):
                    if a == b:
                        continue
                    rb = routes[b]
                    if route_load(rb) + demands[node] > capacity:
                        continue
                    best_move = None
                    base_a = route_cost(ra)
                    base_b = route_cost(rb)
                    ra_wo = ra[:ia] + ra[ia + 1:]
                    if not ra_wo:
                        continue
                    new_base_a = route_cost(ra_wo)
                    for ib in range(len(rb) + 1):
                        nb = rb[:ib] + [node] + rb[ib:]
                        gain = (new_base_a + route_cost(nb)) - (base_a + base_b)
                        key = (gain, a, b, ia, ib)
                        if best_move is None or key < best_move:
                            best_move = key
                    if best_move and best_move[0] < -1e-12:
                        _, _, _, ia2, ib2 = best_move
                        node2 = ra[ia2]
                        routes[a] = ra[:ia2] + ra[ia2 + 1:]
                        routes[b] = rb[:ib2] + [node2] + rb[ib2:]
                        if not routes[a]:
                            routes.pop(a)
                        improved = True
                        outer_break = True
                        break
                if outer_break:
                    break

        # Remove any accidental empty routes
        routes = [r for r in routes if r]

    # Final exact cleanup: deduplicate and reinsert if needed
    seen = {}
    for r in routes:
        for n in r:
            seen[n] = seen.get(n, 0) + 1

    extras = []
    for c in customer_ids:
        if seen.get(c, 0) == 0:
            extras.append(c)
        elif seen[c] > 1:
            seen[c] -= 1

    if extras:
        for node in extras:
            best_r = -1
            best_p = None
            best_inc = None
            for ri in range(len(routes)):
                r = routes[ri]
                if route_load(r) + demands[node] > capacity:
                    continue
                for p in range(len(r) + 1):
                    inc = insertion_delta(r, p, node)
                    key = (inc, ri, p)
                    if best_inc is None or key < best_inc:
                        best_inc = key
                        best_r = ri
                        best_p = p
            if best_r == -1:
                routes.append([node])
            else:
                routes[best_r].insert(best_p, node)

    # If any duplicates still exist, normalize by rebuilding from scratch order
    final_seen = {}
    final_routes = []
    for r in routes:
        nr = []
        ld = 0
        for n in r:
            if final_seen.get(n, 0):
                continue
            if ld + demands[n] <= capacity:
                nr.append(n)
                ld += demands[n]
                final_seen[n] = 1
        if nr:
            final_routes.append(nr)
    routes = final_routes

    # Last pass for missing customers
    missing = []
    for c in customer_ids:
        if final_seen.get(c, 0) == 0:
            missing.append(c)
    for node in missing:
        best_r = -1
        best_p = None
        best_inc = None
        for ri in range(len(routes)):
            r = routes[ri]
            if route_load(r) + demands[node] > capacity:
                continue
            for p in range(len(r) + 1):
                inc = insertion_delta(r, p, node)
                key = (inc, ri, p)
                if best_inc is None or key < best_inc:
                    best_inc = key
                    best_r = ri
                    best_p = p
        if best_r == -1:
            routes.append([node])
        else:
            routes[best_r].insert(best_p, node)

    return routes
