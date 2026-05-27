def solve_cvrp(instance):
    def as_dict(obj):
        if isinstance(obj, dict):
            return obj
        try:
            d = vars(obj)
            if isinstance(d, dict):
                return d
        except:
            pass
        return {}

    data = as_dict(instance)

    def pick(keys, default=None):
        for k in keys:
            if k in data:
                return data[k]
        return default

    coords = pick(["coords", "coordinates", "points", "loc", "locations", "xy"])
    demands = pick(["demands", "demand", "q"])
    capacity = pick(["capacity", "vehicle_capacity", "cap"])
    depot = pick(["depot", "depot_id"], 0)
    n = pick(["n", "num_nodes", "size"], None)

    if coords is None:
        if n is None:
            if isinstance(demands, (list, tuple)):
                n = len(demands)
            elif isinstance(demands, dict) and demands:
                n = max(demands) + 1
            else:
                return []
        coords = [(0.0, 0.0)] * n
    elif isinstance(coords, dict):
        max_id = -1
        for k in coords:
            if k > max_id:
                max_id = k
        arr = [(0.0, 0.0)] * (max_id + 1)
        for k in coords:
            arr[k] = coords[k]
        coords = arr
    else:
        coords = list(coords)

    n = len(coords)

    if isinstance(depot, bool):
        depot = 0
    try:
        depot = int(depot)
    except:
        depot = 0
    if depot < 0 or depot >= n:
        depot = 0

    if demands is None:
        demands = [0] * n
    elif isinstance(demands, dict):
        arr = [0] * n
        for k in demands:
            if 0 <= k < n:
                arr[k] = demands[k]
        demands = arr
    else:
        demands = list(demands)
        if len(demands) < n:
            demands += [0] * (n - len(demands))
        elif len(demands) > n:
            demands = demands[:n]

    if capacity is None:
        capacity = sum(demands)

    try:
        capacity = float(capacity)
    except:
        capacity = sum(demands)

    def dist(i, j):
        a = coords[i]
        b = coords[j]
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    customers = []
    for i in range(n):
        if i != depot and demands[i] >= 0:
            customers.append(i)

    if not customers:
        return []

    if any(demands[c] > capacity for c in customers):
        return [[c] for c in sorted(customers)]

    unassigned = customers[:]
    unassigned_set = set(unassigned)
    radial = sorted(customers, key=lambda c: (dist(depot, c), -demands[c], c))
    routes = []

    while unassigned_set:
        start = None
        for c in radial:
            if c in unassigned_set and demands[c] <= capacity:
                start = c
                break
        if start is None:
            start = min(unassigned_set)
        route = [start]
        load = demands[start]
        unassigned_set.remove(start)
        curr = start

        while True:
            best = None
            best_key = None
            for c in unassigned_set:
                if load + demands[c] > capacity:
                    continue
                key = (dist(curr, c) - 0.15 * dist(depot, c) + 0.001 * demands[c], dist(depot, c), c)
                if best_key is None or key < best_key:
                    best_key = key
                    best = c
            if best is None:
                break
            route.append(best)
            load += demands[best]
            unassigned_set.remove(best)
            curr = best
        routes.append(route)

    def route_load(route):
        s = 0
        for c in route:
            s += demands[c]
        return s

    def route_cost(route):
        if not route:
            return 0.0
        total = dist(depot, route[0])
        for i in range(len(route) - 1):
            total += dist(route[i], route[i + 1])
        total += dist(route[-1], depot)
        return total

    def two_opt(route):
        if len(route) < 4:
            return route
        improved = True
        while improved:
            improved = False
            base = route_cost(route)
            best_gain = 0.0
            best_i = -1
            best_k = -1
            for i in range(len(route) - 2):
                for k in range(i + 2, len(route)):
                    if i == 0 and k == len(route) - 1:
                        continue
                    new_route = route[:i + 1] + route[i + 1:k + 1][::-1] + route[k + 1:]
                    gain = base - route_cost(new_route)
                    if gain > best_gain + 1e-12 or (abs(gain - best_gain) <= 1e-12 and (i, k) < (best_i, best_k)):
                        best_gain = gain
                        best_i = i
                        best_k = k
            if best_gain > 1e-12:
                route = route[:best_i + 1] + route[best_i + 1:best_k + 1][::-1] + route[best_k + 1:]
                improved = True
        return route

    routes = [two_opt(r[:]) for r in routes if r]

    def total_cost(rs):
        s = 0.0
        for r in rs:
            s += route_cost(r)
        return s

    changed = True
    while changed:
        changed = False
        routes = [r for r in routes if r]
        routes.sort(key=lambda r: (len(r), route_cost(r), r))

        # merge singleton into best insertion
        i = 0
        while i < len(routes):
            if len(routes[i]) != 1:
                i += 1
                continue
            c = routes[i][0]
            best = None
            best_j = -1
            best_p = -1
            for j in range(len(routes)):
                if j == i:
                    continue
                t = routes[j]
                if route_load(t) + demands[c] > capacity:
                    continue
                for p in range(len(t) + 1):
                    prev_node = depot if p == 0 else t[p - 1]
                    next_node = depot if p == len(t) else t[p]
                    delta = dist(prev_node, c) + dist(c, next_node) - dist(prev_node, next_node)
                    key = (delta, j, p)
                    if best is None or key < best:
                        best = key
                        best_j = j
                        best_p = p
            if best is not None:
                routes[best_j].insert(best_p, c)
                routes.pop(i)
                changed = True
                continue
            i += 1

        # relocate single customer if improves total cost
        current_total = total_cost(routes)
        best_move = None
        for i in range(len(routes)):
            r = routes[i]
            for pos in range(len(r)):
                c = r[pos]
                r_removed = r[:pos] + r[pos + 1:]
                for j in range(len(routes)):
                    if i == j:
                        continue
                    t = routes[j]
                    if route_load(t) + demands[c] > capacity:
                        continue
                    for p in range(len(t) + 1):
                        new_t = t[:p] + [c] + t[p:]
                        new_routes = []
                        for idx in range(len(routes)):
                            if idx == i:
                                if r_removed:
                                    new_routes.append(r_removed)
                            elif idx == j:
                                new_routes.append(new_t)
                            else:
                                new_routes.append(routes[idx])
                        new_total = total_cost(new_routes)
                        delta = new_total - current_total
                        key = (delta, i, pos, j, p, c)
                        if delta < -1e-12 and (best_move is None or key < best_move[0]):
                            best_move = (key, new_routes)
        if best_move is not None:
            routes = [r for r in best_move[1] if r]
            routes = [two_opt(r[:]) for r in routes]
            changed = True

    routes = [r for r in routes if r]
    routes.sort(key=lambda r: (len(r), route_cost(r), r))
    return routes
