def solve_cvrp(instance):
    depot = instance["depot_index"]
    customers = list(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    dist = instance["distance_matrix"]

    def route_load(route):
        s = 0
        for c in route:
            s += demands[c]
        return s

    def route_cost(route):
        if not route:
            return 0
        c = dist[depot][route[0]]
        for i in range(len(route) - 1):
            c += dist[route[i]][route[i + 1]]
        c += dist[route[-1]][depot]
        return c

    def insertion_delta(route, pos, node):
        prev = depot if pos == 0 else route[pos - 1]
        nxt = depot if pos == len(route) else route[pos]
        return dist[prev][node] + dist[node][nxt] - dist[prev][nxt]

    def best_insertion(route, node):
        best_pos = 0
        best_delta = None
        for pos in range(len(route) + 1):
            d = insertion_delta(route, pos, node)
            if best_delta is None or d < best_delta or (d == best_delta and pos < best_pos):
                best_delta = d
                best_pos = pos
        return best_pos, best_delta

    def two_opt(route):
        n = len(route)
        if n < 3:
            return route
        improved = True
        while improved:
            improved = False
            best_delta = 0
            bi = bj = -1
            for i in range(n - 1):
                a = depot if i == 0 else route[i - 1]
                b = route[i]
                for j in range(i + 1, n):
                    c = route[j]
                    d = depot if j == n - 1 else route[j + 1]
                    delta = dist[a][c] + dist[b][d] - dist[a][b] - dist[c][d]
                    if delta < best_delta or (delta == best_delta and (i < bi or (i == bi and j < bj))):
                        best_delta = delta
                        bi = i
                        bj = j
            if best_delta < 0:
                route = route[:bi] + route[bi:bj + 1][::-1] + route[bj + 1:]
                n = len(route)
                improved = True
        return route

    def normalize_routes(routes):
        out = []
        for r in routes:
            if r:
                out.append(r)
        out.sort(key=lambda r: (r[0], len(r), tuple(r)))
        return out

    def merge_pair(r1, r2):
        if route_load(r1) + route_load(r2) > capacity:
            return None
        variants = [
            r1 + r2,
            r1 + r2[::-1],
            r1[::-1] + r2,
            r1[::-1] + r2[::-1],
        ]
        best = None
        best_cost = None
        base = route_cost(r1) + route_cost(r2)
        for r in variants:
            c = route_cost(r)
            if best is None or c < best_cost or (c == best_cost and tuple(r) < tuple(best)):
                best = r
                best_cost = c
        if best_cost is not None and best_cost <= base:
            return best
        return None

    # Initial construction: cheapest insertion with a deterministic starting seed.
    unserved = {c: True for c in customers}
    ordered = sorted(customers, key=lambda x: (-dist[depot][x], -demands[x], x))
    routes = []

    while unserved:
        start = None
        for c in ordered:
            if c in unserved:
                start = c
                break
        del unserved[start]
        route = [start]
        load = demands[start]

        # greedily grow the route by minimum insertion cost among feasible unserved customers
        while True:
            best = None
            for c in ordered:
                if c not in unserved:
                    continue
                if load + demands[c] > capacity:
                    continue
                pos, delta = best_insertion(route, c)
                key = (delta, dist[depot][c], -demands[c], c, pos)
                if best is None or key < best[0]:
                    best = (key, c, pos)
            if best is None:
                break
            _, c, pos = best
            route.insert(pos, c)
            load += demands[c]
            del unserved[c]

        route = two_opt(route)
        routes.append(route)

    routes = normalize_routes(routes)

    def total_cost(rs):
        s = 0
        for r in rs:
            s += route_cost(r)
        return s

    # Inter-route improvement: relocate, swap, and merge; repeat until stable.
    improved = True
    passes = 0
    while improved and passes < 50:
        passes += 1
        improved = False

        # Merge routes when beneficial
        best_merge = None
        best_key = None
        rcount = len(routes)
        for i in range(rcount):
            for j in range(i + 1, rcount):
                m = merge_pair(routes[i], routes[j])
                if m is not None:
                    delta = route_cost(m) - route_cost(routes[i]) - route_cost(routes[j])
                    key = (delta, i, j, tuple(m))
                    if best_key is None or key < best_key:
                        best_key = key
                        best_merge = (i, j, m)
        if best_merge is not None:
            i, j, m = best_merge
            new_routes = []
            for k, r in enumerate(routes):
                if k != i and k != j:
                    new_routes.append(r)
            new_routes.append(two_opt(m))
            routes = normalize_routes(new_routes)
            improved = True
            continue

        # Best relocate
        best = None
        best_key = None
        rcount = len(routes)
        for i in range(rcount):
            ri = routes[i]
            for p in range(len(ri)):
                node = ri[p]
                if len(ri) == 1:
                    rem_delta = -dist[depot][node] - dist[node][depot]
                else:
                    prev = depot if p == 0 else ri[p - 1]
                    nxt = depot if p == len(ri) - 1 else ri[p + 1]
                    rem_delta = dist[prev][nxt] - dist[prev][node] - dist[node][nxt]
                for j in range(rcount):
                    if i == j:
                        continue
                    rj = routes[j]
                    if route_load(rj) + demands[node] > capacity:
                        continue
                    for q in range(len(rj) + 1):
                        add_delta = insertion_delta(rj, q, node)
                        delta = rem_delta + add_delta
                        if delta < 0:
                            key = (delta, i, p, j, q, node)
                            if best_key is None or key < best_key:
                                best_key = key
                                best = (i, p, j, q, node)
        if best is not None:
            i, p, j, q, node = best
            new_routes = []
            for idx, r in enumerate(routes):
                if idx == i:
                    rr = r[:p] + r[p + 1:]
                    if rr:
                        new_routes.append(two_opt(rr))
                elif idx == j:
                    rr = r[:q] + [node] + r[q:]
                    new_routes.append(two_opt(rr))
                else:
                    new_routes.append(r)
            routes = normalize_routes(new_routes)
            improved = True
            continue

        # Best swap
        best = None
        best_key = None
        rcount = len(routes)
        for i in range(rcount):
            ri = routes[i]
            li = route_load(ri)
            for j in range(i + 1, rcount):
                rj = routes[j]
                lj = route_load(rj)
                for p, a in enumerate(ri):
                    for q, b in enumerate(rj):
                        if li - demands[a] + demands[b] > capacity:
                            continue
                        if lj - demands[b] + demands[a] > capacity:
                            continue
                        def node_delta(route, idx, old, new):
                            prev = depot if idx == 0 else route[idx - 1]
                            nxt = depot if idx == len(route) - 1 else route[idx + 1]
                            return dist[prev][new] + dist[new][nxt] - dist[prev][old] - dist[old][nxt]
                        delta = node_delta(ri, p, a, b) + node_delta(rj, q, b, a)
                        if delta < 0:
                            key = (delta, i, p, j, q, a, b)
                            if best_key is None or key < best_key:
                                best_key = key
                                best = (i, p, j, q)
        if best is not None:
            i, p, j, q = best
            ri = routes[i][:]
            rj = routes[j][:]
            ri[p], rj[q] = rj[q], ri[p]
            new_routes = []
            for k, r in enumerate(routes):
                if k == i:
                    new_routes.append(two_opt(ri))
                elif k == j:
                    new_routes.append(two_opt(rj))
                else:
                    new_routes.append(r)
            routes = normalize_routes(new_routes)
            improved = True
            continue

    return routes
