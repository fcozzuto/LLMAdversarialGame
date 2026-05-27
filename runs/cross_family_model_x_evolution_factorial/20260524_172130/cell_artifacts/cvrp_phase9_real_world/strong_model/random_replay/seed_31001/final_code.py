def solve_cvrp(instance):
    def get_val(keys, default=None):
        try:
            for k in keys:
                try:
                    return instance[k]
                except:
                    pass
        except:
            pass
        try:
            d = instance.__dict__
            for k in keys:
                try:
                    return d[k]
                except:
                    pass
        except:
            pass
        return default

    coords = get_val(["coords", "coord", "locations", "points", "nodes", "node_coords"], None)
    demands = get_val(["demands", "demand"], None)
    capacity = get_val(["capacity", "vehicle_capacity", "cap"], 0)
    depot = get_val(["depot", "depot_id", "depot_index"], 0)

    try:
        capacity = float(capacity)
    except:
        capacity = 0.0

    def is_dict_like(x):
        try:
            x.keys
            return True
        except:
            return False

    def coord_of(i):
        if coords is None:
            return (0.0, 0.0)
        try:
            v = coords[i]
            return (float(v[0]), float(v[1]))
        except:
            return (0.0, 0.0)

    def demand_of(i):
        if demands is None:
            return 0.0
        try:
            if is_dict_like(demands):
                return float(demands.get(i, 0.0))
            return float(demands[i])
        except:
            return 0.0

    def dist(a, b):
        ax, ay = coord_of(a)
        bx, by = coord_of(b)
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    customers = []
    if is_dict_like(coords):
        for k in coords.keys():
            if k != depot:
                customers.append(k)
    else:
        try:
            n = len(coords)
            for i in range(n):
                if i != depot:
                    customers.append(i)
        except:
            if is_dict_like(demands):
                for k in demands.keys():
                    if k != depot:
                        customers.append(k)
            else:
                try:
                    n = len(demands)
                    for i in range(n):
                        if i != depot:
                            customers.append(i)
                except:
                    customers = []

    dx0, dy0 = coord_of(depot)

    def angle_key(i):
        x, y = coord_of(i)
        vx = x - dx0
        vy = y - dy0
        half = 0 if (vy > 0 or (vy == 0 and vx >= 0)) else 1
        if vx == 0:
            slope = 1e100 if vy >= 0 else -1e100
        else:
            slope = vy / vx
        return (half, slope, dist(depot, i), i)

    customers.sort(key=angle_key)

    def route_load(route):
        s = 0.0
        for c in route:
            s += demand_of(c)
        return s

    def route_cost(route):
        if not route:
            return 0.0
        c = dist(depot, route[0]) + dist(route[-1], depot)
        for i in range(len(route) - 1):
            c += dist(route[i], route[i + 1])
        return c

    def two_opt(route):
        n = len(route)
        if n < 4:
            return route[:]
        best = route[:]
        best_cost = route_cost(best)
        improved = True
        while improved:
            improved = False
            for i in range(n - 2):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    cand = best[:i + 1] + best[i + 1:j + 1][::-1] + best[j + 1:]
                    c = route_cost(cand)
                    if c + 1e-12 < best_cost:
                        best = cand
                        best_cost = c
                        improved = True
                        break
                if improved:
                    break
        return best

    routes = []
    unrouted = customers[:]

    while unrouted:
        best_seed_idx = 0
        best_seed_key = None
        for idx, c in enumerate(unrouted):
            key = (demand_of(c) > capacity, dist(depot, c), -demand_of(c), c)
            if best_seed_key is None or key < best_seed_key:
                best_seed_key = key
                best_seed_idx = idx
        seed = unrouted.pop(best_seed_idx)
        route = [seed]
        load = demand_of(seed)

        while True:
            last = route[-1]
            best_idx = -1
            best_key = None
            for idx, c in enumerate(unrouted):
                d = demand_of(c)
                if load + d <= capacity + 1e-12:
                    key = (dist(last, c), dist(depot, c), d, c)
                    if best_key is None or key < best_key:
                        best_key = key
                        best_idx = idx
            if best_idx < 0:
                break
            c = unrouted.pop(best_idx)
            route.append(c)
            load += demand_of(c)

        routes.append(two_opt(route))

    def relocate_once():
        loads = [route_load(r) for r in routes]
        best_move = None
        best_gain = 0.0
        for a in range(len(routes)):
            ra = routes[a]
            for ia in range(len(ra)):
                x = ra[ia]
                prev = depot if ia == 0 else ra[ia - 1]
                nxt = depot if ia == len(ra) - 1 else ra[ia + 1]
                remove_gain = dist(prev, x) + dist(x, nxt) - dist(prev, nxt)
                dx = demand_of(x)
                for b in range(len(routes)):
                    if a == b:
                        continue
                    if loads[b] + dx > capacity + 1e-12:
                        continue
                    rb = routes[b]
                    for pos in range(len(rb) + 1):
                        p = depot if pos == 0 else rb[pos - 1]
                        n = depot if pos == len(rb) else rb[pos]
                        add_cost = dist(p, x) + dist(x, n) - dist(p, n)
                        gain = remove_gain - add_cost
                        if gain > best_gain + 1e-12:
                            best_gain = gain
                            best_move = (a, ia, b, pos)
        if best_move is None:
            return False
        a, ia, b, pos = best_move
        x = routes[a].pop(ia)
        if a < b:
            pass
        routes[b].insert(pos, x)
        if len(routes[a]) > 1:
            routes[a] = two_opt(routes[a])
        if len(routes[b]) > 1:
            routes[b] = two_opt(routes[b])
        if len(routes[a]) == 0:
            routes.pop(a)
        return True

    for _ in range(20):
        improved = False
        for r in range(len(routes)):
            newr = two_opt(routes[r])
            if route_cost(newr) + 1e-12 < route_cost(routes[r]):
                routes[r] = newr
                improved = True
        if relocate_once():
            improved = True
        if not improved:
            break

    return routes
