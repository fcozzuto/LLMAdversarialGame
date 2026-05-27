def solve_cvrp(instance):
    def get(key, default=None):
        if isinstance(instance, dict):
            return instance.get(key, default)
        try:
            return instance[key]
        except:
            pass
        try:
            d = instance.__dict__
            if key in d:
                return d[key]
        except:
            pass
        return default

    depot = get("depot", 0)

    coords = get("coords", None)
    if coords is None:
        coords = get("positions", None)

    dist_matrix = get("distance_matrix", None)
    if dist_matrix is None:
        dist_matrix = get("distances", None)

    demands = get("demands", None)
    if demands is None:
        demands = get("demand", None)
    if demands is None:
        demands = {}

    capacity = get("capacity", None)
    if capacity is None:
        capacity = get("vehicle_capacity", None)

    customers = get("customers", None)
    if customers is None:
        if isinstance(demands, dict):
            customers = [k for k in demands.keys() if k != depot]
        elif coords is not None:
            customers = [k for k in coords.keys() if k != depot]
        elif dist_matrix is not None:
            customers = [i for i in range(len(dist_matrix)) if i != depot]
        else:
            customers = []
    else:
        customers = [c for c in customers if c != depot]

    def d(i, j):
        if dist_matrix is not None:
            return dist_matrix[i][j]
        if coords is not None:
            xi, yi = coords[i]
            xj, yj = coords[j]
            dx = xi - xj
            dy = yi - yj
            return (dx * dx + dy * dy) ** 0.5
        return 0.0 if i == j else 1.0

    def demand_of(c):
        if isinstance(demands, dict):
            return demands.get(c, 0)
        if isinstance(demands, (list, tuple)) and 0 <= c < len(demands):
            return demands[c]
        return 0

    unserved = set(customers)
    routes = []

    while unserved:
        route = []
        load = 0
        current = depot
        while True:
            best = None
            best_key = None
            for c in unserved:
                dc = demand_of(c)
                if capacity is not None and load + dc > capacity:
                    continue
                key = (d(current, c), -dc, c)
                if best is None or key < best_key:
                    best = c
                    best_key = key
            if best is None:
                break
            route.append(best)
            unserved.remove(best)
            load += demand_of(best)
            current = best
        if not route:
            c = min(unserved, key=lambda x: (d(depot, x), -demand_of(x), x))
            route = [c]
            unserved.remove(c)
        routes.append(route)

    def route_load(route):
        s = 0
        for c in route:
            s += demand_of(c)
        return s

    def improve_route_2opt(route):
        n = len(route)
        if n < 4:
            return route
        changed = True
        while changed:
            changed = False
            best_delta = 0
            best_i = best_j = None
            for i in range(n - 1):
                a = depot if i == 0 else route[i - 1]
                b = route[i]
                for j in range(i + 1, n):
                    c = route[j]
                    nxt = depot if j == n - 1 else route[j + 1]
                    old = d(a, b) + d(c, nxt)
                    new = d(a, c) + d(b, nxt)
                    delta = old - new
                    if delta > best_delta + 1e-12:
                        best_delta = delta
                        best_i, best_j = i, j
            if best_i is not None:
                route[best_i:best_j + 1] = list(reversed(route[best_i:best_j + 1]))
                changed = True
        return route

    for idx in range(len(routes)):
        routes[idx] = improve_route_2opt(routes[idx])

    while True:
        best_move = None
        best_gain = 0

        loads = [route_load(r) for r in routes]

        for i in range(len(routes)):
            ri = routes[i]
            li = loads[i]
            for pos in range(len(ri)):
                c = ri[pos]
                dc = demand_of(c)
                prev_c = depot if pos == 0 else ri[pos - 1]
                next_c = depot if pos == len(ri) - 1 else ri[pos + 1]
                remove_delta = d(prev_c, c) + d(c, next_c) - d(prev_c, next_c)

                for j in range(len(routes)):
                    if i == j:
                        continue
                    rj = routes[j]
                    lj = loads[j]
                    if capacity is not None and lj + dc > capacity:
                        continue
                    for ins in range(len(rj) + 1):
                        prev_j = depot if ins == 0 else rj[ins - 1]
                        next_j = depot if ins == len(rj) else rj[ins]
                        insert_delta = d(prev_j, c) + d(c, next_j) - d(prev_j, next_j)
                        gain = remove_delta - insert_delta
                        if gain > best_gain + 1e-12:
                            best_gain = gain
                            best_move = ("relocate", i, j, pos, ins)

                for j in range(i + 1, len(routes)):
                    rj = routes[j]
                    lj = loads[j]
                    for q in range(len(rj)):
                        c2 = rj[q]
                        d2 = demand_of(c2)
                        if capacity is not None and li - dc + d2 > capacity:
                            continue
                        if capacity is not None and lj - d2 + dc > capacity:
                            continue

                        pi = depot if pos == 0 else ri[pos - 1]
                        ni = depot if pos == len(ri) - 1 else ri[pos + 1]
                        pj = depot if q == 0 else rj[q - 1]
                        nj = depot if q == len(rj) - 1 else rj[q + 1]

                        old = d(pi, c) + d(c, ni) + d(pj, c2) + d(c2, nj)
                        new = d(pi, c2) + d(c2, ni) + d(pj, c) + d(c, nj)
                        gain = old - new
                        if gain > best_gain + 1e-12:
                            best_gain = gain
                            best_move = ("swap", i, j, pos, q)

        if best_move is None:
            break

        if best_move[0] == "relocate":
            _, i, j, pos, ins = best_move
            c = routes[i][pos]
            routes[i].pop(pos)
            if i == j and ins > pos:
                ins -= 1
            routes[j].insert(ins, c)
            if not routes[i]:
                routes.pop(i)
        else:
            _, i, j, pos, q = best_move
            routes[i][pos], routes[j][q] = routes[j][q], routes[i][pos]

        routes = [r for r in routes if r]
        for idx in range(len(routes)):
            routes[idx] = improve_route_2opt(routes[idx])

    return routes
