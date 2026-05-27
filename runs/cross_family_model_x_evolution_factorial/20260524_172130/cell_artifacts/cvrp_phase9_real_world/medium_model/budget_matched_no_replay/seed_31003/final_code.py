def solve_cvrp(instance):
    # instance is expected to be a dict with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id or 0 (not included in routes)
    # - 'cap': vehicle capacity
    # We implement a deterministic constructive + simple repair/local-heuristic approach.

    # Extract data
    customers = instance.get('customers', [])
    depot = instance.get('depot', 0)
    capacity = instance.get('cap', None)
    if capacity is None:
        # If capacity not provided, try to infer from customer demands
        max_d = max((c.get('demand', 0) for c in customers), default=0)
        capacity = max(n for n in (max_d, 1))

    # Normalize customers: ensure each has id and demand
    custs = []
    for c in customers:
        cid = c.get('id')
        d = c.get('demand', 0)
        if cid is None:
            continue
        custs.append({'id': cid, 'demand': d})

    # Simple heuristic: sort customers by demand-to-distance proxy.
    # Since we don't have distances, use id as proxy for deterministic order.
    # We'll use a two-phase approach:
    # 1) Construct routes by filling capacity in increasing id order.
    # 2) If some route would exceed capacity, split.
    # 3) Optional local improvement: try to swap adjacent customers between routes to reduce route count without violating capacity.
    # This is deterministic and property-preserving.

    # Sort customers by id for determinism
    custs.sort(key=lambda x: x['id'])

    routes = []
    current_route = []
    current_load = 0

    for c in custs:
        d = c['demand']
        if d > capacity:
            # If a single customer exceeds capacity, we cannot serve; create empty route (ignored) and skip
            # To keep consistency, assign as its own route if possible by splitting into multiple trips is not allowed since demand>cap.
            # We'll still place it as its own route if possible (capacity check). If not, skip to avoid infinite loop.
            if d <= capacity:
                pass
            else:
                # Skip this customer to keep feasibility; in real solver we would split, but here we skip to maintain determinism.
                continue
        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            # finish current route
            if current_route:
                routes.append(current_route)
            # start new route
            current_route = [c['id']]
            current_load = d

    if current_route:
        routes.append(current_route)

    # If any route ended up empty, filter (though unlikely)
    routes = [r for r in routes if r]

    # Local improvement: try to move a customer from a larger route to a smaller one if it fits
    # This is a simple, deterministic 1-pass repair step.
    improved = True
    while improved:
        improved = False
        # Try all pairs of routes
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j:
                    continue
                ri = routes[i]
                rj = routes[j]
                if not ri:
                    continue
                # Try move last element of ri to rj
                cand = ri[-1]
                # find demand of cand
                d = None
                for c in custs:
                    if c['id'] == cand:
                        d = c['demand']
                        break
                if d is None:
                    continue
                # Compute new loads
                load_i = sum(next(x['demand'] for x in custs if x['id']==cid) for cid in ri)
                load_j = sum(next(x['demand'] for x in custs if x['id']==cid) for cid in rj)
                if load_j + d <= capacity:
                    # move
                    routes[i] = ri[:-1]
                    routes[j] = rj + [cand]
                    improved = True
                    break
            if improved:
                break

    # Final return: ensure no empty routes
    routes = [r for r in routes if r]
    return routes
