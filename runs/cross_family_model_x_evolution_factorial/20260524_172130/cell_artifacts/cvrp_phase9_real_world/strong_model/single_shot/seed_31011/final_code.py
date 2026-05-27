def solve_cvrp(instance):
    def is_seq(x):
        return isinstance(x, (list, tuple))

    def obj_get(obj, names, default=None):
        if isinstance(obj, dict):
            for n in names:
                if n in obj:
                    return obj[n]
            return default
        for n in names:
            try:
                return obj[n]
            except Exception:
                pass
        for n in names:
            try:
                d = vars(obj)
                if n in d:
                    return d[n]
            except Exception:
                pass
        return default

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    def parse_instance(inst):
        coords = None
        demands = None
        capacity = None
        depot = 0

        if isinstance(inst, dict):
            coords = obj_get(inst, ["coords", "coordinates", "locations", "points", "xy"], None)
            demands = obj_get(inst, ["demands", "demand"], None)
            capacity = obj_get(inst, ["capacity", "vehicle_capacity", "cap"], None)
            depot = obj_get(inst, ["depot", "depot_id", "depot_index"], 0)
            if coords is None:
                nodes = obj_get(inst, ["nodes", "customers"], None)
                if nodes is not None:
                    coords = []
                    demands = [] if demands is None else list(demands)
                    for n in nodes:
                        x = obj_get(n, ["x", "X", "lon", "lng"], None)
                        y = obj_get(n, ["y", "Y", "lat"], None)
                        coords.append((x, y))
                        if len(demands) < len(coords):
                            demands.append(obj_get(n, ["demand", "dem"], 0))
        elif is_seq(inst) and len(inst) >= 2:
            coords = inst[0]
            demands = inst[1]
            if len(inst) > 2:
                capacity = inst[2]
            if len(inst) > 3:
                depot = inst[3]
        else:
            coords = obj_get(inst, ["coords", "coordinates", "locations", "points", "xy"], None)
            demands = obj_get(inst, ["demands", "demand"], None)
            capacity = obj_get(inst, ["capacity", "vehicle_capacity", "cap"], None)
            depot = obj_get(inst, ["depot", "depot_id", "depot_index"], 0)

        if coords is None:
            return None, None, None, None

        coords = list(coords)
        n = len(coords)

        if demands is None:
            demands = [0] * n
        else:
            demands = list(demands)
            if len(demands) < n:
                demands.extend([0] * (n - len(demands)))
            elif len(demands) > n:
                demands = demands[:n]

        if capacity is None:
            total = 0
            for d in demands:
                total += d
            capacity = max(1, total)

        try:
            depot = int(depot)
        except Exception:
            depot = 0

        if depot < 0 or depot >= n:
            depot = 0

        return coords, demands, capacity, depot

    coords, demands, capacity, depot = parse_instance(instance)
    if coords is None:
        return []

    n = len(coords)
    customers = [i for i in range(n) if i != depot]
    if not customers:
        return []

    D = [[0.0] * n for _ in range(n)]
    for i in range(n):
        ai = coords[i]
        for j in range(i + 1, n):
            d = dist(ai, coords[j])
            D[i][j] = d
            D[j][i] = d

    def route_load(route):
        s = 0
        for c in route:
            s += demands[c]
        return s

    def route_cost(route):
        if not route:
            return 0.0
        c = D[depot][route[0]] + D[route[-1]][depot]
        for i in range(len(route) - 1):
            c += D[route[i]][route[i + 1]]
        return c

    def insertion_delta(route, pos, c):
        prevn = depot if pos == 0 else route[pos - 1]
        nextn = depot if pos == len(route) else route[pos]
        return D[prevn][c] + D[c][nextn] - D[prevn][nextn]

    unrouted = set(customers)
    routes = []

    first = max(customers, key=lambda c: (D[depot][c], -c))
    routes.append([first])
    unrouted.remove(first)

    while unrouted:
        best = None
        for c in unrouted:
            for ri, r in enumerate(routes):
                if route_load(r) + demands[c] > capacity:
                    continue
                local_delta = None
                local_pos = 0
                for pos in range(len(r) + 1):
                    dlt = insertion_delta(r, pos, c)
                    if local_delta is None or dlt < local_delta or (dlt == local_delta and pos < local_pos):
                        local_delta = dlt
                        local_pos = pos
                cand = (local_delta, ri, local_pos, c)
                if best is None or cand < best:
                    best = cand
        if best is None:
            c = max(unrouted, key=lambda x: (demands[x], D[depot][x], -x))
            routes.append([c])
            unrouted.remove(c)
        else:
            _, ri, pos, c = best
            routes[ri].insert(pos, c)
            unrouted.remove(c)

    def two_opt_route(route):
        if len(route) < 4:
            return route
        improved = True
        while improved:
            improved = False
            m = len(route)
            for i in range(m - 1):
                a = depot if i == 0 else route[i - 1]
                b = route[i]
                for j in range(i + 2, m):
                    c = route[j - 1]
                    d = depot if j == m else route[j]
                    if D[a][c] + D[b][d] + 1e-12 < D[a][b] + D[c][d]:
                        route[i:j] = route[i:j][::-1]
                        improved = True
                        break
                if improved:
                    break
        return route

    for i in range(len(routes)):
        routes[i] = two_opt_route(routes[i])

    improved = True
    while improved:
        improved = False
        best_move = None
        loads = [route_load(r) for r in routes]
        for ri, r in enumerate(routes):
            for pos, c in enumerate(r):
                prevc = depot if pos == 0 else r[pos - 1]
                nextc = depot if pos == len(r) - 1 else r[pos + 1]
                remove_gain = D[prevc][c] + D[c][nextc] - D[prevc][nextc]
                for rj, s in enumerate(routes):
                    if ri == rj:
                        continue
                    if loads[rj] + demands[c] > capacity:
                        continue
                    for ipos in range(len(s) + 1):
                        prevs = depot if ipos == 0 else s[ipos - 1]
                        nexts = depot if ipos == len(s) else s[ipos]
                        insert_cost = D[prevs][c] + D[c][nexts] - D[prevs][nexts]
                        gain = remove_gain - insert_cost
                        if gain > 1e-12:
                            cand = (gain, ri, pos, rj, ipos, c)
                            if best_move is None or cand > best_move:
                                best_move = cand
        if best_move is not None:
            _, ri, pos, rj, ipos, c = best_move
            routes[ri].pop(pos)
            routes[rj].insert(ipos, c)
            if not routes[ri]:
                routes.pop(ri)
            for i in range(len(routes)):
                routes[i] = two_opt_route(routes[i])
            improved = True

    routes = [r for r in routes if r]
    return routes
