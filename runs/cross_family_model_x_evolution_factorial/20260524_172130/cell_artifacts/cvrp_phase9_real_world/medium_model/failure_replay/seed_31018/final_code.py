def solve_cvrp(instance):
    """
    Deterministic constructive + repair CVRP solver with simple local improvements.
    Assumptions about 'instance':
      - instance is a dict with keys:
        - 'customers': list of dicts with 'id', 'demand', 'x', 'y'
        - 'depot': dict with 'id', 'x', 'y'
        - 'vehicle_capacity': int
      If keys differ, the function will try reasonable fallbacks.
    Returns:
      - routes: list of routes, each is a list of customer ids (no depot)
    """
    # Fallback parsing
    customers = []
    depot_id = None
    vehicle_capacity = None

    if isinstance(instance, dict):
        motor = instance
        depot = motor.get('depot')
        if depot:
            depot_id = depot.get('id')
        vehicle_capacity = motor.get('vehicle_capacity')
        custs = motor.get('customers')
        if custs is None:
            # try to build from a generic list
            items = motor.get('nodes') or motor.get('clients') or []
            for it in items:
                if isinstance(it, dict) and 'id' in it:
                    customers.append(it)
        else:
            customers = custs
    else:
        # If not dict, cannot solve
        return []

    # Normalize customers list
    if not customers:
        # If instance is a simple list of customer dicts
        try:
            # assume instance is a list of dicts
            if isinstance(instance, list):
                customers = instance
        except Exception:
            pass

    # Build simple deterministic order: by id
    # Ensure all customers have required fields
    valid = []
    for c in customers:
        if isinstance(c, dict) and 'id' in c and 'demand' in c:
            # ensure numbers
            try:
                cid = int(c['id'])
                dmd = int(c['demand'])
                x = c.get('x', 0.0)
                y = c.get('y', 0.0)
                valid.append({'id': cid, 'demand': dmd, 'x': x, 'y': y})
            except Exception:
                continue

    if not valid:
        return []

    # sort by id for determinism
    valid.sort(key=lambda c: c['id'])

    cap = vehicle_capacity if isinstance(vehicle_capacity, int) else 0
    if cap <= 0:
        # default reasonable capacity
        cap = max(1, sum(c['demand'] for c in valid) // max(1, len(valid) - 1))

    # Precompute simple distance from depot (assume depot at (0,0) if not provided)
    if depot and isinstance(depot, dict):
        dep_x = depot.get('x', 0.0)
        dep_y = depot.get('y', 0.0)
    else:
        dep_x = 0.0
        dep_y = 0.0

    def dist(a, b):
        dx = a['x'] - b['x']
        dy = a['y'] - b['y']
        return (dx*dx + dy*dy) ** 0.5

    # Build depot object
    depot_point = {'id': depot_id if depot_id is not None else 0, 'x': dep_x, 'y': dep_y}

    # Construction: greedy nearest where capacity allows
    unvisited = valid[:]
    routes = []

    while unvisited:
        route = []
        load = 0
        last = depot_point
        # select next by nearest neighbor to current location, among remaining with fit
        while True:
            # choose candidate with minimal distance from last and fit
            best = None
            best_score = None
            for c in unvisited:
                if load + c['demand'] > cap:
                    continue
                # distance from last to c
                d = ((last['x'] - c['x'])**2 + (last['y'] - c['y'])**2) ** 0.5
                # simple heuristic: prefer closer, and if first in route, distance from depot
                if best is None or d < best_score:
                    best = c
                    best_score = d
            if best is None:
                break
            # pick best
            route.append(best['id'])
            load += best['demand']
            unvisited.remove(best)
            last = {'id': best['id'], 'x': best['x'], 'y': best['y']}
        if route:
            routes.append(route)
        else:
            # cannot place any remaining due to single item exceeding cap; force assign it alone
            oddly = unvisited[0]
            if oddly['demand'] > cap:
                # force violate capacity minimally by starting new route, then continue
                routes.append([oddly['id']])
                unvisited.remove(oddly)
            else:
                # should not happen, but break to avoid infinite loop
                break

    # Repair: try to merge small routes if possible (improves efficiency)
    # Simple two-phase merge: attempt to concatenate two routes if total demand <= cap and merge reduces distance
    def route_demand(r):
        s = 0
        for cid in r:
            # find in valid
            for c in valid:
                if c['id'] == cid:
                    s += c['demand']
                    break
        return s

    i = 0
    while i < len(routes) - 1:
        r1 = routes[i]
        r2 = routes[i+1]
        d1 = route_demand(r1)
        d2 = route_demand(r2)
        if d1 + d2 <= cap:
            # compute rough detour distance: from depot -> r1 -> r2 (treat as concatenation)
            # We'll approximate by sum of internal distances using order as given
            def route_distance(r):
                if not r:
                    return 0
                # depot to first
                first = next((c for c in valid if c['id'] == r[0]), None)
                if first is None:
                    return 0
                total = ((depot_point['x'] - first['x'])**2 + (depot_point['y'] - first['y'])**2) ** 0.5
                for idx in range(len(r)-1):
                    a = next((c for c in valid if c['id'] == r[idx]), None)
                    b = next((c for c in valid if c['id'] == r[idx+1]), None)
                    if a is not None and b is not None:
                        total += ((a['x'] - b['x'])**2 + (a['y'] - b['y'])**2) ** 0.5
                return total
            new_dist = route_distance(r1 + r2)
            old_dist = route_distance(r1) + route_distance(r2)
            if new_dist <= old_dist:
                routes[i] = r1 + r2
                del routes[i+1]
                continue
        i += 1

    # Local improvement: swap adjacent customers between routes if improves
    improved = True
    while improved:
        improved = False
        for a in range(len(routes)):
            for b in range(a+1, len(routes)):
                ra = routes[a]
                rb = routes[b]
                for i_idx in range(len(ra)):
                    for j_idx in range(len(rb)):
                        # compute new loads after swap
                        cand_a = ra[:]
                        cand_b = rb[:]
                        cid_a = cand_a[i_idx]
                        cid_b = cand_b[j_idx]
                        # get demands
                        da = next((c['demand'] for c in valid if c['id'] == cid_a), 0)
                        db = next((c['demand'] for c in valid if c['id'] == cid_b), 0)
                        load_a = sum(next((c['demand']) for c in valid if c['id'] == x) for x in cand_a)  # type: ignore
                        load_b = sum(next((c['demand']) for c in valid if c['id'] == x) for x in cand_b)  # type: ignore
                        if load_a - da + db > cap or load_b - db + da > cap:
                            continue
                        # perform swap
                        cand_a[i_idx] = cid_b
                        cand_b[j_idx] = cid_a
                        # compute simple distance cost before/after
                        def route_cost(seq):
                            if not seq:
                                return 0
                            total = ((depot_point['x'] - next((c['x'] for c in valid if c['id'] == seq[0]), 0))**2 +
                                     (depot_point['y'] - next((c['y'] for c in valid if c['id'] == seq[0]), 0))**2) ** 0.5
                            for k in range(len(seq)-1):
                                a = next((c for c in valid if c['id'] == seq[k]), None)
                                b = next((c for c in valid if c['id'] == seq[k+1]), None)
                                if a is None or b is None:
                                    continue
                                total += ((a['x'] - b['x'])**2 + (a['y'] - b['y'])**2) ** 0.5
                            return total
                        old = route_cost(ra) + route_cost(rb)
                        new = route_cost(cand_a) + route_cost(cand_b)
                        if new < old:
                            routes[a] = cand_a
                            routes[b] = cand_b
                            improved = True
        # end double loop

    # Final cleanliness: ensure all customers covered
    covered = set()
    for r in routes:
        for cid in r:
            covered.add(cid)
    all_ids = set(c['id'] for c in valid)
    if covered != all_ids:
        # attempt to fix by distributing missing ids to new routes
        missing = list(all_ids - covered)
        for mid in missing:
            routes.append([mid])

    return routes
