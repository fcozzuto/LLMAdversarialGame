def solve_cvrp(instance):
    def get_field(*keys, default=None):
        try:
            for k in keys:
                if k in instance:
                    return instance[k]
        except:
            pass
        return default

    depot = get_field('depot', 'depot_id', default=0)
    capacity = get_field('capacity', 'vehicle_capacity', 'C', default=None)

    demands = get_field('demands', 'demand', default=None)
    coords = get_field('coords', 'coordinates', 'locations', default=None)
    distmat = get_field('distance_matrix', 'distances', 'matrix', default=None)

    customers = []
    if demands is not None:
        try:
            for k in demands:
                if k != depot:
                    customers.append(k)
        except:
            pass
    if not customers and coords is not None:
        try:
            for k in coords:
                if k != depot:
                    customers.append(k)
        except:
            pass
    if not customers and distmat is not None:
        try:
            n = len(distmat)
            for i in range(n):
                if i != depot:
                    customers.append(i)
        except:
            pass
    if not customers:
        try:
            for c in instance.get('customers', []):
                if c != depot:
                    customers.append(c)
        except:
            pass

    seen = {}
    ordered = []
    for c in customers:
        if c not in seen:
            seen[c] = 1
            ordered.append(c)
    customers = ordered

    def demand_of(c):
        if demands is None:
            return 0
        try:
            return demands[c]
        except:
            try:
                return demands[int(c)]
            except:
                return 0

    def coord_of(c):
        if coords is None:
            return (0.0, 0.0)
        try:
            return coords[c]
        except:
            try:
                return coords[int(c)]
            except:
                return (0.0, 0.0)

    def dist(a, b):
        if distmat is not None:
            try:
                return distmat[a][b]
            except:
                try:
                    return distmat[int(a)][int(b)]
                except:
                    pass
        if coords is not None:
            ax, ay = coord_of(a)
            bx, by = coord_of(b)
            dx = ax - bx
            dy = ay - by
            return (dx * dx + dy * dy) ** 0.5
        try:
            return abs(a - b)
        except:
            return 0.0

    total_demand = 0
    for c in customers:
        total_demand += demand_of(c)
    if capacity is None:
        capacity = total_demand if total_demand > 0 else 1

    if not customers:
        return []

    # Initial ordering
    if coords is not None:
        dx0, dy0 = coord_of(depot)
        ang_list = []
        for c in customers:
            x, y = coord_of(c)
            ang = 0.0
            try:
                ang = (y - dy0) / ((x - dx0) * (x - dx0) + (y - dy0) * (y - dy0) + 1e-9)
            except:
                ang = x + y
            ang_list.append((ang, dist(depot, c), c))
        ang_list.sort()
        order = [c for _, _, c in ang_list]
    else:
        order = customers[:]
        order.sort()

    # Construct feasible routes by first-fit in ordered sequence
    routes = []
    loads = []
    cur = []
    cur_load = 0
    for c in order:
        d = demand_of(c)
        if cur and cur_load + d > capacity:
            routes.append(cur)
            loads.append(cur_load)
            cur = [c]
            cur_load = d
        else:
            cur.append(c)
            cur_load += d
    if cur:
        routes.append(cur)
        loads.append(cur_load)

    # Repair: move oversized singletons to own route if needed
    repaired = []
    repaired_loads = []
    for r in routes:
        load = 0
        for c in r:
            load += demand_of(c)
        if load <= capacity:
            repaired.append(r)
            repaired_loads.append(load)
        else:
            for c in r:
                repaired.append([c])
                repaired_loads.append(demand_of(c))
    routes = repaired
    loads = repaired_loads

    # Savings merge on route endpoints
    def route_load(route):
        s = 0
        for c in route:
            s += demand_of(c)
        return s

    def route_cost(route):
        if not route:
            return 0.0
        cst = dist(depot, route[0]) + dist(route[-1], depot)
        for i in range(len(route) - 1):
            cst += dist(route[i], route[i + 1])
        return cst

    def orient(route, rev):
        if rev:
            return route[::-1]
        return route

    # Map customer -> route index
    pos = {}
    for i in range(len(routes)):
        for c in routes[i]:
            pos[c] = i

    savings = []
    for i in range(len(customers)):
        a = customers[i]
        for j in range(i + 1, len(customers)):
            b = customers[j]
            s = dist(depot, a) + dist(depot, b) - dist(a, b)
            savings.append((s, a, b))
    savings.sort(reverse=True)

    changed = True
    while changed:
        changed = False
        for s, a, b in savings:
            ia = pos.get(a, None)
            ib = pos.get(b, None)
            if ia is None or ib is None or ia == ib:
                continue
            ra = routes[ia]
            rb = routes[ib]
            if not ra or not rb:
                continue
            best = None

            cand = [
                (ra + rb, ra[-1] == a and rb[0] == b),
                (ra + rb[::-1], ra[-1] == a and rb[-1] == b),
                (ra[::-1] + rb, ra[0] == a and rb[0] == b),
                (ra[::-1] + rb[::-1], ra[0] == a and rb[-1] == b),
                (rb + ra, rb[-1] == b and ra[0] == a),
                (rb + ra[::-1], rb[-1] == b and ra[-1] == a),
                (rb[::-1] + ra, rb[0] == b and ra[0] == a),
                (rb[::-1] + ra[::-1], rb[0] == b and ra[-1] == a),
            ]
            for nr, ok in cand:
                if not ok:
                    continue
                if route_load(nr) <= capacity:
                    best = nr
                    break
            if best is None:
                continue

            if ia > ib:
                ia, ib = ib, ia
            routes[ia] = best
            loads[ia] = route_load(best)
            del routes[ib]
            del loads[ib]
            pos = {}
            for idx in range(len(routes)):
                for c in routes[idx]:
                    pos[c] = idx
            changed = True
            break

    # Local search: relocate customers to reduce cost while keeping feasibility
    improved = True
    while improved:
        improved = False
        best_move = None
        best_delta = 0.0

        for i in range(len(routes)):
            ri = routes[i]
            if not ri:
                continue
            li = loads[i]
            for p in range(len(ri)):
                c = ri[p]
                dc = demand_of(c)

                prev_c = depot if p == 0 else ri[p - 1]
                next_c = depot if p == len(ri) - 1 else ri[p + 1]
                remove_delta = dist(prev_c, next_c) - dist(prev_c, c) - dist(c, next_c)

                for j in range(len(routes)):
                    if i == j:
                        continue
                    if loads[j] + dc > capacity:
                        continue
                    rj = routes[j]
                    for ins in range(len(rj) + 1):
                        left = depot if ins == 0 else rj[ins - 1]
                        right = depot if ins == len(rj) else rj[ins]
                        add_delta = dist(left, c) + dist(c, right) - dist(left, right)
                        delta = remove_delta + add_delta
                        if delta < best_delta - 1e-12:
                            best_delta = delta
                            best_move = (i, j, p, ins, c)

        if best_move is not None:
            i, j, p, ins, c = best_move
            if i < j:
                ri = routes[i]
                rj = routes[j]
            else:
                ri = routes[i]
                rj = routes[j]
