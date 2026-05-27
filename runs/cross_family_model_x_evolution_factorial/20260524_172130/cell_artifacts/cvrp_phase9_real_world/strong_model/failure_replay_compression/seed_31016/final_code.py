def solve_cvrp(instance):
    def get_first(keys, default=None):
        for k in keys:
            if isinstance(instance, dict) and k in instance:
                return instance[k]
        return default

    coords = get_first(["coords", "coordinates", "locations", "points"], None)
    dist = get_first(["distance_matrix", "distances", "matrix"], None)
    demands = get_first(["demands", "demand"], None)
    capacity = get_first(["capacity", "vehicle_capacity", "cap"], None)
    depot = get_first(["depot", "depot_id"], 0)
    customers = get_first(["customers", "nodes", "customer_ids"], None)

    if customers is None:
        if isinstance(coords, dict):
            customers = [k for k in coords.keys() if k != depot]
        elif isinstance(demands, dict):
            customers = [k for k in demands.keys() if k != depot]
        elif dist is not None:
            n = len(dist)
            customers = [i for i in range(n) if i != depot]
        else:
            customers = []

    customers = [c for c in customers if c != depot]
    customers.sort()

    def d(i, j):
        if dist is not None:
            return dist[i][j]
        if coords is not None:
            a = coords[i]
            b = coords[j]
            return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
        return 0

    def dem(i):
        if demands is None:
            return 1
        if isinstance(demands, dict):
            return demands.get(i, 1)
        return demands[i]

    if capacity is None:
        total = 0
        for c in customers:
            total += dem(c)
        capacity = max(total, 1)

    # If coordinates exist, sort by angle around depot for a sweep-like construction.
    if coords is not None and depot in coords:
        dx, dy = coords[depot]
        def angle(c):
            x, y = coords[c]
            return (y - dy, x - dx)
        customers = sorted(customers, key=lambda c: (angle(c)[0] < 0, angle(c)[0] / (abs(angle(c)[1]) + abs(angle(c)[0]) + 1e-12), c))
    elif dist is not None:
        # Fallback deterministic order via nearest-neighbor chain from depot.
        unvisited = customers[:]
        ordered = []
        current = depot
        while unvisited:
            best = None
            best_key = None
            for c in unvisited:
                key = (d(current, c), c)
                if best_key is None or key < best_key:
                    best_key = key
                    best = c
            ordered.append(best)
            unvisited.remove(best)
            current = best
        customers = ordered

    # Greedy route construction by order.
    routes = []
    current = []
    load = 0
    for c in customers:
        dc = dem(c)
        if current and load + dc > capacity:
            routes.append(current)
            current = [c]
            load = dc
        else:
            current.append(c)
            load += dc
    if current:
        routes.append(current)

    # Repair: ensure no empty routes, and all customers included exactly once.
    seen = {}
    for r in routes:
        for c in r:
            seen[c] = seen.get(c, 0) + 1

    missing = [c for c in customers if c not in seen]
    if missing:
        # Insert missing customers into feasible places or new routes.
        for c in missing:
            placed = False
            best = None
            best_cost = None
            for ri, r in enumerate(routes):
                load_r = 0
                for x in r:
                    load_r += dem(x)
                if load_r + dem(c) <= capacity:
                    for pos in range(len(r) + 1):
                        prev = depot if pos == 0 else r[pos - 1]
                        nxt = depot if pos == len(r) else r[pos]
                        cost = d(prev, c) + d(c, nxt) - d(prev, nxt)
                        key = (cost, ri, pos)
                        if best_cost is None or key < best_cost:
                            best_cost = key
                            best = (ri, pos)
                    placed = True
            if placed and best is not None:
                ri, pos = best
                routes[ri].insert(pos, c)
            else:
                routes.append([c])

    # Remove duplicates by keeping first occurrence and repairing later.
    counts = {}
    for r in routes:
        for c in r:
            counts[c] = counts.get(c, 0) + 1

    if any(v > 1 for v in counts.values()):
        new_routes = []
        used = set()
        for r in routes:
            nr = []
            for c in r:
                if c not in used:
                    nr.append(c)
                    used.add(c)
            if nr:
                new_routes.append(nr)
        routes = new_routes
        missing = [c for c in customers if c not in used]
        for c in missing:
            routes.append([c])

    def route_load(r):
        s = 0
        for x in r:
            s += dem(x)
        return s

    def route_cost(r):
        if not r:
            return 0
        total = d(depot, r[0])
        for i in range(len(r) - 1):
            total += d(r[i], r[i + 1])
        total += d(r[-1], depot)
        return total

    def two_opt_route(r):
        if len(r) < 4:
            return r[:]
        best = r[:]
        best_cost = route_cost(best)
        improved = True
        while improved:
            improved = False
            n = len(best)
            for i in range(n - 2):
                for j in range(i + 2, n):
                    cand = best[:i + 1] + best[i + 1:j + 1][::-1] + best[j + 1:]
                    cc = route_cost(cand)
                    if cc + 1e-12 < best_cost or (abs(cc - best_cost) <= 1e-12 and cand < best):
                        best = cand
                        best_cost = cc
                        improved = True
                        break
                if improved:
                    break
        return best

    # Intra-route improvement.
    routes = [two_opt_route(r) for r in routes if r]

    # Inter-route relocate/swap improvement.
    improved = True
    while improved:
        improved = False
        best_move = None
        best_delta = 0
        m = len(routes)
        for a in range(m):
            ra = routes[a]
            la = route_load(ra)
            ca = route_cost(ra)
            for i, x in enumerate(ra):
                prev = depot if i == 0 else ra[i - 1]
                nxt = depot if i == len(ra) - 1 else ra[i + 1]
                remove_delta = d(prev, nxt) - d(prev, x) - d(x, nxt)
                for b in range(m):
                    rb = routes[b]
                    if a == b:
                        continue
                    lb = route_load(rb)
                    if lb + dem(x) > capacity:
                        continue
                    for pos in range(len(rb) + 1):
                        p = depot if pos == 0 else rb[pos - 1]
                        n = depot if pos == len(rb) else rb[pos]
                        add_delta = d(p, x) + d(x, n) - d(p, n)
                        delta = remove_delta + add_delta
                        move_key = (delta, a, i, b, pos, x)
                        if delta < best_delta or (abs(delta - best_delta) <= 1e-12 and (best_move is None or move_key < best_move)):
                            best_delta = delta
                            best_move = ("relocate", a, i, b, pos)
                # swap
                for b in range(a + 1, m):
                    rb = routes[b]
                    lb = route_load(rb)
                    xb = None
                    for j, y in enumerate(rb):
                        if la - dem(x) + dem(y) <= capacity and lb - dem(y) + dem(x) <= capacity:
                            ap = depot if i == 0 else ra[i - 1]
                            an = depot if i == len(ra) - 1 else ra[i + 1]
                            bp = depot if j == 0 else rb[j - 1]
                            bn = depot if j == len(rb) - 1 else rb[j + 1]
                            delta = (
                                d(ap, y) + d(y, an) - d(ap, x) - d(x, an)
                                + d(bp, x) + d(x, bn) - d(bp, y) - d(y, bn)
                            )
                            move_key = (delta, a, i, b, j, x, y)
                            if delta < best_delta or (abs(delta - best_delta) <= 1e-12 and (best_move is None or move_key < best_move)):
                                best_delta = delta
                                best_move = ("swap", a, i, b, j)
        if best_move is not None and best_delta < -1e-12:
            if best_move[0] == "relocate":
                _, a, i, b, pos = best_move
                x = routes[a][i]
                del routes[a][i]
                routes[b].insert(pos, x)
                if not routes[a]:
                    del routes[a]
                routes = [two_opt_route(r) for r in routes]
            else:
                _, a, i, b, j = best_move
                ra = routes[a]
                rb = routes[b]
                ra[i], rb[j] = rb[j], ra[i]
                routes[a] = two_opt_route(ra)
                routes[b] = two_opt_route(rb)
            improved = True

    # Final cleanup: remove empties and ensure deterministic order.
    routes = [r for r in routes if r]
    routes.sort(key=lambda r: (route_cost(r), len(r), r))

    return routes
