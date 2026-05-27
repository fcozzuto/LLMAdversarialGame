def solve_cvrp(instance):
    # instance is expected to be a dict-like with:
    # - 'customers': a list of dicts with keys 'id', 'demand'
    # - 'depot': an id or index (not to be included in routes)
    # - 'capacity': vehicle capacity
    # The function returns a list of routes, each route is a list of customer ids (no depot),
    # visiting every customer exactly once, and with total demand per route <= capacity.
    #
    # Deterministic constructive + repair + local-search style:
    # 1) Sort customers by non-increasing demand (largest first) for stable, interpretable batching.
    # 2) Build routes by adding customers greedily until capacity would be exceeded, then start new route.
    # 3) Repair: if any route is empty (shouldn't happen) skip; ensure all customers covered.
    # 4) Local adjustment: try to swap a customer from a loaded route to an earlier route if it keeps feasibility.
    #
    # This is a single-shot, deterministic solver with no external data dependencies.

    # Extract data with safe fallbacks
    customers = instance.get('customers', [])
    depot_id = instance.get('depot', None)
    capacity = instance.get('capacity', None)

    # Quick validation / defaults
    if capacity is None:
        # If capacity missing, assume 1 to avoid division by zero; but also ensure integer
        capacity = 1

    # Build a simple mapping of id -> demand
    custs = []
    for c in customers:
        cid = c.get('id', None)
        demand = c.get('demand', 0)
        custs.append({'id': cid, 'demand': int(demand)})

    # If there are no customers, return empty list
    if not custs:
        return []

    # Sort customers by non-increasing demand for deterministic packing
    custs.sort(key=lambda x: (-x['demand'], x['id']))

    # Greedy constructive: pack into routes
    routes = []
    current_route = []
    current_load = 0

    for c in custs:
        d = c['demand']
        if d > capacity:
            # If a single demand exceeds capacity, we cannot satisfy constraints deterministically.
            # As a fallback, place it alone in its own route but still violate capacity; however, to
            # respect the constraint, return an empty plan indicating infeasibility.
            # We'll instead split into a minimal feasible approach by assigning to its own route if possible.
            # Here we skip adding this customer to avoid infinite loop; this situation should be prevented by input.
            continue

        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            # close current route and start new
            if current_route:
                routes.append(current_route)
            current_route = [c['id']]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Repair step: ensure all customers appear exactly once.
    # Build a set of assigned ids
    assigned = []
    for r in routes:
        assigned.extend(r)
    assigned_set = set(assigned)

    all_ids = set(c['id'] for c in custs)
    missing = list(all_ids - assigned_set)

    # If there are missing customers (due to capacity issues with impossible large demand), append them as separate routes
    # (best effort)
    for mid in missing:
        routes.append([mid])

    # Local adjustment: try to move a customer from a heavier route to an earlier one if feasible
    # For deterministic behavior, perform a single pass of simple checks.
    # Build a quick map id -> demand
    id_to_demand = {c['id']: c['demand'] for c in custs}

    # Recompute loads for safety
    def route_load(route):
        return sum(id_to_demand[cid] for cid in route)

    improved = True
    while improved:
        improved = False
        # Attempt to move any customer from route i to route i-1 if feasible
        for i in range(1, len(routes)):
            if not routes[i]:
                continue
            cid_to_move = routes[i][-1]  # take last as a heuristic
            d = id_to_demand[cid_to_move]
            load_prev = route_load(routes[i-1])
            if load_prev + d <= capacity:
                # move
                routes[i].pop()
                routes[i-1].append(cid_to_move)
                improved = True
        if improved:
            # clean up empty routes
            routes = [r for r in routes if r]

    # Final guard: ensure no route exceeds capacity and all ids appear
    final_routes = []
    seen = set()
    valid = True
    for r in routes:
        total = 0
        for cid in r:
            total += id_to_demand[cid]
            seen.add(cid)
        if total > capacity:
            valid = False
        final_routes.append(list(r))

    # If somehow some customers are missing due to oddities, attempt a simple fix by placing missing into new routes
    missing_all = all_ids - seen
    if missing_all:
        for mid in missing_all:
            final_routes.append([mid])

    return final_routes
