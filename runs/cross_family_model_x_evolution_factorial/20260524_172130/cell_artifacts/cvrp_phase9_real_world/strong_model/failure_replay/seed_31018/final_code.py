def solve_cvrp(instance):
    def get(obj, *names, default=None):
        for n in names:
            try:
                return obj[n]
            except:
                pass
            try:
                return obj.__dict__[n]
            except:
                pass
            try:
                return object.__getattribute__(obj, n)
            except:
                pass
        return default

    depot = get(instance, "depot", "depot_id", default=0)
    cap = get(instance, "capacity", "vehicle_capacity", default=10**18)
    dm = get(instance, "distance_matrix", "dist_matrix", "matrix", default=None)

    coords = {}
    crd = get(instance, "coords", "coordinates", "points", default=None)
    try:
        for k in crd.keys():
            coords[k] = crd[k]
    except:
        try:
            for i in range(len(crd)):
                coords[i] = crd[i]
        except:
            pass

    dem = {}
    dr = get(instance, "demands", "demand", default=None)
    try:
        for k in dr.keys():
            dem[k] = dr[k]
    except:
        try:
            for i in range(len(dr)):
                dem[i] = dr[i]
        except:
            pass
    dem[depot] = 0

    customers = get(instance, "customers", "nodes", "customer_ids", default=None)
    if customers is None:
        customers = []
        try:
            n = len(dm)
            for i in range(n):
                if i != depot:
                    customers.append(i)
        except:
            if coords:
                for k in coords:
                    if k != depot:
                        customers.append(k)
            else:
                n = get(instance, "n", "num_customers", default=0) or 0
                i = 1
                while i <= n:
                    customers.append(i)
                    i += 1
    else:
        try:
            customers = list(customers)
        except:
            tmp = []
            try:
                i = 0
                while True:
                    tmp.append(customers[i])
                    i += 1
            except:
                pass
            customers = tmp

    idx = {}
    try:
        if dm is not None and type(dm) is not dict:
            seq = customers + [depot]
            i = 0
            while i < len(seq):
                idx[seq[i]] = i
                i += 1
    except:
        pass

    def dist(a, b):
        if a == b:
            return 0
        if dm is not None:
            try:
                return dm[a][b]
            except:
                try:
                    return dm[idx[a]][idx[b]]
                except:
                    pass
        pa = coords.get(a)
        pb = coords.get(b)
        if pa is None or pb is None:
            return 0
        dx = pa[0] - pb[0]
        dy = pa[1] - pb[1]
        return (dx * dx + dy * dy) ** 0.5

    def route_load(route):
        s = 0
        i = 0
        while i < len(route):
            s += dem.get(route[i], 0)
            i += 1
        return s

    def route_cost(route):
        if not route:
            return 0
        c = dist(depot, route[0])
        i = 0
        while i + 1 < len(route):
            c += dist(route[i], route[i + 1])
            i += 1
        return c + dist(route[-1], depot)

    def insertion_delta(route, pos, c):
        if not route:
            return dist(depot, c) + dist(c, depot)
        if pos == 0:
            return dist(depot, c) + dist(c, route[0]) - dist(depot, route[0])
        if pos == len(route):
            return dist(route[-1], c) + dist(c, depot) - dist(route[-1], depot)
        a = route[pos - 1]
        b = route[pos]
        return dist(a, c) + dist(c, b) - dist(a, b)

    def best_insert(route, c):
        bp = 0
        bd = None
        p = 0
        while p <= len(route):
            d = insertion_delta(route, p, c)
            if bd is None or d < bd or (d == bd and p < bp):
                bp = p
                bd = d
            p += 1
        return bp

    def two_opt(route):
        r = route[:]
        n = len(r)
        if n < 4:
            return r
        improved = True
        while improved:
            improved = False
            i = 0
            while i < n - 1:
                a = depot if i == 0 else r[i - 1]
                b = r[i]
                j = i + 1
                while j < n:
                    c = r[j]
                    d = depot if j == n - 1 else r[j + 1]
                    if dist(a, c) + dist(b, d) < dist(a, b) + dist(c, d):
                        r[i:j + 1] = r[i:j + 1][::-1]
                        improved = True
                        break
                    j += 1
                if improved:
                    break
                i += 1
        return r

    def swap_improve(route):
        r = route[:]
        n = len(r)
        if n < 2:
            return r
        improved = True
        while improved:
            improved = False
            i = 0
            while i < n:
                j = i + 1
                while j < n:
                    before = route_cost(r)
                    r[i], r[j] = r[j], r[i]
                    after = route_cost(r)
                    if after < before:
                        improved = True
                        break
                    r[i], r[j] = r[j], r[i]
                    j += 1
                if improved:
                    break
                i += 1
        return r

    unassigned = customers[:]
    unassigned.sort(key=lambda c: (-dem.get(c, 0), c))
    routes = []

    while unassigned:
        seed = unassigned.pop(0)
        route = [seed]
        load = dem.get(seed, 0)
        while True:
            best = None
            best_key = None
            i = 0
            while i < len(unassigned):
                c = unassigned[i]
                d = dem.get(c, 0)
                if load + d <= cap:
                    k = (dist(route[-1], c), dist(depot, c), -d, c)
                    if best_key is None or k < best_key:
                        best_key = k
                        best = i
                i += 1
            if best is None:
                break
            c = unassigned.pop(best)
            route.append(c)
            load += dem.get(c, 0)
        routes.append(route)

    i = 0
    while i < len(routes):
        routes[i] = two_opt(routes[i])
        routes[i] = swap_improve(routes[i])
        i += 1

    changed = True
    while changed:
        changed = False

        best_move = None
        best_gain = 0

        i = 0
        while i < len(routes):
            ri = routes[i]
            li = route_load(ri)
            p = 0
            while p < len(ri):
                c = ri[p]
                rem_gain = 0
                if len(ri) == 1:
                    rem_gain = route_cost(ri)
                else:
                    left = depot if p == 0 else ri[p - 1]
                    right = depot if p == len(ri) - 1 else ri[p + 1]
                    rem_gain = dist(left, c) + dist(c, right) - dist(left, right)
                j = 0
                while j < len(routes):
                    if i != j:
                        rj = routes[j]
                        if route_load(rj) + dem.get(c, 0) <= cap:
                            pos = best_insert(rj, c)
                            ins_gain = insertion_delta(rj, pos, c)
                            gain = rem_gain - ins_gain
                            if gain > best_gain or (gain == best_gain and (i, p, j, pos, c) < best_move if best_move is not None else True):
                                best_gain = gain
                                best_move = (i, p, j, pos, c)
                    j += 1
                p += 1
            i += 1

        if best_move is not None and best_gain > 1e-12:
            i, p, j, pos, c = best_move
            routes[i].pop(p)
            routes[j].insert(pos, c)
            if len(routes[i]) == 0:
                routes.pop(i)
                if i < j:
                    j -= 1
