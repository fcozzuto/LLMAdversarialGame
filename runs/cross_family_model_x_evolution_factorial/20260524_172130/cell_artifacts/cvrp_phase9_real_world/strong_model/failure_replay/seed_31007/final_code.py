def solve_cvrp(instance):
    def _is_dict(x):
        try:
            return x.__class__ is dict
        except:
            return False

    def _is_seq(x):
        try:
            t = x.__class__
            return t is list or t is tuple
        except:
            return False

    def _get(obj, keys, default=None):
        if _is_dict(obj):
            for k in keys:
                try:
                    if k in obj:
                        return obj[k]
                except:
                    pass
        return default

    def _num(x):
        try:
            return x + 0 == x
        except:
            return False

    def _coord(node):
        if _is_dict(node):
            for a, b in (('x', 'y'), ('X', 'Y')):
                try:
                    if a in node and b in node and _num(node[a]) and _num(node[b]):
                        return (float(node[a]), float(node[b]))
                except:
                    pass
            for k in ('coord', 'location', 'coords', 'xy'):
                try:
                    v = node[k]
                    if _is_seq(v) and len(v) >= 2 and _num(v[0]) and _num(v[1]):
                        return (float(v[0]), float(v[1]))
                except:
                    pass
        elif _is_seq(node):
            try:
                if len(node) >= 2 and _num(node[0]) and _num(node[1]):
                    return (float(node[0]), float(node[1]))
            except:
                pass
        return None

    def _demand(node):
        if _is_dict(node):
            for k in ('demand', 'd', 'q', 'load'):
                try:
                    if k in node and _num(node[k]):
                        return float(node[k])
                except:
                    pass
        elif _is_seq(node):
            try:
                if len(node) >= 3 and _num(node[2]):
                    return float(node[2])
            except:
                pass
        return 0.0

    def _dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    coords = {}
    demands = {}
    depot_id = _get(instance, ['depot', 'depot_id', 'depot_index'], 0)
    capacity = _get(instance, ['capacity', 'vehicle_capacity', 'Q'], None)

    depot_coord = None
    if _is_dict(instance):
        try:
            if depot_id in instance:
                depot_coord = _coord(instance[depot_id])
        except:
            pass
        if depot_coord is None:
            depot_coord = _coord(_get(instance, ['depot']))
        if depot_coord is None:
            depot_coord = _coord(_get(instance, ['depot_coord', 'depot_location']))
    if depot_coord is None:
        depot_coord = (0.0, 0.0)

    nodes = _get(instance, ['customers', 'nodes', 'points', 'customer_data', 'locations'], None)
    if nodes is None and _is_dict(instance):
        nodes = instance

    customer_ids = []

    if _is_dict(nodes):
        for k in nodes:
            try:
                if k == depot_id:
                    continue
            except:
                pass
            c = _coord(nodes[k])
            if c is not None:
                coords[k] = c
                demands[k] = _demand(nodes[k])
                customer_ids.append(k)
    elif _is_seq(nodes):
        for i in range(len(nodes)):
            if i == depot_id:
                continue
            c = _coord(nodes[i])
            if c is not None:
                coords[i] = c
                demands[i] = _demand(nodes[i])
                customer_ids.append(i)

    if not customer_ids:
        # Fallback: scan top-level dict for node-like entries
        if _is_dict(instance):
            for k in instance:
                if k == depot_id:
                    continue
                v = instance[k]
                c = _coord(v)
                if c is not None:
                    coords[k] = c
                    demands[k] = _demand(v)
                    customer_ids.append(k)

    if capacity is None:
        s = 0.0
        for cid in customer_ids:
            s += demands.get(cid, 0.0)
        capacity = s if s > 0 else 1.0

    # ensure all demands exist
    for cid in customer_ids:
        if cid not in demands:
            demands[cid] = 0.0

    # deterministic initial construction: nearest-neighbor with capacity fill
    unassigned = {}
    for cid in customer_ids:
        unassigned[cid] = 1

    routes = []

    def _route_load(route):
        s = 0.0
        for cid in route:
            s += demands.get(cid, 0.0)
        return s

    def _best_start():
        best = None
        best_key = None
        for cid in customer_ids:
            if cid not in unassigned:
                continue
            c = coords[cid]
            d = _dist(depot_coord, c)
            key = (-d, -demands.get(cid, 0.0), cid)
            if best is None or key < best_key:
                best = cid
                best_key = key
        return best

    while unassigned:
        start = _best_start()
        if start is None:
            break
        route = [start]
        del unassigned[start]
        load = demands.get(start, 0.0)
        last = start
        while True:
            best = None
            best_key = None
            last_c = coords[last]
            for cid in unassigned:
                q = demands.get(cid, 0.0)
                if load + q > capacity + 1e-9:
                    continue
                d1 = _dist(last_c, coords[cid])
                d0 = _dist(depot_coord, coords[cid])
                key = (d1, d0, q, cid)
                if best is None or key < best_key:
                    best = cid
                    best_key = key
            if best is None:
                break
            route.append(best)
            del unassigned[best]
            load += demands.get(best, 0.0)
            last = best
        routes.append(route)

    # repair: if any route empty or missing due to parsing issues, append remaining as singletons
    if unassigned:
        leftovers = []
        for cid in unassigned:
            leftovers.append(cid)
        leftovers.sort()
        for cid in leftovers:
            routes.append([cid])

    # local search: intra-route 2-opt and inter-route relocate, deterministic
    def _route_distance(route):
        if not route:
            return 0.0
        total = _dist(depot_coord, coords[route[0]])
        for i in range(len(route) - 1):
            total += _dist(coords[route[i]], coords[route[i + 1]])
        total += _dist(coords[route[-1]], depot_coord)
        return total

    improved = True
    while improved:
        improved = False

        # 2-opt within routes
        for r in range(len(routes)):
            route = routes[r]
            n = len(route)
            if n < 4:
                continue
            best_gain = 0.0
            best_i = -1
            best_j = -1
            base = _route_distance(route)
            for i in range(n - 2):
                for j in range(i + 2, n):
                    cand = route[:i + 1] + route[i + 1:j + 1][::-1] + route[j + 1:]
                    newd = _route_distance(cand)
                    gain = base - newd
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best_i = i
                        best_j = j
            if best_gain > 1e-12:
                routes[r] = route[:best_i + 1] + route[best_i + 1:best_j + 1][::-1] + route[best_j + 1:]
                improved = True

        # relocate between routes
        for a in range(len(routes)):
            for i in range(len(routes[a])):
                cid = routes[a][i]
                dem = demands.get(cid, 0.0)
                for b in range(len(routes)):
                    if a == b:
                        continue
                    if _route_load(routes[b]) + dem > capacity + 1e-9:
                        continue
                    ra = routes[a]
                    rb = routes[b]
                    base_a = _route_distance(ra)
                    base_b = _route_distance(rb)

                    # remove cid from a
                    tmp_a = ra[:i] + ra[i + 1:]
                    if len(tmp_a) == 0:
                        continue

                    # try all insertion positions in b
                    best_move_gain = 0.0
                    best_pos = -1
                    for p in range(len(rb) + 1):
                        tmp_b = rb[:p] + [cid] + rb[p:]
                        newd = _route_distance(tmp_a) + _route_distance(tmp_b)
                        gain = (base_a + base_b) - newd
                        if gain > best_move_gain + 1e-12:
                            best_move_gain = gain
                            best_pos = p
                    if best_pos >= 0 and best_move_gain > 1e-12:
                        routes[a] = tmp_a
                        routes[b] = rb[:best_pos] + [cid] + rb[best_pos:]
                        improved = True
                        break
                if improved:
                    break
