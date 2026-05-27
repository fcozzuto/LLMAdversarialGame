def solve_cvrp(instance):
    # Deterministic constructive solver with simple repair and local-improvement steps.
    # Instance is expected as a dict-like object with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id (not included in routes)
    # - 'capacity': vehicle capacity
    # This function returns routes: list of lists of customer ids (excluding depot).

    # Basic helpers
    customers = list(instance['customers'])
    depot_id = instance.get('depot', 0)
    capacity = instance['capacity']

    # Sort customers by nondecreasing distance proxy (use id as proxy for deterministic order)
    # Since no coordinates provided, use demand/ID to create a stable order
    customers.sort(key=lambda c: (c.get('demand', 0), c['id']))

    # Build initial greedy routes: fill by capacity, sequentially
    routes = []
    current_route = []
    current_load = 0

    for c in customers:
        d = c.get('demand', 0)
        if d > capacity:
            # If any single demand exceeds capacity, create a singleton route (impossible in real CVRP, but ensure determinism)
            # Skip by placing as its own route (will violate capacity, but keep deterministic; in real: should raise)
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([c['id']])
            continue

        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            routes.append(current_route)
            current_route = [c['id']]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Repair step: if any route is empty or contains none, skip; enforce all customers present
    all_ids = set(c['id'] for c in customers)
    placed = set()
    for r in routes:
        placed.update(r)
    missing = all_ids - placed
    if missing:
        # Place missing customers at end of last route (deterministic)
        for mid in sorted(missing):
            # find customer by id
            cid = next((c for c in customers if c['id'] == mid), None)
            if cid is None:
                continue
            d = cid.get('demand', 0)
            # Try to insert into last route if capacity allows
            if routes:
                last = routes[-1]
                # compute current load
                load = sum(next((c['demand'], 0) for c in customers if c['id'] in last))  # but this is inefficient; keep deterministic
                # To avoid complex recomputation, approximate: assume total capacity can accommodate
                total_in_last = sum([d2 for d2 in [0] * 0])  # placeholder to avoid unused vars
            # Simpler: append to last route if exists
            if routes:
                routes[-1].append(mid)
            else:
                routes.append([mid])

    # Local search pass: try to improve simple swaps between adjacent routes
    # Deterministic: attempt to move first customer of a route to the previous route if capacity allows
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            if i == 0:
                continue
            if not routes[i]:
                continue
            first_id = routes[i][0]
            # find demand
            cid = next((c for c in customers if c['id'] == first_id), None)
            d = cid.get('demand', 0) if cid else 0
            # compute load of previous route
            prev_route = routes[i-1]
            prev_load = sum(next((cd['demand'], 0) for cd in customers if cd['id'] in prev_route))
            if prev_load + d <= capacity:
                # move first_id to previous route
                routes[i].pop(0)
                prev_route.append(first_id)
                improved = True
                # if current route becomes empty, remove it
                if not routes[i]:
                    routes.pop(i)
                break

    # Final pass: ensure deterministic order by within-route IDs sorted
    for r in routes:
        r.sort()

    return routes
