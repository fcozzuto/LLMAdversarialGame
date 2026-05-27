def solve_cvrp(instance):
    def fetch(obj, names, default=None):
        try:
            d = obj.__dict__
            for n in names:
                if n in d:
                    return d[n]
        except:
            pass
        try:
            for n in names:
                try:
                    return obj[n]
                except:
                    pass
        except:
            pass
        try:
            for n in names:
                if n in obj:
                    return obj[n]
        except:
            pass
        return default

    demands = fetch(instance, ("demands", "demand"), None)
    capacity = fetch(instance, ("capacity", "vehicle_capacity"), None)
    dist = fetch(instance, ("distance_matrix", "distances"), None)
    coords = fetch(instance, ("coords", "coordinates"), None)
    depot = fetch(instance, ("depot",), 0)
    customers = fetch(instance, ("customers",), None)

    n = None
    if demands is not None:
        n = len(demands)
    elif dist is not None:
        n = len(dist)
    elif coords is not None:
        n = len(coords)

    if customers is None:
        if n is None:
            customers = []
        else:
            customers = list(range(n))
            if depot in customers:
                customers = [c for c in customers if c != depot]
            elif depot == 0 and customers and customers[0] == 0:
                customers = customers[1:]

    def demand(i):
        if demands is None:
            return 1
        return demands[i]

    def d(i, j):
        if dist is not None:
            return dist[i][j]
        xi, yi = coords[i]
        xj, yj = coords[j]
        dx = xi - xj
        dy = yi - yj
        return (dx * dx + dy * dy) ** 0.5

    if capacity is None:
        capacity = 0
        for c in customers:
            capacity += demand(c)
        if capacity <= 0:
            capacity = 1

    # Precompute polar order / nearest order as deterministic constructions.
    ordered1 = []
    ordered2 = []
    if coords is not None:
        dx0, dy0 = coords[depot]
        tmp = []
        for c in customers:
            x, y = coords[c]
            dx1 = x - dx0
            dy1 = y - dy0
            quad = 0
            if dx1 < 0:
                quad = 1
            ang = dy1 / (abs(dx1) + abs(dy1) + 1e-12)
            tmp.append((quad, ang, d(depot, c), c))
        tmp.sort()
        ordered1 = [t[3] for t in tmp]

        tmp = []
        for c in customers:
            x, y = coords[c]
            dx1 = x - dx0
            dy1 = y - dy0
            tmp.append((dx1 * dx1 + dy1 * dy1, c))
        tmp.sort(reverse=True)
        ordered2 = [t[1] for t in tmp]
    else:
        unvisited = customers[:]
        cur = depot
        while unvisited:
            best_i = 0
            best_key = (d(cur, unvisited[0]), unvisited[0])
            k = 1
            while k < len(unvisited):
                cand = unvisited[k]
                key = (d(cur, cand), cand)
                if key < best_key:
                    best_key = key
                    best_i = k
                k += 1
            nxt = unvisited.pop(best_i)
            ordered1.append(nxt)
            cur = nxt
        ordered2 = customers[:]
        ordered2.sort(reverse=True)

    def build_routes(order):
        rs = []
        r = []
        load = 0
        for c in order:
            dc = demand(c)
            if dc > capacity:
                if r:
                    rs.append(r)
                    r = []
                    load = 0
                rs.append([c])
                continue
            if r and load + dc > capacity:
                rs.append(r)
                r = [c]
                load = dc
            else:
                r.append(c)
                load += dc
        if r:
            rs.append(r)
        return rs

    def route_cost(r):
        if not r:
            return 0.0
        total = d(depot, r[0])
        i = 0
        while i + 1 < len(r):
            total += d(r[i], r[i + 1])
            i += 1
        total += d(r[-1], depot)
        return total

    def total_cost(rs):
        s = 0.0
        for r in rs:
            s += route_cost(r)
        return s

    routes_a = build_routes(ordered1)
    routes_b = build_routes(ordered2)

    # Repair/merge: choose better initial solution by cost.
    routes = routes_a if total_cost(routes_a) <= total_cost(routes_b) else routes_b

    def route_load(r):
        s = 0
        for c in r:
            s += demand(c)
        return s

    def best_insert_pos(route, c):
        best_pos = 0
        best_delta = None
        prev = depot
        pos = 0
        while pos <= len(route):
            nxt = depot if pos == len(route) else route[pos]
            delta = d(prev, c) + d(c, nxt) - d(prev, nxt)
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_pos = pos
            if pos < len(route):
                prev = route[pos]
            pos += 1
        return best_pos, best_delta

    def all_customers_in_routes(rs):
        seen = {}
        for r in rs:
            for c in r:
                seen[c] = seen.get(c, 0) + 1
        return seen

    # Local search: relocate and swap, keeping feasibility.
    improved = True
    guard = 0
    while improved and guard < 8:
        improved = False
        guard += 1

        # Clean empties
        tmp = []
        for r in routes:
            if r:
                tmp.append(r)
        routes = tmp

        # Relocate between routes
        i = 0
        while i < len(routes):
            moved = False
            if i >= len(routes):
                break
            r1 = routes[i]
            p = 0
            while p < len(r1):
                c = r1[p]
                dc = demand(c)
                best_move = None
                best_gain = 0.0
                j = 0
                while j < len(routes):
                    if j != i:
                        r2 = routes[j]
                        if route_load(r2) + dc <= capacity:
                            pos, delta_ins = best_insert_pos(r2, c)
                            a = depot if p == 0 else r1[p - 1]
                            b = depot if p == len(r1) - 1 else r1[p + 1]
                            delta_rem = d(a, b) - d(a, c) - d(c, b)
                            gain = delta_rem - delta_ins
                            if gain > best_gain + 1e-12:
                                best_gain = gain
                                best_move = (j, pos)
                    j += 1
                if best_move is not None:
                    j, pos = best_move
                    routes[j] = routes[j][:pos] + [c] + routes[j][pos:]
                    del r1[p]
                    if not r1:
                        del routes[i]
                        moved = True
                        improved = True
                        break
                    moved = True
                    improved = True
                    break
                p += 1
            if not moved:
                i += 1

        # Intra-route 2-opt
        idx = 0
        while idx < len(routes):
            r = routes[idx]
            n2 = len(r)
            if n2 >= 4:
                changed = True
                while changed:
                    changed = False
                    a = 0
                    while a + 2 < n2 and not changed:
                        b = a + 2
                        while b < n2:
                            x1 = depot if a == 0 else r[a - 1]
                            x2 = r[a]
                            y1 = r[b - 1]
                            y2 = depot if b == n2 else r[b]
                            old = d(x1, x2) + d(y1, y2)
                            new = d(x1, y1) + d(x2, y2)
                            if new + 1e-12 < old:
                                r[a:b] = r[a:b][::-1]
                                improved = True
                                changed = True
                                break
                            b += 1
                        a += 1
            idx += 1

        # Swap between routes
        i = 0
