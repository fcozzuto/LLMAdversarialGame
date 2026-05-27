def solve_cvrp(instance):
    def get_item(obj, keys, default=None):
        try:
            for k in keys:
                try:
                    if k in obj:
                        return obj[k]
                except:
                    pass
        except:
            pass
        return default

    def to_dict_from_list(lst):
        d = {}
        i = 0
        for v in lst:
            d[i] = v
            i += 1
        return d

    def parse_instance(inst):
        depot_id = get_item(inst, ["depot_id", "depot", "DEPOT"], 0)
        cap = get_item(inst, ["capacity", "vehicle_capacity", "CAPACITY", "Q"], 0)
        demands = get_item(inst, ["demands", "demand", "DEMANDS"], None)
        coords = get_item(inst, ["coords", "coordinates", "locations", "nodes", "node_coords"], None)
        dist = get_item(inst, ["distance_matrix", "distances", "matrix", "cost_matrix"], None)
        customers = get_item(inst, ["customers", "customer_ids", "ids"], None)

        try:
            if demands and not hasattr(demands, "get"):
                demands = to_dict_from_list(demands)
        except:
            pass
        try:
            if coords and not hasattr(coords, "get"):
                coords = to_dict_from_list(coords)
        except:
            pass

        if customers is None:
            if demands and hasattr(demands, "get"):
                customers = [k for k in demands.keys() if k != depot_id]
            elif coords and hasattr(coords, "get"):
                customers = [k for k in coords.keys() if k != depot_id]
            elif dist is not None:
                try:
                    customers = list(range(1, len(dist)))
                except:
                    customers = []
            else:
                customers = []
        else:
            customers = list(customers)
            customers = [c for c in customers if c != depot_id]

        return depot_id, cap, demands, coords, dist, customers

    depot_id, capacity, demands, coords, dist, customers = parse_instance(instance)

    def demand_of(c):
        try:
            return demands.get(c, 0)
        except:
            return 0

    def coord_of(c):
        try:
            return coords.get(c, None)
        except:
            return None

    def dist_of(a, b):
        try:
            if dist is not None:
                return dist[a][b]
        except:
            pass
        ca = coord_of(a)
        cb = coord_of(b)
        try:
            if ca is not None and cb is not None:
                dx = ca[0] - cb[0]
                dy = ca[1] - cb[1]
                return dx * dx + dy * dy
        except:
            pass
        try:
            return abs(a - b)
        except:
            return 0

    total_demand = 0
    for c in customers:
        total_demand += demand_of(c)
    if capacity <= 0:
        capacity = total_demand if total_demand > 0 else 1

    # Order customers deterministically: angular sweep when possible, else by id
    ordered = []
    dep = coord_of(depot_id)
    if dep is not None:
        cx = dep[0]
        cy = dep[1]
        items = []
        for c in customers:
            p = coord_of(c)
            if p is None:
                items.append((10**18, dist_of(depot_id, c), c))
            else:
                dx = p[0] - cx
                dy = p[1] - cy
                quad = 0
                if dy < 0 or (dy == 0 and dx < 0):
                    quad = 1
                ang_num = dy
                ang_den = abs(dx) + abs(dy) + 1e-9
                items.append((quad, ang_num / ang_den, dist_of(depot_id, c), c))
        items.sort()
        ordered = [x[-1] for x in items]
    else:
        ordered = sorted(customers)

    # Construct initial routes by sweep/greedy fill
    routes = []
    cur = []
    load = 0
    for c in ordered:
        d = demand_of(c)
        if d > capacity:
            # singleton anyway; later repair cannot fix infeasible demand, but keep deterministic
            if cur:
                routes.append(cur)
                cur = []
                load = 0
            routes.append([c])
            continue
        if load + d > capacity and cur:
            routes.append(cur)
            cur = [c]
            load = d
        else:
            cur.append(c)
            load += d
    if cur:
        routes.append(cur)

    def route_load(route):
        s = 0
        for c in route:
            s += demand_of(c)
        return s

    def route_cost(route):
        if not route:
            return 0
        c = dist_of(depot_id, route[0])
        i = 0
        while i + 1 < len(route):
            c += dist_of(route[i], route[i + 1])
            i += 1
        c += dist_of(route[-1], depot_id)
        return c

    def best_orientation(route):
        if len(route) <= 1:
            return route[:]
        r1 = route[:]
        r2 = list(reversed(route))
        return r2 if route_cost(r2) < route_cost(r1) else r1

    # Local search: relocate and 2-opt within routes
    improved = True
    iters = 0
    while improved and iters < 4:
        improved = False
        iters += 1

        # normalize orientations
        i = 0
        while i < len(routes):
            routes[i] = best_orientation(routes[i])
            i += 1

        # intra-route 2-opt
        i = 0
        while i < len(routes):
            r = routes[i]
            n = len(r)
            if n >= 4:
                best_r = r
                best_c = route_cost(r)
                a = 0
                while a + 2 < n:
                    b = a + 2
                    while b < n:
                        cand = r[:a + 1] + list(reversed(r[a + 1:b + 1])) + r[b + 1:]
                        cc = route_cost(cand)
                        if cc < best_c:
                            best_c = cc
                            best_r = cand
                            improved = True
                        b += 1
                    a += 1
                routes[i] = best_r
            i += 1

        # inter-route relocate
        moved = True
        inner = 0
        while moved and inner < 2:
            moved = False
            inner += 1
            i = 0
            while i < len(routes):
                if not routes[i]:
                    i += 1
                    continue
                j = 0
                while j < len(routes):
                    if i == j:
                        j += 1
                        continue
                    ri = routes[i]
                    rj = routes[j]
                    li = route_load(ri)
                    lj = route_load(rj)
                    best_delta = 0
                    best_move = None
                    ai = 0
                    while ai < len(ri):
                        c = ri[ai]
                        dc = demand_of(c)
                        if lj + dc <= capacity:
                            # remove c from ri
                            new_ri = ri[:ai] + ri[ai + 1:]
                            base_i = route_cost(ri)
                            base_j = route_cost(rj)
                            if len(new_ri) == 0:
                                cost_i = 0
                            else:
                                cost_i = route_cost(new_ri)
                            p = 0
                            while p <= len(rj):
                                new_rj = rj[:p] + [c] + rj[p:]
                                cost_j = route_cost(new_rj)
                                delta = (cost_i + cost_j) - (base_i + base_j)
                                if delta < best_delta:
                                    best_delta = delta
                                    best_move = (i, j, ai, p, new_ri, new_rj)
                                p += 1
                        ai += 1
                    if best_move is not None:
                        _, _, _, _, new_ri, new_rj = best_move
                        routes[i] = new_ri
                        routes[j] = new_rj
                        if not routes[i]:
                            routes.pop(i)
                            if j > i:
                                j -= 1
                        improved = True
                        moved = True
                        break
                    j += 1
                if moved:
                    break
                i += 1

    # Cleanup empty routes and final orientation
    final_routes = []
    for r in routes:
        if r:
            final_routes.append(best_orientation(r))
    # Ensure every customer appears once; repair if needed
    seen = {}
    for r in final_routes:
        for c in r:
            seen[c] = seen.get(c, 0) + 1

    missing = [c for c in customers if c not in seen]
