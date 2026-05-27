def solve_cvrp(instance):
    def getv(obj, keys, default=None):
        for k in keys:
            try:
                return obj[k]
            except:
                pass
        return default

    depot = getv(instance, ["depot", "depot_id", "start", "origin"], 0)
    capacity = getv(instance, ["capacity", "vehicle_capacity", "Q"], None)
    coords = getv(instance, ["coords", "coordinates", "points", "locations"], None)
    dist_matrix = getv(instance, ["distance_matrix", "distances", "matrix"], None)
    demands = getv(instance, ["demands", "demand"], None)

    customers = []
    try:
        if "customers" in instance:
            customers = list(instance["customers"])
        elif "nodes" in instance:
            customers = list(instance["nodes"])
        elif coords is not None:
            customers = list(range(len(coords)))
        elif dist_matrix is not None:
            customers = list(range(len(dist_matrix)))
        elif demands is not None:
            customers = list(range(len(demands)))
    except:
        customers = []

    if depot in customers:
        customers = [c for c in customers if c != depot]

    def demand_of(i):
        if demands is None:
            return 0
        try:
            return demands[i]
        except:
            try:
                return demands.get(i, 0)
            except:
                return 0

    def dist(i, j):
        if dist_matrix is not None:
            try:
                return dist_matrix[i][j]
            except:
                return 0
        if coords is not None:
            try:
                xi, yi = coords[i][0], coords[i][1]
                xj, yj = coords[j][0], coords[j][1]
                dx = xi - xj
                dy = yi - yj
                return (dx * dx + dy * dy) ** 0.5
            except:
                return 0
        return 0

    if capacity is None:
        total = 0
        for c in customers:
            total += demand_of(c)
        capacity = total if total > 0 else 1

    if not customers:
        return []

    # deterministic ordering
    if coords is not None:
        try:
            ox, oy = coords[depot][0], coords[depot][1]
            ordered = []
            for c in customers:
                x, y = coords[c][0], coords[c][1]
                dx = x - ox
                dy = y - oy
                ang = 0 if dx == 0 and dy == 0 else dy / (abs(dx) + abs(dy) + 1e-12)
                ordered.append((ang, dx * dx + dy * dy, -demand_of(c), c))
            ordered.sort()
            ordered = [t[3] for t in ordered]
        except:
            ordered = sorted(customers, key=lambda c: (-demand_of(c), c))
    else:
        ordered = sorted(customers, key=lambda c: (-demand_of(c), c))

    unvisited = {}
    for c in customers:
        unvisited[c] = 1

    routes = []

    # Construct routes by farthest-seed + nearest-feasible insertion
    while unvisited:
        seed = None
        best_key = None
        for c in ordered:
            if c in unvisited:
                key = (-dist(depot, c), -demand_of(c), c)
                if best_key is None or key < best_key:
                    best_key = key
                    seed = c
        if seed is None:
            break

        route = [seed]
        load = demand_of(seed)
        del unvisited[seed]
        current = seed

        while True:
            best = None
            best_key = None
            for c in ordered:
                if c not in unvisited:
                    continue
                dc = demand_of(c)
                if load + dc > capacity:
                    continue
                key = (dist(current, c), dist(depot, c), -dc, c)
                if best_key is None or key < best_key:
                    best_key = key
                    best = c
            if best is None:
                break
            route.append(best)
            load += demand_of(best)
            current = best
            del unvisited[best]

        routes.append(route)

    # Repair: ensure every customer exactly once
    seen = {}
    cleaned = []
    for r in routes:
        nr = []
        load = 0
        for c in r:
            if seen.get(c, 0) == 0:
                dc = demand_of(c)
                if load + dc <= capacity:
                    nr.append(c)
                    load += dc
                    seen[c] = 1
        if nr:
            cleaned.append(nr)

    missing = [c for c in customers if seen.get(c, 0) == 0]
    for c in missing:
        dc = demand_of(c)
        if dc <= capacity:
            cleaned.append([c])
            seen[c] = 1
        else:
            # Split impossible single demand by still returning a singleton to preserve coverage
            cleaned.append([c])
            seen[c] = 1

    # Final duplicate removal while preserving order
    assigned = {}
    final_routes = []
    for r in cleaned:
        nr = []
        load = 0
        for c in r:
            if c not in assigned:
                dc = demand_of(c)
                if load + dc <= capacity:
                    nr.append(c)
                    load += dc
                    assigned[c] = 1
        if nr:
            final_routes.append(nr)

    # Any customers still missing
    for c in customers:
        if c not in assigned:
            final_routes.append([c])
            assigned[c] = 1

    return final_routes
