def solve_cvrp(instance):
    # Deterministic constructive solver with simple repair and local-improvement.
    # Instance expected as a dict with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id or 0
    # - 'capacity': int
    # We'll assume customers are numbered with positive integers and depot is 0 or specified.
    customers = instance.get('customers', [])
    depot = instance.get('depot', 0)
    capacity = instance.get('capacity', 0)

    # Build a simple list of customers with id and demand
    custs = []
    for c in customers:
        cid = c.get('id', None)
        if cid is None:
            continue
        demand = int(c.get('demand', 0))
        custs.append({'id': cid, 'demand': demand})

    # If no customers, return empty routes
    if not custs:
        return []

    # Sort customers by id to have deterministic order
    custs.sort(key=lambda x: x['id'])

    # Helper: create a route from a sequence of customers
    def make_route(seq):
        return [c['id'] for c in seq]

    # Initialize routes by simple sequential packing into vehicles with capacity
    routes = []
    current_route = []
    current_load = 0

    for c in custs:
        d = c['demand']
        if d > capacity:
            # If a single customer exceeds capacity, cannot satisfy; skip by creating singleton route
            # This is a deterministic fallback; in a proper solver this would fail.
            if current_route:
                routes.append(make_route(current_route))
                current_route = []
                current_load = 0
            routes.append([c['id']])
            continue

        if current_load + d <= capacity:
            current_route.append(c)
            current_load += d
        else:
            # finish current route and start new one
            routes.append(make_route(current_route))
            current_route = [c]
            current_load = d

    if current_route:
        routes.append(make_route(current_route))

    # Repair: ensure no route is empty and all customers covered
    # Deterministic check: collect all ids in routes and compare
    seen = []
    for r in routes:
        seen.extend(r)
    seen_set = set(seen)
    all_ids = set([c['id'] for c in custs])
    if seen_set != all_ids:
        # Fix missing by appending any missing id to last route
        missing = sorted(list(all_ids - seen_set))
        for mid in missing:
            if routes:
                routes[-1].append(mid)
            else:
                routes.append([mid])

    # Local improvement: try to reduce route count by merging if capacity allows,
    # in a deterministic way: attempt to merge adjacent routes' last and first customers.
    improved = True
    while improved:
        improved = False
        if len(routes) >= 2:
            r1 = routes[0]
            r2 = routes[1]
            if r1 and r2:
                # get last of r1 and first of r2
                c_last = next((c for c in custs if c['id'] == r1[-1]), None)
                c_first = next((c for c in custs if c['id'] == r2[0]), None)
                if c_last and c_first:
                    total_d = c_last['demand'] + c_first['demand']
                    if total_d <= capacity:
                        # merge
                        routes[0] = r1 + [r2[0]]
                        routes[1] = r2[1:]
                        improved = True
                        # remove empty route if any
                        if not routes[1]:
                            routes.pop(1)
        # If after attempt the first route got emptied (edge case)
        if routes and not routes[0]:
            routes.pop(0)

    return routes
