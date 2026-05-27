def solve_cvrp(instance):
    def gkey(*names):
        for n in names:
            try:
                if n in instance:
                    return instance[n]
            except:
                pass
        return None

    depot = gkey("depot", "depot_id")
    if depot is None:
        depot = 0

    capacity = gkey("capacity", "vehicle_capacity", "vehicleCapacity", "CAPACITY")
    if capacity is None:
        capacity = 0

    demands = gkey("demands", "demand")
    coords = gkey("coords", "coordinates", "locations", "nodes")
    distm = gkey("distance_matrix", "distances", "matrix")

    customers = gkey("customers", "customer_ids", "ids")
    if customers is None:
        try:
            customers = [k for k in demands.keys() if k != depot]
        except:
            try:
                customers = [k for k in coords.keys() if k != depot]
            except:
                try:
                    n = instance.get("n", instance.get("num_customers", 0))
                    customers = list(range(1, n + 1))
                except:
                    customers = []

    def dem(i):
        try:
            return demands.get(i, 0)
        except:
            try:
                return demands[i]
            except:
                return 0

    def cor(i):
        try:
            return coords.get(i)
        except:
            try:
                return coords[i]
            except:
                return None

    def dist(i, j):
        if distm is not None:
            try:
                return distm[i][j]
            except:
                try:
                    return distm[j][i]
                except:
                    pass
        a = cor(i)
        b = cor(j)
        if a is not None and b is not None:
            try:
                dx = a[0] - b[0]
                dy = a[1] - b[1]
                return (dx * dx + dy * dy) ** 0.5
            except:
                pass
        try:
            return abs(i - j)
        except:
            return 1

    def route_load(r):
        s = 0
        for c in r:
            s += dem(c)
        return s

    def route_cost(r):
        if not r:
            return 0
        t = dist(depot, r[0])
        for i in range(len(r) - 1):
            t += dist(r[i], r[i + 1])
        t += dist(r[-1], depot)
        return t

    def ins_delta(r, pos, c):
        l = depot if pos == 0 else r[pos - 1]
        rr = depot if pos == len(r) else r[pos]
        return dist(l, c) + dist(c, rr) - dist(l, rr)

    def two_opt_best(r):
        n = len(r)
        if n < 4:
            return r
        best_gain = 0
        bi = bj = -1
        for i in range(n - 1):
            a = depot if i == 0 else r[i - 1]
            b = r[i]
            for j in range(i + 1, n):
                c = r[j]
                d = depot if j == n - 1 else r[j + 1]
                gain = (dist(a, b) + dist(c, d)) - (dist(a, c) + dist(b, d))
                if gain > best_gain:
                    best_gain = gain
                    bi = i
                    bj = j
        if best_gain > 1e-12:
            return r[:bi] + r[bi:bj + 1][::-1] + r[bj + 1:]
        return r

    cust = [c for c in customers if c != depot]
    cust.sort(key=lambda c: (-dem(c), dist(depot, c), c))

    unserved = {}
    for c in cust:
        unserved[c] = True

    routes = []

    # Construct by seed-and-extend with regret-aware choices
    while unserved:
        seed = None
        sk = None
        for c in cust:
            if c in unserved:
                k = (dist(depot, c), -dem(c), c)
                if sk is None or k < sk:
                    sk = k
                    seed = c
        if seed is None:
            break
        r = [seed]
        del unserved[seed]
        load = dem(seed)
        last = seed
        while True:
            best = None
            bk = None
            for c in cust:
                if c not in unserved:
                    continue
                d = dem(c)
                if load + d > capacity:
                    continue
                k = (dist(last, c), dist(depot, c), -d, c)
                if bk is None or k < bk:
                    bk = k
                    best = c
            if best is None:
                break
            r.append(best)
            del unserved[best]
            load += dem(best)
            last = best
        routes.append(r)

    # Repair any leftovers by cheapest insertion
    if unserved:
        leftovers = list(unserved.keys())
        for c in leftovers:
            best_r = -1
            best_p = -1
            best_d = None
            for ri in range(len(routes)):
                r = routes[ri]
                if route_load(r) + dem(c) > capacity:
                    continue
                for p in range(len(r) + 1):
                    d = ins_delta(r, p, c)
                    if best_d is None or d < best_d or (d == best_d and (ri, p, c) < (best_r, best_p, c)):
                        best_d = d
                        best_r = ri
                        best_p = p
            if best_r >= 0:
                routes[best_r].insert(best_p, c)
            else:
                routes.append([c])

    # Intra-route improvement
    for idx in range(len(routes)):
        routes[idx] = two_opt_best(routes[idx])

    # Merge routes if feasible and beneficial
    improved = True
    while improved:
        improved = False
        best_i = -1
        best_j = -1
        best_gain = 0
        best_new = None
        for i in range(len(routes)):
            ri = routes[i]
            li = route_load(ri)
            for j in range(i + 1, len(routes)):
                rj = routes[j]
                if li + route_load(rj) > capacity:
                    continue
                candidates = []
                a = ri + rj
                b = ri + rj[::-1]
                c = ri[::-1] + rj
                d = ri[::-1] + rj[::-1]
                for cand in (a, b, c, d):
                    candidates.append(cand)
                old = route_cost(ri) + route_cost(rj)
                for cand in candidates:
                    gain = old - route_cost(cand)
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best_i = i
                        best_j = j
                        best_new = cand
        if best_i >= 0:
            routes[best_i] = best_new
            del routes[best_j]
            improved = True

    # Final cleanup: remove empties, sort routes by first customer for determinism
    cleaned = []
    for r in routes:
        if r:
            cleaned.append(r)
    cleaned.sort(key=lambda r: (r[0], len(r), route_cost(r)))
    return cleaned
