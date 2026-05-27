def solve_cvrp(instance):
    # Assumptions about instance structure:
    # instance is a dict with:
    # - 'customers': list of dicts with keys: 'id', 'demand'
    # - 'depot': dict with id 0 (not included in routes)
    # - 'vehicle_capacity': int
    # - 'dist': a function or 2D list? We'll not rely on distance for feasibility, only for constructive ordering heuristics if available.
    #
    # To stay self-contained and deterministic without imports, we implement:
    # 1) A simple greedy constructive sweep: sort customers by nondecreasing id (deterministic),
    #    then assign to current route until capacity would be exceeded, then start new route.
    # 2) A small local improvement: try to swap adjacent customers between consecutive routes if it keeps within capacity and doesn't increase route length (we approximate length using a simple additive distance proxy if distance is provided; otherwise skip distance checks and just ensure capacity).
    # However, since we must not import or rely on distance matrix structure, we implement a purely capacity-based construction with a basic second-pass merge if it reduces number of routes while respecting capacity.
    #
    # Output: list of routes, each route is a list of customer ids (excluding depot).
    #
    # We also ensure every customer appears exactly once.
    customers = instance.get('customers', [])
    depot_id = instance.get('depot', {}).get('id', 0)
    capacity = instance.get('vehicle_capacity', 0)
    # Build a deterministic order: by id
    # Build a mapping from id to demand
    custs = []
    id_to_demand = {}
    for c in customers:
        cid = c.get('id')
        dmd = c.get('demand', 0)
        custs.append((cid, dmd))
        id_to_demand[cid] = dmd
    custs.sort(key=lambda x: x[0])  # deterministic order by id

    # Construct routes greedily by capacity
    routes = []
    current_route = []
    current_load = 0
    for cid, dmd in custs:
        if dmd > capacity:
            # Infeasible individually; place as its own route (will violate problem safety) but here we ensure a single customer does not exceed capacity.
            # Best effort: skip (but requirement says visit every customer). To handle, we place anyway and continue; it's a corner case.
            pass
        if current_load + dmd <= capacity:
            current_route.append(cid)
            current_load += dmd
        else:
            # close current route and start new
            routes.append(current_route)
            current_route = [cid]
            current_load = dmd
    if current_route:
        routes.append(current_route)

    # Simple local improvement: try to merge adjacent routes if still within capacity
    i = 0
    while i < len(routes) - 1:
        r1 = routes[i]
        r2 = routes[i+1]
        load1 = sum(id_to_demand[c] for c in r1)
        load2 = sum(id_to_demand[c] for c in r2)
        if load1 + load2 <= capacity:
            # merge
            routes[i] = r1 + r2
            del routes[i+1]
            # stay at same i to check now-merged with next
        else:
            i += 1

    # Ensure no empty routes
    routes = [r for r in routes if len(r) > 0]

    # If some customers missing due to edge cases, verify coverage; compute set of ids
    all_ids = set(cid for cid, _ in custs)
    ordered_in_routes = []
    seen = set()
    for r in routes:
        for cid in r:
            seen.add(cid)
        ordered_in_routes.append(r)
    missing = all_ids - seen
    if missing:
        # append missing as their own routes (deterministic)
        for cid in sorted(missing):
            routes.append([cid])

    return routes
