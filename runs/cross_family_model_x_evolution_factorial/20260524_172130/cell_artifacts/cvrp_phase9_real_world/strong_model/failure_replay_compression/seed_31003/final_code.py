def solve_cvrp(instance):
    def get(obj, key, default=None):
        if isinstance(obj, dict):
            if key in obj:
                return obj[key]
            return default
        try:
            return obj[key]
        except:
            pass
        try:
            d = obj.__dict__
            if key in d:
                return d[key]
        except:
            pass
        return default

    depot = get(instance, "depot", 0)
    capacity = get(instance, "capacity", get(instance, "vehicle_capacity", None))
    demands = get(instance, "demands", get(instance, "demand", None))
    coords = get(instance, "coords", get(instance, "coordinates", None))
    dist = get(instance, "distance_matrix", get(instance, "distances", None))

    customers = get(instance, "customers", None)
    if customers is None:
        n = get(instance, "n", None)
        if n is not None:
            customers = [i for i in range(n) if i != depot]
        elif demands is not None:
            if isinstance(demands, dict):
                customers = sorted([k for k in demands.keys() if k != depot])
            else:
                customers = [i for i in range(len(demands)) if i != depot]
        elif coords is not None:
            customers = [i for i in range(len(coords)) if i != depot]
        elif dist is not None:
            customers = [i for i in range(len(dist)) if i != depot]
        else:
            customers = []
    else:
        customers = list(customers)
        customers = [c for c in customers if c != depot]

    def demand_of(c):
        if demands is None:
            return 1
        if isinstance(demands, dict):
            return demands.get(c, 1)
        return demands[c]

    def euclid(a, b):
        ax, ay = coords[a]
        bx, by = coords[b]
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    def d(a, b):
        if dist is not None:
            return dist[a][b]
        return euclid(a, b)

    if capacity is None:
        cap = 10 ** 18
    else:
        cap = capacity

    remaining = set(customers)
    routes = []

    depot_d = {}
    for c in customers:
        depot_d[c] = d(depot, c)

    def seed_key(c):
        return (depot_d[c], demand_of(c), -c)

    while remaining:
        feasible = [c for c in remaining if demand_of(c) <= cap]
        if feasible:
            seed = max(feasible, key=seed_key)
        else:
            seed = min(remaining, key=lambda c: (demand_of(c), depot_d[c], c))
        route = [seed]
        load = demand_of(seed)
        remaining.remove(seed)

        while True:
            feasible = [c for c in remaining if load + demand_of(c) <= cap]
            if not feasible:
                break
            last = route[-1]
            nxt = min(feasible, key=lambda c: (d(last, c), depot_d[c], -demand_of(c), c))
            route.append(nxt)
            load += demand_of(nxt)
            remaining.remove(nxt)

        routes.append(route)

    def route_cost(r):
        if not r:
            return 0.0
        s = d(depot, r[0]) + d(r[-1], depot)
        for i in range(len(r) - 1):
            s += d(r[i], r[i + 1])
        return s

    improved = True
    passes = 0
    while improved and passes < 30:
        improved = False
        passes += 1

        for ri in range(len(routes)):
            r = routes[ri]
            n = len(r)
            if n < 4:
                continue
            best_delta = 0.0
            best_i = None
            best_j = None
            for i in range(n - 2):
                a = depot if i == 0 else r[i - 1]
                b = r[i]
                for j in range(i + 2, n):
                    c = r[j]
                    d2 = depot if j == n - 1 else r[j + 1]
                    delta = (d(a, c) + d(b, d2)) - (d(a, b) + d(c, d2))
                    if delta < best_delta - 1e-12:
                        best_delta = delta
                        best_i = i
                        best_j = j
            if best_i is not None:
                routes[ri] = r[:best_i] + r[best_i:best_j + 1][::-1] + r[best_j + 1:]
                improved = True

        if not improved:
            for i in range(len(routes)):
                for j in range(len(routes)):
                    if i == j:
                        continue
                    ri = routes[i]
                    rj = routes[j]
                    load_i = 0
                    for c in ri:
                        load_i += demand_of(c)
                    load_j = 0
                    for c in rj:
                        load_j += demand_of(c)

                    moved = False
                    for pos in range(len(ri)):
                        c = ri[pos]
                        dc = demand_of(c)
                        if load_j + dc > cap:
                            continue
                        a = depot if pos == 0 else ri[pos - 1]
                        b = depot if pos == len(ri) - 1 else ri[pos + 1]
                        rem = d(a, c) + d(c, b) - d(a, b)

                        best_ins = None
                        best_gain = 0.0
                        for ins in range(len(rj) + 1):
                            left = depot if ins == 0 else rj[ins - 1]
                            right = depot if ins == len(rj) else rj[ins]
                            add = d(left, c) + d(c, right) - d(left, right)
                            gain = rem - add
                            if gain > best_gain + 1e-12:
                                best_gain = gain
                                best_ins = ins
                        if best_ins is not None:
                            new_ri = ri[:pos] + ri[pos + 1:]
                            new_rj = rj[:best_ins] + [c] + rj[best_ins:]
                            routes[i] = new_ri
                            routes[j] = new_rj
                            improved = True
                            moved = True
                            break
                    if moved:
                        break
                if improved:
                    break

        if not improved:
            for i in range(len(routes)):
                for j in range(i + 1, len(routes)):
                    ri = routes[i]
                    rj = routes[j]
                    li = 0
                    for c in ri:
                        li += demand_of(c)
                    lj = 0
                    for c in rj:
                        lj += demand_of(c)

                    best_pi = None
                    best_pj = None
                    best_gain = 0.0

                    for pi in range(len(ri)):
                        a = ri[pi]
                        da = demand_of(a)
                        for pj in range(len(rj)):
                            b = rj[pj]
                            db = demand_of(b)
                            if li - da + db > cap or lj - db + da > cap:
                                continue

                            prev_a = depot if pi == 0 else ri[pi - 1]
                            next_a = depot if pi == len(ri) - 1 else ri[pi + 1]
                            prev_b = depot if pj == 0 else rj[pj - 1]
                            next_b = depot if pj == len(rj) - 1 else rj[pj + 1]

                            delta = (
                                d(prev_a, b) + d(b, next_a) - d(prev_a, a) - d(a, next_a)
                                + d(prev_b, a) + d(a, next_b) - d(prev_b, b) - d(b, next_b)
                            )
                            gain = -delta
                            if gain > best_gain + 1e-12:
                                best_gain = gain
                                best_pi = pi
                                best_pj = pj

                    if best_pi is not None:
                        ri2 = list(ri)
                        rj2 = list(rj)
                        ri2[best_pi], rj2[best_pj] = rj2[best_pj], ri2[best_pi]
                        routes[i] = ri2
                        routes[j] = rj2
                        improved = True
                        break
                if improved:
                    break

        routes = [r for r in routes if r]

    return routes
