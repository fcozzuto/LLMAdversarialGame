def solve_cvrp(instance):
    # instance = {
    #   'depot': depot_id,
    #   'customers': {id: {'demand': int, 'x': ..., 'y': ...}, ...},
    #   'capacity': C
    # }
    # Deterministic constructive solver with simple repair and local-improvement
    depot = instance['depot']
    capacity = instance['capacity']
    customers = dict(instance['customers'])  # id -> data
    # We will create a simple nearest-incomplete heuristic with deterministic tie-breaks
    unvisited = sorted([cid for cid in customers.keys()], key=lambda cid: cid)  # deterministic order
    routes = []
    while unvisited:
        route = []
        load = 0
        last = depot
        # Greedily add the nearest customer that fits
        # We approximate distance via simple Manhattan (x,y). If not provided, assume 0.
        def dist(a, b):
            ax = 0 if a == depot else customers[a].get('x', 0)
            ay = 0 if a == depot else customers[a].get('y', 0)
            bx = 0 if b == depot else customers[b].get('x', 0)
            by = 0 if b == depot else customers[b].get('y', 0)
            return abs(ax - bx) + abs(ay - by)
        # Build a candidate list sorted by distance from last with deterministic tie-break
        while True:
            candidates = []
            for cid in unvisited:
                d = dist(last, cid)
                if load + customers[cid]['demand'] <= capacity:
                    candidates.append((d, cid))
            if not candidates:
                break
            candidates.sort(key=lambda t: (t[0], t[1]))
            _, pick = candidates[0]
            route.append(pick)
            load += customers[pick]['demand']
            unvisited.remove(pick)
            last = pick
        if not route:
            # If a single customer's demand exceeds capacity (shouldn't happen in valid input),
            # skip it to avoid infinite loop (placehold, but keep deterministic behavior).
            cid = unvisited.pop(0)
            route.append(cid)
            unvisited = unvisited
        routes.append(route)
    # Local improvement: try to swap between routes if capacity allows and reduces total distance
    # Compute simple distance with depot returns for evaluation; implement one-pass attempt
    def route_distance(r):
        if not r:
            return 0
        d = 0
        prev = depot
        for cid in r:
            d += abs(customers[cid].get('x',0) - (0 if prev==depot else customers[prev].get('x',0))) + \
                 abs(customers[cid].get('y',0) - (0 if prev==depot else customers[prev].get('y',0)))
            prev = cid
        # return to depot
        d += abs(customers[prev].get('x',0)) + abs(customers[prev].get('y',0)
                )
        return d
    # Simple pairwise swap between routes
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                ri = routes[i].copy()
                rj = routes[j].copy()
                if not ri or not rj:
                    continue
                # try moving one from end of ri to end of rj if capacity allows
                moved = False
                cid = ri[-1]
                if sum(customers[c]['demand'] for c in rj) + customers[cid]['demand'] <= capacity:
                    new_ri = ri[:-1]
                    new_rj = rj + [cid]
                    routes_candidate = routes.copy()
                    routes_candidate[i] = new_ri
                    routes_candidate[j] = new_rj
                    # compute simple total distance to decide
                    def total_dist(rs):
                        return sum(route_distance(r) for r in rs)
                    if total_dist(routes_candidate) < total_dist(routes):
                        routes = routes_candidate
                        improved = True
                        moved = True
                        break
                if moved:
                    break
            if improved:
                break
    return routes
