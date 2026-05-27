def solve_cvrp(instance):
    # --- parsing ---
    def get_capacity(inst):
        for k in ("capacity", "vehicle_capacity", "veh_capacity", "truck_capacity"):
            if k in inst:
                return inst[k]
        return None

    def is_number(x):
        return isinstance(x, (int, float))

    def node_id(node):
        for k in ("id", "node_id", "customer_id", "idx"):
            if isinstance(node, dict) and k in node:
                return node[k]
        return node

    def node_demand(node):
        if isinstance(node, dict):
            for k in ("demand", "quantity", "d"):
                if k in node:
                    return node[k]
        return 0

    def node_xy(node):
        if isinstance(node, dict):
            if "x" in node and "y" in node:
                return node["x"], node["y"]
            if "coord" in node and isinstance(node["coord"], (list, tuple)) and len(node["coord"]) >= 2:
                return node["coord"][0], node["coord"][1]
        return None

    depot = None
    customers = []

    if "depot" in instance:
        depot = instance["depot"]
    elif "nodes" in instance and instance["nodes"]:
        depot = instance["nodes"][0]
    elif "customers" in instance and isinstance(instance["customers"], list) and instance["customers"]:
        depot = {"id": 0, "x": 0, "y": 0, "demand": 0}

    if "customers" in instance and isinstance(instance["customers"], list):
        customers = instance["customers"]
    elif "nodes" in instance and isinstance(instance["nodes"], list):
        customers = [n for n in instance["nodes"] if node_id(n) != node_id(depot)]
    elif "demands" in instance and "coords" in instance:
        customers = []
        for i in range(len(instance["demands"])):
            customers.append({"id": i + 1, "demand": instance["demands"][i], "x": instance["coords"][i + 1][0], "y": instance["coords"][i + 1][1]})
    else:
        customers = []

    cap = get_capacity(instance)
    if cap is None:
        cap = 0

    dep_id = node_id(depot) if depot is not None else 0
    dep_xy = node_xy(depot) if depot is not None else (0, 0)

    cust = []
    demand = {}
    coord = {}
    for n in customers:
        cid = node_id(n)
        if cid == dep_id:
            continue
        cust.append(cid)
        demand[cid] = node_demand(n)
        xy = node_xy(n)
        coord[cid] = xy

    # handle alternative instance formats
    if not cust and "demands" in instance:
        ids = list(range(1, len(instance["demands"])))
        for i in ids:
            cid = i
            cust.append(cid)
            demand[cid] = instance["demands"][i]
            if "coords" in instance and i < len(instance["coords"]):
                coord[cid] = instance["coords"][i]

    # distance helper
    dist_cache = {}

    def dist(a, b):
        key = (a, b)
        if key in dist_cache:
            return dist_cache[key]
        if a == dep_id:
            ax, ay = dep_xy
        else:
            ax, ay = coord.get(a, (0, 0))
        if b == dep_id:
            bx, by = dep_xy
        else:
            bx, by = coord.get(b, (0, 0))
        dx = ax - bx
        dy = ay - by
        d = (dx * dx + dy * dy) ** 0.5
        dist_cache[key] = d
        dist_cache[(b, a)] = d
        return d

    # if no coordinates, use a stable pseudo-distance from ids
    have_coords = True
    if dep_xy is None:
        have_coords = False
    for c in cust:
        if coord.get(c) is None:
            have_coords = False
            break

    if not have_coords:
        def dist(a, b):
            if a == dep_id:
                ai = 0
            else:
                ai = int(a)
            if b == dep_id:
                bi = 0
            else:
                bi = int(b)
            return abs(ai - bi) + 1e-6 * (ai + bi)

    # --- constructive: greedy nearest feasible with route restart ---
    unserved = {}
    for c in cust:
        unserved[c] = True

    # deterministic starting order: high demand first, then proximity to depot
    order = list(cust)
    order.sort(key=lambda c: (-demand.get(c, 0), dist(dep_id, c), c))

    routes = []

    while unserved:
        # pick a seed customer
        seed = None
        for c in order:
            if c in unserved and demand.get(c, 0) <= cap:
                seed = c
                break
        if seed is None:
            # infeasible instance under capacity; place remaining singleton routes
            for c in order:
                if c in unserved:
                    routes.append([c])
                    del unserved[c]
            break

        route = [seed]
        load = demand.get(seed, 0)
        del unserved[seed]
        last = seed

        while True:
            best = None
            best_key = None
            for c in order:
                if c not in unserved:
                    continue
                d = demand.get(c, 0)
                if load + d > cap:
                    continue
                k = (dist(last, c), -d, c)
                if best is None or k < best_key:
                    best = c
                    best_key = k
            if best is None:
                break
            route.append(best)
            load += demand.get(best, 0)
            del unserved[best]
            last = best

        routes.append(route)

    # --- repair: ensure no empty routes, merge trivial slack if possible ---
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(routes):
            if not routes[i]:
                del routes[i]
                changed = True
                continue
            i += 1

    def route_load(r):
        s = 0
        for c in r:
            s += demand.get(c, 0)
        return s

    def route_cost(r):
        if not r:
            return 0
        s = dist(dep_id, r[0])
        for i in range(len(r) - 1):
            s += dist(r[i], r[i + 1])
        s += dist(r[-1], dep_id)
        return s

    def insert_cost(r, pos, c):
        prev = dep_id if pos == 0 else r[pos - 1]
        nxt = dep_id if pos == len(r) else r[pos]
        return dist(prev, c) + dist(c, nxt) - dist(prev, nxt)

    # --- local search: intra-route 2-opt and inter-route relocate/swap ---
    improved = True
    passes = 0
    while improved and passes < 20:
        improved = False
        passes += 1

        # intra-route reversal (2-opt)
        for ri in range(len(routes)):
            r = routes[ri]
            n = len(r)
            if n < 4:
                continue
            best_delta = 0
            best_i = -1
            best_j = -1
            base = route_cost(r)
            for i in range(n - 2):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    nr = r[:i + 1] + r[i + 1:j + 1][::-1] + r[j + 1:]
                    delta = route_cost(nr) - base
                    if delta < best_delta - 1e-12:
                        best_delta = delta
                        best_i = i
                        best_j = j
            if best_i >= 0:
                routes[ri] = r[:best_i + 1] + r[best_i + 1:best_j + 1][::-1] + r[best_j + 1:]
                improved = True

        # inter-route relocate
        outer = True
        while outer:
            outer = False
            best_move = None
            best_delta = 0
            for a in range(len(routes)):
                ra = routes[a]
                la = route_load(ra)
                for i in range(len(ra)):
                    c = ra[i]
                    dc = demand.get(c, 0)
                    for b in range(len(routes)):
                        if a == b:
                            continue
                        rb = routes[b]
                        lb = route_load(rb)
                        if lb + dc > cap:
                            continue
                        rem_delta = insert_cost(ra, i, c)  # misuse variable; compute removal separately
                        # removal delta in ra if c removed
                        prev = dep_id if i == 0 else ra[i - 1]
                        nxt = dep_id if i == len(ra) - 1 else ra[i + 1]
                        remove_delta = dist(prev, nxt) - dist(prev, c) - dist(c, nxt)
                        base_change = remove_delta
                        for pos in range(len(rb) + 1):
                            add_delta = insert_cost(rb, pos, c)
                            delta = base_change + add_delta
                            if delta < best_delta - 1e-12:
                                best_delta = delta
                                best_move = (a, b, i, pos, c)
            if best_move is not None:
                a, b, i, pos, c = best_move
                ra = routes[a]
                rb = routes[b]
                del ra[i]
                if a == b and pos > i:
                    pos -= 1
                rb.insert(pos, c)
                if not ra:
                    del routes[a]
                improved = True
                outer = True
                break

        # inter-route swap
        best_swap = None
        best_delta = 0
