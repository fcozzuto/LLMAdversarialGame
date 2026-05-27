def solve_cvrp(instance):
    # Deterministic constructive CVRP solver with simple repair/local-search phases.
    # Instance format assumed:
    # instance = {
    #   'customer_count': N, integers 1..N,
    #   'demands': {i: d_i, ...},  # i in 1..N
    #   'capacities': {'vehicle_capacity': C},
    #   'depot': 0
    # }
    # We return routes as list of lists, each inner list is a route of customer ids (no depot).
    #
    # Assumptions (to keep self-contained and no imports):
    # - Customers are numbered 1..N
    # - Distances are not needed for feasibility; we use a simple deterministic order
    #   and a nearest-fit style by input order.
    # - We ensure every customer is included exactly once and capacity constraints are met.

    # Extract basic data
    N = instance.get('customer_count', 0)
    demands = instance.get('demands', {})
    C = instance.get('capacities', {}).get('vehicle_capacity', 0)
    # Fallback: if demands not provided in dict, assume 1 each
    def demand(i):
        return demands.get(i, 1)

    if N <= 0 or C <= 0:
        return []

    # Create a deterministic order of customers: 1..N
    order = list(range(1, N + 1))

    # Phase 1: constructive packing by simple first-fit-in-decreasing-like (but deterministically original order)
    routes = []
    current_route = []
    current_load = 0

    for i in order:
        di = demand(i)
        if di > C:
            # Individual customer exceeds capacity; place it in its own route (unusual case)
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([i])
            continue

        if current_load + di <= C:
            current_route.append(i)
            current_load += di
        else:
            # start new route
            if current_route:
                routes.append(current_route)
            current_route = [i]
            current_load = di

    if current_route:
        routes.append(current_route)

    # Phase 2: simple local repair: try to swap last element of a route with first of next if it improves balance
    # We use a tiny deterministic improvement: move from larger to smaller to balance loads but without distances.
    improved = True
    while improved:
        improved = False
        for idx in range(len(routes) - 1):
            r1 = routes[idx]
            r2 = routes[idx + 1]
            if not r1 or not r2:
                continue
            l1 = sum(demand(x) for x in r1)
            l2 = sum(demand(x) for x in r2)
            # Try moving last of r1 to front of r2
            x = r1[-1]
            dx = demand(x)
            if l1 - dx <= C and l2 + dx <= C:
                # perform move
                new_r1 = r1[:-1]
                new_r2 = [x] + r2
                routes[idx] = new_r1
                routes[idx + 1] = new_r2
                improved = True
                break
        if improved:
            continue

    # Phase 3: ensure each customer exactly once (remove duplicates if any)
    seen = set()
    unique_routes = []
    for r in routes:
        new_r = []
        for c in r:
            if c not in seen:
                seen.add(c)
                new_r.append(c)
        if new_r:
            unique_routes.append(new_r)
    routes = unique_routes

    # Phase 4: final verification and fix: ensure all customers present
    all_customers = set(range(1, N + 1))
    present = set()
    for r in routes:
        for c in r:
            present.add(c)
    missing = sorted(all_customers - present)
    # Append missing customers as single-customer routes (deterministic)
    for c in missing:
        routes.append([c])

    # Phase 5: ensure capacity constraints still satisfied after adjustments
    # If any route exceeds capacity due to missing handling, split them
    final_routes = []
    for r in routes:
        cur = []
        cur_load = 0
        for c in r:
            dc = demand(c)
            if cur_load + dc <= C:
                cur.append(c)
                cur_load += dc
            else:
                if cur:
                    final_routes.append(cur)
                cur = [c]
                cur_load = dc
        if cur:
            final_routes.append(cur)
    routes = final_routes

    # Final pass: if any route empty, filter
    routes = [r for r in routes if r]

    return routes
