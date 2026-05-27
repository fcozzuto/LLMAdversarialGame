def solve_cvrp(instance):
    def is_mapping(x):
        try:
            x.keys()
            return True
        except:
            return False

    def get_field(*names):
        if is_mapping(instance):
            for n in names:
                try:
                    if n in instance:
                        return instance[n]
                except:
                    pass
        for n in names:
            try:
                return instance[n]
            except:
                pass
        return None

    depot = get_field("depot", "depot_id", "start", "origin", "source")
    capacity = get_field("capacity", "vehicle_capacity", "Q", "cap")
    demands = get_field("demands", "demand", "loads", "d")
    coords = get_field("coords", "coordinates", "points", "loc", "locations", "xy")
    nodes = get_field("nodes", "customers", "customer_ids", "ids")

    if nodes is None and demands is not None:
        try:
            nodes = list(demands.keys()) if is_mapping(demands) else list(range(len(demands)))
        except:
            nodes = []
    if nodes is None and coords is not None:
        try:
            nodes = list(coords.keys()) if is_mapping(coords) else list(range(len(coords)))
        except:
            nodes = []
    if nodes is None:
        nodes = []

    if depot is None:
        depot = 0 if (0 in nodes or not nodes) else nodes[0]

    customers = [n for n in nodes if n != depot]

    def get_dem(n):
        if demands is None:
            return 1
        try:
            if is_mapping(demands):
                return demands.get(n, 1)
        except:
            pass
        try:
            return demands[n]
        except:
            try:
                return demands[n - 1 if depot == 0 else n]
            except:
                return 1

    def get_xy(n):
        if coords is None:
            return (0.0, 0.0)
        try:
            if is_mapping(coords):
                c = coords.get(n, None)
                if c is not None:
                    return (float(c[0]), float(c[1]))
        except:
            pass
        try:
            c = coords[n]
            return (float(c[0]), float(c[1]))
        except:
            try:
                c = coords[n - 1 if depot == 0 else n]
                return (float(c[0]), float(c[1]))
            except:
                return (0.0, 0.0)

    if capacity is None:
        s = 0
        for c in customers:
            s += get_dem(c)
        capacity = s if s > 0 else 1

    dx0, dy0 = get_xy(depot)

    def dist(a, b):
        ax, ay = get_xy(a)
        bx, by = get_xy(b)
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    def route_load(r):
        s = 0
        for c in r:
            s += get_dem(c)
        return s

    def route_cost(r):
        if not r:
            return 0.0
        c = dist(depot, r[0]) + dist(r[-1], depot)
        i = 0
        while i + 1 < len(r):
            c += dist(r[i], r[i + 1])
            i += 1
        return c

    def insert_cost(r, pos, c):
        if not r:
            return 0.0
        if pos == 0:
            return dist(depot, c) + dist(c, r[0]) - dist(depot, r[0])
        if pos == len(r):
            return dist(r[-1], c) + dist(c, depot) - dist(r[-1], depot)
        return dist(r[pos - 1], c) + dist(c, r[pos]) - dist(r[pos - 1], r[pos])

    def angle_key(c):
        x, y = get_xy(c)
        return ((y - dy0) / (abs(x - dx0) + abs(y - dy0) + 1e-12), x, y, c)

    # Initial sweep by angle
    ordered = sorted(customers, key=angle_key)
    routes = []
    cur = []
    load = 0
    for c in ordered:
        d = get_dem(c)
        if d > capacity:
            if cur:
                routes.append(cur)
                cur = []
                load = 0
            routes.append([c])
            continue
        if cur and load + d > capacity:
            routes.append(cur)
            cur = [c]
            load = d
        else:
            cur.append(c)
            load += d
    if cur:
        routes.append(cur)

    # Repair duplicates/missing
    seen = {}
    cleaned = []
    for r in routes:
        nr = []
        for c in r:
            if c not in seen:
                seen[c] = 1
                nr.append(c)
        if nr:
            cleaned.append(nr)
    routes = cleaned
    missing = []
    for c in customers:
        if c not in seen:
            missing.append(c)

    for c in missing:
        d = get_dem(c)
        best = None
        bi = -1
        bp = -1
        for i in range(len(routes)):
            r = routes[i]
            if route_load(r) + d <= capacity:
                for p in range(len(r) + 1):
                    inc = insert_cost(r, p, c)
                    if best is None or inc < best:
                        best = inc
                        bi = i
                        bp = p
        if bi == -1:
            routes.append([c])
        else:
            routes[bi].insert(bp, c)

    # Merge tiny routes greedily
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(routes):
            if len(routes[i]) == 1:
                c = routes[i][0]
                d = get_dem(c)
                best = None
                bj = -1
                bp = -1
                j = 0
                while j < len(routes):
                    if j != i and route_load(routes[j]) + d <= capacity:
                        r = routes[j]
                        for p in range(len(r) + 1):
                            inc = insert_cost(r, p, c)
                            if best is None or inc < best:
                                best = inc
                                bj = j
                                bp = p
                    j += 1
                if bj != -1:
                    routes[bj].insert(bp, c)
                    routes.pop(i)
                    changed = True
                    continue
            i += 1

    # Local search within routes: 2-opt
    def two_opt_route(r):
        n = len(r)
        if n < 4:
            return r
        improved = True
        while improved:
            improved = False
            i = 0
            while i + 2 < n:
                j = i + 2
                while j < n:
                    a = depot if i == 0 else r[i - 1]
                    b = r[i]
                    c = r[j - 1]
                    d = depot if j == n else r[j]
                    before = dist(a, b) + dist(c, d)
                    after = dist(a, c) + dist(b, d)
                    if after + 1e-12 < before:
                        r[i:j] = reversed(r[i:j])
                        improved = True
                    j += 1
                i += 1
        return r

    for idx in range(len(routes)):
        routes[idx] = two_opt_route(routes[idx])

    # Cross-route relocate improvement
    improved = True
    while improved:
        improved = False
        best_delta = 0.0
        best_move = None
        for i in range(len(routes)):
            r1 = routes[i]
            for p in range(len(r1)):
                c = r1[p]
                d = get_dem(c)
                rem_delta = insert_cost(r1, p, c)  # not used directly
                # removal delta
                prevn = depot if p == 0 else r1[p - 1]
                nextn = depot if p == len(r1) - 1 else r1[p + 1]
                delta_remove = dist(prevn, nextn) - dist(prevn, c) - dist(c, nextn)
                for j in range(len(routes)):
                    if j == i:
                        continue
                    r2 = routes[j]
                    if route_load(r2) + d > capacity:
                        continue
                    for q in range(len(r2) + 1):
                        delta_insert = insert_cost(r2, q, c)
                        delta = delta_remove + delta_insert
                        if delta < best_delta:
                            best_delta = delta
                            best_move = (i, p, j, q, c)
        if best_move is not None:
            i, p, j, q, c = best_move
            if i < j:
                routes[j].insert(q, c)
                routes[i].pop(p)
            else:
                routes[i].pop(p)
                routes[j].insert(q, c)
