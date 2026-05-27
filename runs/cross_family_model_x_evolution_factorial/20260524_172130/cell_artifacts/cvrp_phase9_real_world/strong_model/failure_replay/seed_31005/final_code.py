def solve_cvrp(instance):
    def get_field(obj, names, default=None):
        if isinstance(obj, dict):
            for n in names:
                if n in obj:
                    return obj[n]
            return default
        d = None
        try:
            d = obj.__dict__
        except:
            d = None
        if d is not None:
            for n in names:
                if n in d:
                    return d[n]
        for n in names:
            try:
                return object.__getattribute__(obj, n)
            except:
                pass
        return default

    coords = get_field(instance, ("coords", "locations", "points", "xy", "nodes"), None)
    demands = get_field(instance, ("demands", "demand"), None)
    capacity = get_field(instance, ("capacity", "vehicle_capacity", "cap"), None)
    depot = get_field(instance, ("depot", "depot_id", "start", "origin"), 0)

    if coords is None:
        return []

    n = len(coords)
    if n == 0:
        return []

    if demands is None:
        demands = [0] * n
    if capacity is None:
        capacity = 0

    if isinstance(depot, (list, tuple)):
        depot = depot[0] if depot else 0
    depot = int(depot)

    def xy(i):
        p = coords[i]
        return p[0], p[1]

    def dist(i, j):
        ax, ay = xy(i)
        bx, by = xy(j)
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    def route_demand(route):
        s = 0
        for c in route:
            s += demands[c]
        return s

    def route_cost(route):
        if not route:
            return 0.0
        c = dist(depot, route[0]) + dist(route[-1], depot)
        k = 0
        while k + 1 < len(route):
            c += dist(route[k], route[k + 1])
            k += 1
        return c

    def insertion_cost(route, pos, cust):
        prev_node = depot if pos == 0 else route[pos - 1]
        next_node = depot if pos == len(route) else route[pos]
        return dist(prev_node, cust) + dist(cust, next_node) - dist(prev_node, next_node)

    customers = []
    i = 0
    while i < n:
        if i != depot:
            customers.append(i)
        i += 1

    unrouted = set(customers)
    routes = []

    while unrouted:
        start = None
        best_key = None
        for c in unrouted:
            d = demands[c]
            if d > capacity and capacity > 0:
                continue
            key = (-d, dist(depot, c), c)
            if best_key is None or key < best_key:
                best_key = key
                start = c
        if start is None:
            start = min(unrouted, key=lambda c: (demands[c], dist(depot, c), c))

        route = [start]
        unrouted.remove(start)
        load = demands[start]

        while unrouted:
            best_choice = None
            best_c = None
            best_pos = None
            for c in unrouted:
                d = demands[c]
                if capacity > 0 and load + d > capacity:
                    continue
                pos = 0
                while pos <= len(route):
                    ins = insertion_cost(route, pos, c)
                    prev_node = depot if pos == 0 else route[pos - 1]
                    next_node = depot if pos == len(route) else route[pos]
                    key = (ins, dist(prev_node, c) + dist(c, next_node), dist(depot, c), c, pos)
                    if best_choice is None or key < best_choice:
                        best_choice = key
                        best_c = c
                        best_pos = pos
                    pos += 1
            if best_c is None:
                break
            route.insert(best_pos, best_c)
            unrouted.remove(best_c)
            load += demands[best_c]

        routes.append(route)

    changed = True
    while changed:
        changed = False

        # Intra-route 2-opt
        r_idx = 0
        while r_idx < len(routes):
            route = routes[r_idx]
            m = len(route)
            if m >= 4:
                best_delta = 0.0
                best_i = None
                best_j = None
                i = 0
                while i < m - 1:
                    a = depot if i == 0 else route[i - 1]
                    b = route[i]
                    j = i + 2
                    while j < m:
                        c = route[j - 1]
                        d = depot if j == m else route[j]
                        delta = (dist(a, c) + dist(b, d)) - (dist(a, b) + dist(c, d))
                        if delta < best_delta - 1e-12:
                            best_delta = delta
                            best_i = i
                            best_j = j
                        j += 1
                    i += 1
                if best_i is not None:
                    route[best_i:best_j] = reversed(route[best_i:best_j])
                    changed = True
            r_idx += 1

        # Relocate between routes
        i = 0
        moved = False
        while i < len(routes) and not moved:
            j = 0
            while j < len(routes) and not moved:
                if i != j:
                    ri = routes[i]
                    rj = routes[j]
                    if ri:
                        load_j = route_demand(rj)
                        best_move = None
                        best_p = None
                        best_pos = None
                        p = 0
                        while p < len(ri):
                            c = ri[p]
                            dc = demands[c]
                            if capacity <= 0 or load_j + dc <= capacity:
                                rem_prev = depot if p == 0 else ri[p - 1]
                                rem_next = depot if p == len(ri) - 1 else ri[p + 1]
                                remove_delta = dist(rem_prev, rem_next) - dist(rem_prev, c) - dist(c, rem_next)
                                pos = 0
                                while pos <= len(rj):
                                    add_delta = insertion_cost(rj, pos, c)
                                    delta = remove_delta + add_delta
                                    key = (delta, c, p, pos)
                                    if best_move is None or key < best_move:
                                        best_move = key
                                        best_p = p
                                        best_pos = pos
                                    pos += 1
                            p += 1
                        if best_move is not None and best_move[0] < -1e-12:
                            c = ri.pop(best_p)
                            if best_pos > len(rj):
                                best_pos = len(rj)
                            rj.insert(best_pos, c)
                            changed = True
                            moved = True
                j += 1
            i += 1

        # Remove empty routes
        new_routes = []
        for r in routes:
            if r:
                new_routes.append(r)
        routes = new_routes

    routes.sort(key=lambda r: (r[0], len(r), route_cost(r)))
    return routes
