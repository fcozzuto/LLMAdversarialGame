def solve_cvrp(instance):
    # instance expected as a dict-like with:
    # - 'customers': list of dicts with 'id', 'x', 'y', 'demand'
    # - 'vehicle_capacity': int
    # - optional 'depot': dict with 'id', 'x', 'y' (not used in routes)
    #
    # Deterministic constructive + simple repair + local improvement without imports.
    customers = list(instance['customers'])
    depot = instance.get('depot', {'id': 0})
    capacity = instance['vehicle_capacity']
    # Sort customers by a simple deterministic key: demand descending stable tie-breaker by id
    customers.sort(key=lambda c: (-c['demand'], c['id']))
    unassigned = [c for c in customers]
    routes = []

    # Construct routes: greedy fill by capacity using simple sequential placement
    while unassigned:
        route = []
        remaining = capacity
        i = 0
        # pick the next feasible customers in order
        while i < len(unassigned):
            c = unassigned[i]
            if c['demand'] <= remaining:
                route.append(c['id'])
                remaining -= c['demand']
                unassigned.pop(i)
            else:
                i += 1
        if route:
            routes.append(route)
        else:
            # If a single customer demand exceeds capacity (unusual), create a singleton route
            # to avoid infinite loop
            c = unassigned.pop(0)
            routes.append([c['id']])

    # Simple repair: try to merge adjacent routes if capacity allows (deterministic)
    merged = True
    while merged:
        merged = False
        for i in range(len(routes) - 1):
            r1 = routes[i]
            r2 = routes[i+1]
            cap_used = 0
            for cid in r1:
                d = next((c['demand'] for c in customers if c['id'] == cid), 0)
                cap_used += d
            cap_used2 = 0
            for cid in r2:
                d = next((c['demand'] for c in customers if c['id'] == cid), 0)
                cap_used2 += d
            total = cap_used + cap_used2
            if total <= capacity:
                # merge r2 into r1
                routes[i] = r1 + r2
                routes.pop(i+1)
                merged = True
                break

    # Local improvement: attempt 2-opt style swap between adjacent routes (simple)
    # Ensure each customer appears once already; implement a small improvement by moving
    # a leading item of a route to previous route if capacity allows.
    for idx in range(1, len(routes)):
        if not routes[idx]:
            continue
        lead = routes[idx][0]
        d_lead = next((c['demand'] for c in customers if c['id'] == lead), 0)
        # try move to previous route if capacity allows
        prev_route = routes[idx-1]
        used_prev = sum(next((c['demand'] for c in customers if c['id'] == cid), 0) for cid in prev_route)
        if used_prev + d_lead <= capacity:
            # perform move
            routes[idx] = routes[idx][1:]
            routes[idx-1] = prev_route + [lead]
            # if current becomes empty, remove
            if not routes[idx]:
                routes.pop(idx)

    return routes
