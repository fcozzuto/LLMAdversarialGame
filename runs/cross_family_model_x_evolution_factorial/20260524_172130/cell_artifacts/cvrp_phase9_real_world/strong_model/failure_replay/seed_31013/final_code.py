def solve_cvrp(instance):
    def is_seq(x):
        try:
            len(x)
            x[0] if len(x) > 0 else None
            return True
        except:
            return False

    def get_inst(keys):
        try:
            for k in keys:
                try:
                    if k in instance:
                        return instance[k]
                except:
                    pass
        except:
            pass
        return None

    depot_id = 0
    try:
        depot_id = instance.get("depot", instance.get("depot_id", 0))
    except:
        depot_id = 0

    nodes = get_inst(("nodes", "customers", "points", "locations"))
    demands_in = get_inst(("demands", "demand"))
    capacity = get_inst(("capacity", "vehicle_capacity", "cap"))
    dist_matrix = get_inst(("distance_matrix", "distances", "cost_matrix", "matrix"))
    coords = get_inst(("coords", "coordinates", "xy"))

    customer_ids = []
    demand = {}
    coord = {}

    def add_node(nid, nd):
        if nid == depot_id:
            return
        customer_ids.append(nid)
        try:
            demand[nid] = nd.get("demand", 0)
        except:
            demand[nid] = 0
        try:
            if "coord" in nd:
                coord[nid] = nd["coord"]
            elif "coords" in nd:
                coord[nid] = nd["coords"]
            elif "x" in nd and "y" in nd:
                coord[nid] = (nd["x"], nd["y"])
        except:
            pass

    try:
        if hasattr(nodes, "items"):
            for nid, nd in nodes.items():
                add_node(nid, nd)
        elif is_seq(nodes):
            for i in range(len(nodes)):
                if i == depot_id:
                    continue
                nd = nodes[i]
                customer_ids.append(i)
                try:
                    demand[i] = nd.get("demand", 0)
                except:
                    demand[i] = 0
                try:
                    if "coord" in nd:
                        coord[i] = nd["coord"]
                    elif "coords" in nd:
                        coord[i] = nd["coords"]
                    elif "x" in nd and "y" in nd:
                        coord[i] = (nd["x"], nd["y"])
                except:
                    pass
        else:
            n = 0
            if is_seq(demands_in):
                n = len(demands_in)
            elif is_seq(coords):
                n = len(coords)
            elif is_seq(dist_matrix):
                n = len(dist_matrix)
            customer_ids = [i for i in range(n) if i != depot_id]
            for i in customer_ids:
                try:
                    demand[i] = demands_in[i] if is_seq(demands_in) and i < len(demands_in) else 0
                except:
                    demand[i] = 0
                try:
                    if is_seq(coords) and i < len(coords):
                        coord[i] = coords[i]
                except:
                    pass
    except:
        customer_ids = []

    try:
        if hasattr(demands_in, "items"):
            for i in customer_ids:
                if i in demands_in:
                    demand[i] = demands_in[i]
        elif is_seq(demands_in):
            for i in customer_ids:
                if i < len(demands_in):
                    demand[i] = demands_in[i]
    except:
        pass

    customer_ids = sorted([i for i in customer_ids if i != depot_id])

    if capacity is None:
        total = 0
        for i in customer_ids:
            total += demand.get(i, 0)
        capacity = total if total > 0 else 1

    def euclid(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    def dist(i, j):
        if i == j:
            return 0.0
        if dist_matrix is not None:
            try:
                return dist_matrix[i][j]
            except:
                try:
                    return dist_matrix[int(i)][int(j)]
                except:
                    pass
        try:
            if i in coord and j in coord:
                return euclid(coord[i], coord[j])
        except:
            pass
        try:
            if is_seq(coords):
                return euclid(coords[i], coords[j])
        except:
            pass
        return 1.0

    def route_demand(route):
        s = 0
        for c in route:
            s += demand.get(c, 0)
        return s

    def route_cost(route):
        if not route:
            return 0.0
        c = dist(depot_id, route[0])
        for a, b in zip(route, route[1:]):
            c += dist(a, b)
        c += dist(route[-1], depot_id)
        return c

    def insertion_delta(route, pos, cust):
        if not route:
            return 2.0 * dist(depot_id, cust)
        if pos == 0:
            return dist(depot_id, cust) + dist(cust, route[0]) - dist(depot_id, route[0])
        if pos == len(route):
            return dist(route[-1], cust) + dist(cust, depot_id) - dist(route[-1], depot_id)
        a = route[pos - 1]
        b = route[pos]
        return dist(a, cust) + dist(cust, b) - dist(a, b)

    def best_insertion(route, cust):
        best_pos = 0
        best_delta = None
        for pos in range(len(route) + 1):
            d = insertion_delta(route, pos, cust)
            if best_delta is None or d < best_delta or (d == best_delta and pos < best_pos):
                best_delta = d
                best_pos = pos
        return best_pos, best_delta

    unserved = set(customer_ids)
    routes = []

    # Constructive: farthest-first seeds + cheapest append
    while unserved:
        seed = None
        best_key = None
        for c in unserved:
            key = (dist(depot_id, c), demand.get(c, 0), -c)
            if best_key is None or key > best_key:
                best_key = key
                seed = c

        route = [seed]
        load = demand.get(seed, 0)
        unserved.remove(seed)

        while True:
            best_c = None
            best_pos = None
            best_delta = None
            for c in unserved:
                d = demand.get(c, 0)
                if load + d > capacity:
                    continue
                pos, delta = best_insertion(route, c)
                score = (delta, d, c)
                if best_delta is None or score < best_delta:
                    best_delta = score
                    best_c = c
                    best_pos = pos
            if best_c is None:
                break
            route.insert(best_pos, best_c)
            load += demand.get(best_c, 0)
            unserved.remove(best_c)

        routes.append(route)

    # Repair: relocate any over-capacity routes greedily (should rarely happen)
    changed = True
    while changed:
        changed = False
        for ri in range(len(routes)):
            while route_demand(routes[ri]) > capacity and routes[ri]:
                # remove least painful customer
                r = routes[ri]
                worst_i = 0
                worst_gain = None
                for i, c in enumerate(r):
                    before = dist(depot_id, r[0]) + dist(r[-1], depot_id) if len(r) == 1 else 0.0
                    if len(r) == 1:
                        gain = 0.0
                    elif i == 0:
                        gain = dist(depot_id, r[0]) + dist(r[0], r[1]) - dist(depot_id, r[1])
                    elif i == len(r) - 1:
                        gain = dist(r[-2], r[-1]) + dist(r[-1], depot_id) - dist(r[-2], depot_id)
                    else:
                        gain = dist(r[i - 1], r[i]) + dist(r[i], r[i + 1]) - dist(r[i - 1], r[i + 1])
                    if worst_gain is None or gain > worst_gain or (gain == worst_gain and c < r[worst_i]):
                        worst_gain = gain
                        worst_i = i
                cust = routes[ri].pop(worst_i)
                placed = False
                best_choice = None
                for rj in range(len(routes)):
                    if rj == ri:
                        continue
                    if route_demand(routes[rj]) + demand.get(cust, 0) <= capacity:
                        pos, delta = best_insertion(routes[rj], cust)
                        choice = (delta, len(routes[rj]), rj, pos)
                        if best_choice is None or choice < best_choice:
                            best_choice = choice
                if best_choice is not None:
                    _, _, rj, pos = best_choice
                    routes[rj].insert(pos, cust)
                    placed = True
                if not placed:
                    routes.append([cust])
                changed = True

    # Local search: intra-route 2-opt and inter-route relocate
    for _ in range(2):
        improved = True
        while improved:
            improved = False

            # 2-opt within routes
            for r in routes:
                n = len(r)
                if n < 4:
                    continue
                best_gain = 0.0
                best_move = None
                base = route_cost(r)
                for i in range(n - 1):
                    for j in range(i + 2, n):
                        cand = r[:i + 1] + r[i + 1:j + 1][::-1] + r[j + 1:]
                        gain = base - route_cost(cand)
