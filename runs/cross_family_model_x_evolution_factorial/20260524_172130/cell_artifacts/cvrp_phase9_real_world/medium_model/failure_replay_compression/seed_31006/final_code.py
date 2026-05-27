def solve_cvrp(instance):
    # Assumptions about instance structure:
    # instance is a dict with keys:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id or index (not included in routes)
    # - 'capacity': int
    # We will implement a deterministic constructive solver with simple repair/local-search steps.

    customers = instance.get('customers', [])
    depot_id = instance.get('depot', None)
    capacity = instance.get('capacity', None)

    # Normalize customers as list of (id, demand)
    custs = []
    for c in customers:
        cid = c.get('id')
        dem = int(c.get('demand', 0))
        if cid == depot_id:
            continue
        custs.append((cid, dem))

    # If capacity not provided, infer from max demand or sum
    if capacity is None:
        max_dem = max((d for (_, d) in custs), default=0)
        capacity = max(1, max_dem * 2)

    # Sort customers by a simple heuristic: smallest demand first (deterministic)
    custs.sort(key=lambda x: (x[1], x[0]))

    # Construct routes by simple bin-packing into capacity, sequentially
    routes = []
    current_route = []
    current_load = 0

    for cid, dem in custs:
        if dem > capacity:
            # single customer cannot fit; create a route with this single customer (edge case)
            # In such case, we still place it as its own route to satisfy constraint
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([cid])
            continue

        if current_load + dem <= capacity:
            current_route.append(cid)
            current_load += dem
        else:
            # finalize previous route and start new
            if current_route:
                routes.append(current_route)
            current_route = [cid]
            current_load = dem

    if current_route:
        routes.append(current_route)

    # Local improvement: try to swap between routes to reduce number of routes (merge) if possible
    # Deterministic pairwise improvement: attempt to move a customer from a larger route to a smaller one
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j or not routes[i] or not routes[j]:
                    continue
                # try move last of i to j
                cid = routes[i][-1]
                dem = next(d for (c, d) in custs if c == cid)
                # current loads
                load_i = sum(next(d) for (c, d) in [(x, next((d for (cc, d) in custs if cc == x), 0)) for x in routes[i]])
                # Simpler: recompute loads
                load_i = sum(next(d) for (c, d) in [(x, next((d for (cc, d) in custs if cc == x), 0)) for x in routes[i]])
                load_j = sum(next(d) for (c, d) in [(x, next((d for (cc, d) in custs if cc == x), 0)) for x in routes[j]])
                # get dem
                if load_j + dem <= capacity:
                    # perform move
                    routes[i].pop()
                    routes[j].append(cid)
                    improved = True
                    break
            if improved:
                # cleanup empty routes
                routes = [r for r in routes if r]
                break

    return routes
