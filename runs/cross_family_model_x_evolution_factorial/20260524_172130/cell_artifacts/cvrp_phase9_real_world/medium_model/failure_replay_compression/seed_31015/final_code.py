def solve_cvrp(instance):
    # instance is expected to be a dict-like object with keys:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id or index (not included in routes)
    # - 'capacity': vehicle capacity (int or float)
    # - optionally 'dist' function or matrix not required; we will use a simple deterministic heuristic
    #
    # We implement a constructive + repair approach:
    # 1) Sort customers by non-increasing demand (to pack large demands first deterministically)
    # 2) Build routes by greedy insertion while maintaining capacity
    # 3) Simple local repair: try to swap customers between routes if it reduces a basic cost surrogate
    # 4) Return routes as lists of customer ids (excluding depot)

    # Minimal deterministic helpers (no imports)
    customers = instance.get('customers', [])
    depot = instance.get('depot', None)
    capacity = instance.get('capacity', 0)

    # Create a deterministic order: sort by (-demand, id) to break ties
    sorted_customers = sorted(customers, key=lambda c: (-c.get('demand', 0), c.get('id')))

    # Helper: get demand per id
    demand_of = {c['id']: c.get('demand', 0) for c in customers}

    # Maintain routes as lists of ids
    routes = []
    route_loads = []

    # Construct routes greedily
    for c in sorted_customers:
        cid = c['id']
        d = c.get('demand', 0)
        # Try to put into first route that has enough capacity
        placed = False
        for i, load in enumerate(route_loads):
            if load + d <= capacity:
                routes[i].append(cid)
                route_loads[i] = load + d
                placed = True
                break
        if not placed:
            # start new route
            routes.append([cid])
            route_loads.append(d)

    # Local repair: try to move a customer from a longer route to another if feasible
    # We'll attempt simple pairwise reassignment to reduce number of routes if possible
    # and to balance loads. Deterministic: single sweep
    n = len(routes)
    if n > 1:
        # Flatten with route indices for deterministic processing
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if not routes[i]:
                    continue
                if not routes[j]:
                    continue
                # Take last customer from i and try to move to j if capacity allows
                cid = routes[i][-1]
                d = demand_of[cid]
                load_i = route_loads[i]
                load_j = route_loads[j]
                if load_j + d <= capacity:
                    # move
                    routes[i].pop()
                    route_loads[i] -= d
                    routes[j].append(cid)
                    route_loads[j] += d
                    # If i becomes empty, drop it
                    if not routes[i]:
                        routes.pop(i)
                        route_loads.pop(i)
                    # break to restart deterministic scanning
                    n = len(routes)
                    if n == 0:
                        break
        # Additional small swap pass: try to swap endpoints between routes to reduce fragmentation
        changed = True
        while changed:
            changed = False
            for i in range(len(routes)):
                for j in range(len(routes)):
                    if i == j:
                        continue
                    if not routes[i] or not routes[j]:
                        continue
                    ci = routes[i][-1]
                    cj = routes[j][-1]
                    di = demand_of[ci]
                    dj = demand_of[cj]
                    # swap if improves balance and respects capacities
                    if route_loads[i] - di + dj <= capacity and route_loads[j] - dj + di <= capacity:
                        routes[i][-1], routes[j][-1] = routes[j][-1], routes[i][-1]
                        route_loads[i] = route_loads[i] - di + dj
                        route_loads[j] = route_loads[j] - dj + di
                        changed = True

    # Final sanity: ensure all customers included exactly once
    all_ids = []
    for r in routes:
        all_ids.extend(r)
    # Build a quick membership check
    seen = set(all_ids)
    customer_ids = {c['id'] for c in customers}
    if seen != customer_ids:
        # Simple fallback: rebuild deterministically by inserting any missing ids
        missing = sorted(customer_ids - seen)
        for mid in missing:
            placed = False
            for i, load in enumerate(route_loads):
                # naive: try to fit at end
                d = demand_of[mid]
                if load + d <= capacity:
                    routes[i].append(mid)
                    route_loads[i] += d
                    placed = True
                    break
            if not placed:
                routes.append([mid])
                route_loads.append(demand_of[mid])

    # Ensure each route is a list of ids and not including depot
    # If any empty route appears, drop it
    routes = [r for r in routes if len(r) > 0]

    return routes
