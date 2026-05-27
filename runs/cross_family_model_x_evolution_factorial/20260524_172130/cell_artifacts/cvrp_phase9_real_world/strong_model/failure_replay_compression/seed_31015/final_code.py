def solve_cvrp(instance):
    def get_capacity(inst):
        for k in ("capacity", "vehicle_capacity", "Q", "cap"):
            if isinstance(inst, dict) and k in inst:
                return inst[k]
        return None

    def get_depot(inst):
        if isinstance(inst, dict):
            for k in ("depot", "depot_id", "start"):
                if k in inst:
                    return inst[k]
        return 0

    def get_coords(inst):
        if isinstance(inst, dict):
            for k in ("coords", "coordinates", "locations", "points", "xy"):
                if k in inst:
                    return inst[k]
        return None

    def get_demands(inst):
        if isinstance(inst, dict):
            for k in ("demands", "demand", "loads"):
                if k in inst:
                    return inst[k]
        return None

    def all_customer_ids(inst, depot):
        ids = []
        if isinstance(inst, dict):
            if "customers" in inst and isinstance(inst["customers"], (list, tuple)):
                ids = list(inst["customers"])
            elif "nodes" in inst and isinstance(inst["nodes"], (list, tuple)):
                ids = list(inst["nodes"])
            else:
                coords = get_coords(inst)
                demands = get_demands(inst)
                if isinstance(coords, dict):
                    ids = list(coords.keys())
                elif isinstance(coords, (list, tuple)):
                    ids = list(range(len(coords)))
                elif isinstance(demands, dict):
                    ids = list(demands.keys())
                elif isinstance(demands, (list, tuple)):
                    ids = list(range(len(demands)))
        if not ids:
            ids = []
        return [i for i in ids if i != depot]

    def demand_of(node, demands):
        if demands is None:
            return 1
        if isinstance(demands, dict):
            return demands.get(node, 1)
        try:
            return demands[node]
        except Exception:
            return 1

    def coord_of(node, coords):
        if coords is None:
            return None
        if isinstance(coords, dict):
            return coords.get(node, None)
        try:
            return coords[node]
        except Exception:
            return None

    def dist(a, b, coords):
        pa = coord_of(a, coords)
        pb = coord_of(b, coords)
        if pa is None or pb is None:
            return 0
        ax, ay = pa[0], pa[1]
        bx, by = pb[0], pb[1]
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    depot = get_depot(instance)
    capacity = get_capacity(instance)
    coords = get_coords(instance)
    demands = get_demands(instance)
    customers = all_customer_ids(instance, depot)

    if capacity is None:
        total = 0
        for c in customers:
            total += demand_of(c, demands)
        capacity = max(1, total)

    unserved = set(customers)
    routes = []

    # Deterministic construction: repeated nearest-feasible neighbor from depot.
    while unserved:
        route = []
        load = 0
        current = depot
        first_pick = None
        best_key = None

        # choose a starting customer: nearest to depot, then lower demand, then id
        for c in unserved:
            d = demand_of(c, demands)
            if d <= capacity and load + d <= capacity:
                key = (dist(depot, c, coords), d, c)
                if best_key is None or key < best_key:
                    best_key = key
                    first_pick = c
        if first_pick is None:
            # fallback: smallest demand customer, even if demand exceeds capacity
            first_pick = min(unserved, key=lambda c: (demand_of(c, demands), dist(depot, c, coords), c))

        route.append(first_pick)
        load += demand_of(first_pick, demands)
        unserved.remove(first_pick)
        current = first_pick

        while True:
            best = None
            best_key = None
            for c in unserved:
                d = demand_of(c, demands)
                if load + d > capacity:
                    continue
                key = (dist(current, c, coords), d, c)
                if best_key is None or key < best_key:
                    best_key = key
                    best = c
            if best is None:
                break
            route.append(best)
            load += demand_of(best, demands)
            unserved.remove(best)
            current = best

        routes.append(route)

    # Simple repair: move customers from overloaded singleton-like routes if possible
    # (helps if capacity was unknown or data irregular)
    def route_load(route):
        s = 0
        for n in route:
            s += demand_of(n, demands)
        return s

    changed = True
    while changed:
        changed = False
        # try to relocate a customer from a route to another feasible route
        for i in range(len(routes)):
            r = routes[i]
            if not r:
                continue
            for pos, node in enumerate(list(r)):
                nd = demand_of(node, demands)
                best_j = None
                best_insert = None
                best_delta = None
                for j in range(len(routes)):
                    if j == i:
                        continue
                    rr = routes[j]
                    if route_load(rr) + nd > capacity:
                        continue
                    # try insert at best position in rr
                    candidates = []
                    if not rr:
                        candidates.append((0, 0))
                    else:
                        for ins in range(len(rr) + 1):
                            prevn = depot if ins == 0 else rr[ins - 1]
                            nextn = depot if ins == len(rr) else rr[ins]
                            delta = dist(prevn, node, coords) + dist(node, nextn, coords) - dist(prevn, nextn, coords)
                            candidates.append((delta, ins))
                    candidates.sort()
                    delta, ins = candidates[0]
                    # removal delta from current route
                    prevn = depot if pos == 0 else r[pos - 1]
                    nextn = depot if pos == len(r) - 1 else r[pos + 1]
                    rem_delta = dist(prevn, node, coords) + dist(node, nextn, coords) - dist(prevn, nextn, coords)
                    total_delta = delta - rem_delta
                    if best_delta is None or (total_delta, j, ins, node) < best_delta:
                        best_delta = (total_delta, j, ins, node)
                        best_j = j
                        best_insert = ins
                if best_j is not None:
                    total_delta, j, ins, node = best_delta
                    # accept only non-worsening or if it creates capacity slack in a better-ordered way
                    if total_delta <= 0:
                        routes[best_j].insert(best_insert, node)
                        del routes[i][pos]
                        changed = True
                        break
            if changed:
                break

    # 2-opt within each route for deterministic improvement when coordinates exist
    if coords is not None:
        for idx in range(len(routes)):
            r = routes[idx]
            improved = True
            while improved:
                improved = False
                n = len(r)
                for i in range(n - 2):
                    a = depot if i == 0 else r[i - 1]
                    b = r[i]
                    for j in range(i + 1, n - 1):
                        c = r[j]
                        d = depot if j == n - 1 else r[j + 1]
                        before = dist(a, b, coords) + dist(c, d, coords)
                        after = dist(a, c, coords) + dist(b, d, coords)
                        if after + 1e-12 < before:
                            r[i:j + 1] = list(reversed(r[i:j + 1]))
                            improved = True
                            break
                    if improved:
                        break
            routes[idx] = r

    # Ensure all customers are present exactly once; if anything went wrong, repair deterministically.
    seen = {}
    for r in routes:
        for n in r:
            seen[n] = seen.get(n, 0) + 1
    missing = [c for c in customers if seen.get(c, 0) == 0]
    duplicates = [c for c, k in seen.items() if k > 1]

    if missing or duplicates:
        flat = []
        for r in routes:
            for n in r:
                if seen.get(n, 0) == 1:
                    flat.append(n)
        for d in duplicates:
            while seen.get(d, 0) > 1:
                seen[d] -= 1
        for c in missing:
            flat.append(c)
        routes = []
        cur = []
        load = 0
        for c in flat:
            d = demand_of(c, demands)
            if cur and load + d > capacity:
                routes.append(cur)
                cur = [c]
                load = d
            else:
                cur.append(c)
                load += d
        if cur:
            routes.append(cur)

    return routes
