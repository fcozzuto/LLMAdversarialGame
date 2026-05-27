def solve_cvrp(instance):
    def get(x, names, default=None):
        try:
            for n in names:
                try:
                    return x[n]
                except:
                    pass
                try:
                    d = x.__dict__
                    if n in d:
                        return d[n]
                except:
                    pass
        except:
            pass
        return default

    depot = get(instance, ("depot_id", "depot", "depot_index"), 0)
    cap = get(instance, ("capacity", "vehicle_capacity", "capacity_limit"), None)
    demands = get(instance, ("demands", "demand"), None)
    coords = get(instance, ("coords", "coordinates", "positions", "xy"), None)
    dist = get(instance, ("distance_matrix", "distances", "distance"), None)
    n = get(instance, ("n", "num_nodes", "n_nodes"), None)

    def seq(x):
        try:
            len(x)
            return True
        except:
            return False

    def dem(i):
        try:
            if demands is None:
                return 0
            v = demands[i]
            return 0 if v is None else v
        except:
            return 0

    def xy(i):
        try:
            if coords is None:
                return None
            p = coords[i]
            if len(p) >= 2:
                return p[0], p[1]
        except:
            pass
        return None

    def d(i, j):
        if dist is not None:
            try:
                v = dist[i][j]
                if v is not None:
                    return v
            except:
                pass
            try:
                v = dist[i, j]
                if v is not None:
                    return v
            except:
                pass
        a = xy(i)
        b = xy(j)
        if a is not None and b is not None:
            dx = a[0] - b[0]
            dy = a[1] - b[1]
            return (dx * dx + dy * dy) ** 0.5
        return abs(i - j)

    cust = []
    if seq(demands):
        for i in range(len(demands)):
            if i != depot:
                cust.append(i)
    elif seq(coords):
        for i in range(len(coords)):
            if i != depot:
                cust.append(i)
    elif n is not None:
        try:
            for i in range(int(n)):
                if i != depot:
                    cust.append(i)
        except:
            pass
    cust.sort()

    if cap is None:
        s = 0
        for i in cust:
            v = dem(i)
            if v > 0:
                s += v
        cap = s if s > 0 else 1

    cust = [i for i in cust if dem(i) <= cap]
    rem = {}
    for i in cust:
        rem[i] = 1

    def rload(r):
        s = 0
        for i in r:
            s += dem(i)
        return s

    def rcost(r):
        if not r:
            return 0
        c = d(depot, r[0])
        for i in range(len(r) - 1):
            c += d(r[i], r[i + 1])
        c += d(r[-1], depot)
        return c

    routes = []
    while rem:
        seed = None
        sk = None
        for i in rem:
            k = (dem(i), -d(depot, i), -i)
            if seed is None or k > sk:
                seed = i
                sk = k
        r = [seed]
        load = dem(seed)
        del rem[seed]
        while True:
            best = None
            bestk = None
            for i in rem:
                di = dem(i)
                if load + di > cap:
                    continue
                m = len(r)
                for pos in range(m + 1):
                    if pos == 0:
                        delta = d(depot, i) + d(i, r[0]) - d(depot, r[0])
                    elif pos == m:
                        delta = d(r[-1], i) + d(i, depot) - d(r[-1], depot)
                    else:
                        a = r[pos - 1]
                        b = r[pos]
                        delta = d(a, i) + d(i, b) - d(a, b)
                    k = (delta, i, pos)
                    if best is None or k < bestk:
                        best = (i, pos)
                        bestk = k
            if best is None:
                break
            i, pos = best
            r.insert(pos, i)
            load += dem(i)
            del rem[i]
        routes.append(r)

    # Merge by savings
    route_of = {}
    loads = []
    active = []
    for idx, r in enumerate(routes):
        loads.append(rload(r))
        active.append(True)
        for i in r:
            route_of[i] = idx

    sav = []
    for a in cust:
        for b in cust:
            if a < b:
                sav.append((d(depot, a) + d(depot, b) - d(a, b), a, b))
    sav.sort(key=lambda x: (-x[0], x[1], x[2]))

    for _, a, b in sav:
        ra = route_of.get(a)
        rb = route_of.get(b)
        if ra is None or rb is None or ra == rb:
            continue
        if not active[ra] or not active[rb]:
            continue
        A = routes[ra]
        B = routes[rb]
        if loads[ra] + loads[rb] > cap or not A or not B:
            continue
        merged = None
        if A[-1] == a and B[0] == b:
            merged = A + B
        elif A[-1] == a and B[-1] == b:
            merged = A + B[::-1]
        elif A[0] == a and B[0] == b:
            merged = A[::-1] + B
        elif A[0] == a and B[-1] == b:
            merged = A[::-1] + B[::-1]
        if merged is None:
            continue
        if rcost(merged) <= rcost(A) + rcost(B):
            routes[ra] = merged
            loads[ra] += loads[rb]
            active[rb] = False
            for i in merged:
                route_of[i] = ra

    routes = [routes[i] for i in range(len(routes)) if active[i] and routes[i]]

    # Intra-route 2-opt
    for idx in range(len(routes)):
        r = routes[idx]
        improved = True
        while improved and len(r) >= 4:
            improved = False
            base = rcost(r)
            best_gain = 0
            bi = bj = -1
            m = len(r)
            for i in range(m - 1):
                for j in range(i + 1, m):
                    nr = r[:i] + r[i:j + 1][::-1] + r[j + 1:]
                    gain = base - rcost(nr)
                    if gain > best_gain:
                        best_gain = gain
                        bi, bj = i, j
            if best_gain > 0:
                r = r[:bi] + r[bi:bj + 1][::-1] + r[bj + 1:]
                improved = True
        routes[idx] = r

    # Repair duplicates/missing
    cnt = {}
    for r in routes:
        for i in r:
            cnt[i] = cnt.get(i, 0) + 1
    missing = [i for i in cust if cnt.get(i, 0) == 0]

    for idx in range(len(routes)):
        seen = {}
        nr = []
        for i in routes[idx]:
            if seen.get(i, 0) == 0 and cnt.get(i, 0) > 0:
                nr.append(i)
                seen[i] = 1
            if cnt.get(i, 0) > 0:
                cnt[i] -= 1
        routes[idx] = nr

    for i in missing:
        best = None
        bestk = None
        di = dem(i)
        for ridx in range(len(routes)):
            r = routes[ridx]
            if rload(r) + di > cap:
                continue
            for pos in range(len(r) + 1):
                if pos == 0:
                    delta = d(depot, i) + d(i, r[0]) - d(depot, r[0])
                elif pos == len(r):
                    delta = d(r[-1], i) + d(i, depot) - d(r[-1], depot)
                else:
                    a = r[pos - 1]
                    b = r[pos]
                    delta = d(a, i) + d(i, b) - d(a, b)
                k = (delta, ridx, pos)
                if best is None or k < bestk:
                    best = (ridx, pos)
                    bestk = k
        if best is None:
            routes.append([i])
        else:
            ridx, pos = best
            routes[ridx].insert(pos, i)

    return [r for r in routes if r]
