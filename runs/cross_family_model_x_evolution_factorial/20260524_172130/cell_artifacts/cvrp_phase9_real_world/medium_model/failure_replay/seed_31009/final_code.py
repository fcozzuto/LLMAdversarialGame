def solve_cvrp(instance):
    # Deterministic constructive solver with simple repair/local-search flavor.
    # Instance format assumed:
    # instance = {
    #   'customers': {id: {'d': demand, 'x': x, 'y': y}, ...},
    #   'depot': id (not included in customer list),
    #   'capacity': C
    # }
    #
    # Output: list of routes, each route is list of customer ids (excluding depot)
    #
    # Approach:
    # 1) Sort customers by nondecreasing demand-to-distance heuristic to prefer small, near-depot first.
    # 2) Build routes sequentially by adding nearest unscheduled customer that fits remaining capacity.
    # 3) If a customer cannot fit in any existing route, start a new route.
    # 4) After constructive pass, perform a simple intra-route reordering by nearest neighbor inside route to reduce travel distance (deterministic).
    # 5) Return routes.

    if not instance or 'customers' not in instance or 'capacity' not in instance or 'depot' not in instance:
        return []

    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['capacity']

    # Helper: distance between two customer ids
    def dist(a, b):
        pa = customers[a]
        pb = customers[b]
        dx = pa['x'] - pb['x']
        dy = pa['y'] - pb['y']
        return (dx*dx + dy*dy) ** 0.5

    # Dist from depot to customer
    def dist_depot(cust):
        dep = customers[depot]
        dcx = dep['x'] - customers[cust]['x']
        dcy = dep['y'] - customers[cust]['y']
        return (dcx*dcx + dcy*dcy) ** 0.5

    # Build a deterministic order: sort by (demand, distance to depot)
    order = sorted(customers.keys(), key=lambda cid: (customers[cid]['d'], dist_depot(cid)))

    # Track remaining capacity in each route
    routes = []
    route_caps = []
    route_elems = []

    for cid in order:
        d = customers[cid]['d']
        # Try to put into an existing route that has room, pick the first that fits
        placed = False
        for i in range(len(routes)):
            if route_caps[i] + d <= capacity:
                route_elems[i].append(cid)
                route_caps[i] += d
                placed = True
                break
        if not placed:
            # start a new route
            routes.append([])  # not used, we'll fill route_elems below
            route_elems.append([cid])
            route_caps.append(d)

    # Remove empty routes (if any)
    final_routes = [list(r) for r in route_elems if len(r) > 0]

    # Basic intra-route reordering: for each route, reorder by nearest neighbor starting from current first element.
    # This makes the route deterministic while improving distance a bit.
    for r in final_routes:
        if len(r) <= 2:
            continue
        ordered = [r[0]]
        remaining = r[1:]
        while remaining:
            last = ordered[-1]
            # pick nearest among remaining
            next_c = min(remaining, key=lambda c: dist(last, c))
            ordered.append(next_c)
            remaining.remove(next_c)
        # replace
        idx = final_routes.index(r)
        final_routes[idx] = ordered

    return final_routes
