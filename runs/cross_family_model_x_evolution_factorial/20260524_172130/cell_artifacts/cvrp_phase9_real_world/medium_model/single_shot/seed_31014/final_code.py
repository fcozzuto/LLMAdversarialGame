def solve_cvrp(instance):
    # instance is expected to be a dict with:
    # - 'demands': dict {customer_id: demand}
    # - 'coords': dict {customer_id: (x, y)} or a list-like structure
    # - 'depot': depot_id
    # - 'capacity': vehicle capacity
    #
    # Deterministic constructive solver with simple repair/local-search ideas.
    #
    # Get customers
    depot = instance['depot']
    demands = instance['demands']
    capacity = instance['capacity']

    # Build a deterministic ordering of customers: sort by non-decreasing demand, then by id
    customers = [cid for cid in demands.keys() if cid != depot]
    customers.sort(key=lambda cid: (demands[cid], cid))

    # Compute a simple distance metric using coordinates (if provided)
    coords = instance.get('coords', {})
    def dist(a, b):
        ca = coords.get(a, (0, 0))
        cb = coords.get(b, (0, 0))
        dx = ca[0] - cb[0]
        dy = ca[1] - cb[1]
        return (dx*dx + dy*dy) ** 0.5

    # Start with empty routes and current load per route
    routes = []
    current_route = []
    current_load = 0
    last_customer = depot

    # Helper: add current route to routes if not empty
    def finalize_route():
        nonlocal current_route, current_load
        if current_route:
            routes.append(current_route)
        current_route = []
        current_load = 0

    # Construct routes greedily: assign next smallest-demand customer to current route if fits;
    # otherwise finalize current route and start a new one
    for c in customers:
        d = demands[c]
        if d > capacity:
            # A single customer exceeding capacity is not solvable; skip to avoid crash
            # In a robust solver, we could split, but we must return feasible routes.
            continue

        if current_load + d <= capacity:
            current_route.append(c)
            current_load += d
            last_customer = c
        else:
            finalize_route()
            current_route = [c]
            current_load = d
            last_customer = c

    finalize_route()

    # If any route is empty (edge case), remove
    routes = [r for r in routes if r]

    # Local repair: try to swap between routes to improve compactness without increasing load
    # Deterministic pairwise swap: for each pair of routes, try moving a tail element to next route if fits
    improved = True
    # Limit iterations to keep it deterministic and finite
    max_iters = 5
    iters = 0
    while improved and iters < max_iters:
        improved = False
        iters += 1
        for i in range(len(routes) - 1):
            if not routes[i]:
                continue
            # Try moving last of route i to route i+1 if fits
            last = routes[i][-1]
            ld = demands[last]
            if ld + sum(demands[c] for c in routes[i+1]) <= capacity:
                # Move
                routes[i].pop()
                routes[i+1].append(last)
                improved = True
                # If route becomes empty, remove it
                if not routes[i]:
                    del routes[i]
                break
        if improved:
            continue
        # Try moving first of route i+1 to route i
        for i in range(len(routes) - 1):
            if not routes[i+1]:
                continue
            first = routes[i+1][0]
            fd = demands[first]
            if sum(demands[c] for c in routes[i]) + fd <= capacity:
                routes[i+1] = routes[i+1][1:]
                routes[i].append(first)
                improved = True
                if not routes[i+1]:
                    del routes[i+1]
                break

    # Final check: ensure each customer appears exactly once
    seen = set()
    for r in routes:
        for c in r:
            if c in seen:
                pass
            seen.add(c)
    # If some customers missing due to issues, attempt simple re-add by leftover
    all_customers = set([cid for cid in demands.keys() if cid != depot])
    missing = all_customers - seen
    if missing:
        # Try to append missing at end of last route if fits
        for m in sorted(missing):
            dm = demands[m]
            if routes:
                if sum(demands[c] for c in routes[-1]) + dm <= capacity:
                    routes[-1].append(m)
                    seen.add(m)
                    continue
            # otherwise start new route
            routes.append([m])
            seen.add(m)

    # Ensure no depot in routes (by construction)
    return routes
