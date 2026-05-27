def solve_cvrp(instance):
    def _get(key, default=None):
        if isinstance(instance, dict) and key in instance:
            return instance[key]
        return default

    depot = _get("depot", 0)
    capacity = _get("capacity", _get("vehicle_capacity", _get("Q", 0)))

    coords = _get("coordinates", _get("coords", None))
    dist_matrix = _get("distance_matrix", _get("distances", None))
    demands_raw = _get("demands", _get("demand", {}))

    def _to_id_set(x):
        if x is None:
            return []
        if isinstance(x, dict):
            return list(x.keys())
        if isinstance(x, (list, tuple)):
            return list(x)
        return [x]

    def _node_ids():
        if isinstance(coords, dict):
            ids = list(coords.keys())
        elif isinstance(coords, (list, tuple)):
            ids = list(range(len(coords)))
        elif isinstance(demands_raw, dict):
            ids = list(demands_raw.keys())
        elif isinstance(demands_raw, (list, tuple)):
            ids = list(range(len(demands_raw)))
        else:
            ids = []
            if isinstance(instance, dict):
                for k, v in instance.items():
                    if isinstance(v, dict) and "demand" in v:
                        ids.append(k)
        if depot not in ids:
            ids.append(depot)
        return ids

    ids = _node_ids()

    def _demand(i):
        if isinstance(demands_raw, dict):
            return demands_raw.get(i, 0)
        if isinstance(demands_raw, (list, tuple)) and isinstance(i, int) and 0 <= i < len(demands_raw):
            return demands_raw[i]
        if isinstance(instance, dict) and i in instance and isinstance(instance[i], dict) and "demand" in instance[i]:
            return instance[i]["demand"]
        return 0

    def _coord(i):
        if isinstance(coords, dict):
            return coords.get(i, None)
        if isinstance(coords, (list, tuple)) and isinstance(i, int) and 0 <= i < len(coords):
            return coords[i]
        if isinstance(instance, dict) and i in instance and isinstance(instance[i], dict):
            v = instance[i]
            if "coord" in v:
                return v["coord"]
            if "x" in v and "y" in v:
                return (v["x"], v["y"])
        return None

    def _dist(a, b):
        if a == b:
            return 0
        if dist_matrix is not None:
            try:
                return dist_matrix[a][b]
            except Exception:
                try:
                    return dist_matrix[int(a)][int(b)]
                except Exception:
                    pass
        ca = _coord(a)
        cb = _coord(b)
        if ca is not None and cb is not None:
            dx = ca[0] - cb[0]
            dy = ca[1] - cb[1]
            return (dx * dx + dy * dy) ** 0.5
        return abs((a if isinstance(a, int) else hash(str(a))) - (b if isinstance(b, int) else hash(str(b))))

    customers = [i for i in ids if i != depot]

    # Initial solution: singleton routes
    routes = [[i] for i in customers]
    route_load = [_demand(r[0]) for r in routes]

    # Clarke-Wright savings merge
    savings = []
    for idx_i in range(len(customers)):
        i = customers[idx_i]
        for idx_j in range(idx_i + 1, len(customers)):
            j = customers[idx_j]
            s = _dist(depot, i) + _dist(depot, j) - _dist(i, j)
            savings.append((s, i, j))
    savings.sort(key=lambda x: (-x[0], x[1], x[2]))

    node_to_route = {}
    pos_in_route = {}
    for r_idx, r in enumerate(routes):
        node_to_route[r[0]] = r_idx
        pos_in_route[r[0]] = 0

    active = [True] * len(routes)

    def _route_of(node):
        ridx = node_to_route.get(node, None)
        if ridx is None or ridx < 0 or ridx >= len(routes) or not active[ridx]:
            return None
        return ridx

    def _refresh_route(ridx):
        r = routes[ridx]
        for p, node in enumerate(r):
            node_to_route[node] = ridx
            pos_in_route[node] = p

    for _, i, j in savings:
        ri = _route_of(i)
        rj = _route_of(j)
        if ri is None or rj is None or ri == rj:
            continue
        if not active[ri] or not active[rj]:
            continue
        route_i = routes[ri]
        route_j = routes[rj]
        if not route_i or not route_j:
            continue
        can_merge = False
        merged = None

        if route_i[-1] == i and route_j[0] == j:
            merged = route_i + route_j
            can_merge = True
        elif route_i[0] == i and route_j[-1] == j:
            merged = route_j + route_i
            can_merge = True
        elif route_i[0] == i and route_j[0] == j:
            merged = list(reversed(route_i)) + route_j
            can_merge = True
        elif route_i[-1] == i and route_j[-1] == j:
            merged = route_i + list(reversed(route_j))
            can_merge = True

        if can_merge:
            load = 0
            for node in merged:
                load += _demand(node)
            if capacity == 0 or load <= capacity:
                routes[ri] = merged
                route_load[ri] = load
                active[rj] = False
                routes[rj] = []
                route_load[rj] = 0
                _refresh_route(ri)

    routes = [r for idx, r in enumerate(routes) if active[idx] and r]
    route_load = [_demand(node) for node in [r[0] for r in routes]] if routes else []

    def _route_cost(r):
        if not r:
            return 0
        c = _dist(depot, r[0]) + _dist(r[-1], depot)
        for k in range(len(r) - 1):
            c += _dist(r[k], r[k + 1])
        return c

    def _total_cost(sol):
        s = 0
        for r in sol:
            s += _route_cost(r)
        return s

    # Intra-route 2-opt
    improved = True
    passes = 0
    while improved and passes < 3:
        improved = False
        passes += 1
        for ridx in range(len(routes)):
            r = routes[ridx]
            n = len(r)
            if n < 4:
                continue
            best_delta = 0
            best_i = -1
            best_j = -1
            base = _route_cost(r)
            for i in range(n - 1):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    nr = r[:i + 1] + list(reversed(r[i + 1:j + 1])) + r[j + 1:]
                    new_cost = _route_cost(nr)
                    delta = new_cost - base
                    if delta < best_delta:
                        best_delta = delta
                        best_i, best_j = i, j
            if best_delta < 0:
                routes[ridx] = r[:best_i + 1] + list(reversed(r[best_i + 1:best_j + 1])) + r[best_j + 1:]
                improved = True

    # Inter-route relocate / swap
    changed = True
    rounds = 0
    while changed and rounds < 4:
        changed = False
        rounds += 1

        # Relocate
        for a in range(len(routes)):
            ra = routes[a]
            la = sum(_demand(x) for x in ra)
            for i in range(len(ra)):
                node = ra[i]
                dn = _demand(node)
                for b in range(len(routes)):
                    if a == b:
                        continue
                    rb = routes[b]
                    lb = sum(_demand(x) for x in rb)
                    if capacity and lb + dn > capacity:
                        continue
                    for pos in range(len(rb) + 1):
                        na = ra[:i] + ra[i + 1:]
                        nb = rb[:pos] + [node] + rb[pos:]
                        old = _route_cost(ra) + _route_cost(rb)
                        new = _route_cost(na) + _route_cost(nb)
                        if new < old:
                            routes[a] = na
                            routes[b] = nb
                            changed = True
                            ra = routes[a]
                            rb = routes[b]
                            break
                    if changed:
                        break
                if changed:
                    break
            if changed:
                break

        # Swap
        if not changed:
            for a in range(len(routes)):
                ra = routes[a]
                la = sum(_demand(x) for x in ra)
                for b in range(a + 1, len(routes)):
                    rb = routes[b]
                    lb = sum(_demand(x) for x in rb)
                    for i in range(len(ra)):
                        for j in range(len(rb)):
                            x = ra[i]
                            y = rb[j]
                            nx_load = la - _demand(x) + _demand(y)
                            ny_load = lb - _demand(y) + _demand(x)
                            if capacity and (nx_load > capacity or ny_load > capacity):
                                continue
                            na = ra[:i] + [y] + ra[i + 1:]
                            nb = rb[:j] + [x] + rb[j + 1:]
                            old = _route_cost(ra) + _route_cost(rb)
                            new = _route_cost(na) + _route_cost(nb)
                            if new < old:
                                routes[a] = na
                                routes[b] = nb
                                changed = True
                                break
                        if changed:
                            break
                    if changed:
                        break
                if changed:
                    break

    # Final sanity: ensure every customer exactly once
    seen = {}
    final_routes = []
    for r in routes:
        nr = []
        for node in r:
            if node == depot:
                continue
