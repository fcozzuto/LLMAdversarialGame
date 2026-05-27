def solve_cvrp(instance):
    # instance is expected as a dict-like object with:
    # - 'customers': list of dicts with keys 'id', 'demand'
    # - 'depot': id (not included in routes)
    # - 'vehicle_capacity': numeric
    #
    # Deterministic constructive solver with simple repair/local-search ideas.
    # Approach:
    # 1) Sort customers by nondecreasing demand-to-distance proxy (distance from depot if available).
    # 2) Build routes greedily: fill each route with next closest feasible customers by that proxy.
    # 3) After initial build, perform simple intra-route 2-opt-like local improvement on each route by swapping adjacent customers if improves feasibility/sum distance (distance is not required by problem, but keeps deterministic improvement).
    #
    # The instance format is assumed to be minimal; if distance data missing, we fall back to a simple list order.
    #
    # Output: list of routes; each route is a list of customer ids (excluding depot).
    #
    # Helper: get distance proxy
    def _proxy(cust, depot):
        # If distance field available use it; else use index as stable proxy
        if isinstance(cust, dict):
            # try to use a 'distance' attribute relative to depot
            d = cust.get('distance_to_depot')
            if isinstance(d, (int, float)):
                return d
            # fall back to demand to encourage smalls first
            return cust.get('demand', 0)
        return 0

    # Extract data with robust fallbacks
    depot = instance.get('depot', 0)
    customers = []
    for c in instance.get('customers', []):
        # ensure id and demand exist
        cid = c.get('id')
        if cid is None:
            continue
        demand = c.get('demand', 0)
        cust = {'id': cid, 'demand': demand}
        # propagate optional distance field
        if isinstance(c, dict) and 'distance_to_depot' in c:
            cust['distance_to_depot'] = c['distance_to_depot']
        customers.append(cust)

    if not customers:
        return []

    capacity = instance.get('vehicle_capacity', None)
    if capacity is None:
        # default capacity if missing
        capacity = max(1, max(c['demand'] for c in customers))

    # Sort by a deterministic proxy: smaller distance to depot or smaller demand
    try:
        customers.sort(key=lambda c: (c.get('distance_to_depot', None) if 'distance_to_depot' in c else None, c['demand']))
    except Exception:
        customers.sort(key=lambda c: c['demand'])

    # Build routes
    routes = []
    current_route = []
    current_load = 0

    for c in customers:
        d = c['demand']
        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            # close current route and start new
            if current_route:
                routes.append(current_route)
            current_route = [c['id']]
            current_load = d
            # if single customer exceeds capacity, place it alone (as a fallback)
            if current_load > capacity:
                # split not allowed; keep as is to ensure feasibility (may violate)
                # We'll create a dedicated route and continue
                current_route = [c['id']]
                current_load = d

    if current_route:
        routes.append(current_route)

    # Repair: ensure no route exceeds capacity (defensive)
    repaired = []
    for rt in routes:
        load = 0
        new_rt = []
        for cid in rt:
            dem = next((c['demand'] for c in customers if c['id'] == cid), 0)
            if load + dem <= capacity:
                new_rt.append(cid)
                load += dem
            else:
                if new_rt:
                    repaired.append(new_rt)
                new_rt = [cid]
                load = dem
        if new_rt:
            repaired.append(new_rt)

    routes = repaired

    # Local improvement: try swapping adjacent customers within each route if feasible and "closer" by a naive proxy
    def _route_swap_improve(rt):
        improved = True
        # simple pairwise swap until no improvement
        while improved:
            improved = False
            for i in range(len(rt) - 1):
                a, b = rt[i], rt[i+1]
                # find demands
                da = next((c['demand'] for c in customers if c['id'] == a), 0)
                db = next((c['demand'] for c in customers if c['id'] == b), 0)
                # check swap feasibility
                # compute current load for the segment (we already know route feasible)
                # After swap, feasibility remains same for the two positions
                # Use a simple heuristic: if a has larger distance proxy than b, swap to move closer to depot (deterministic)
                pa = next((c.get('distance_to_depot', 0) for c in customers if c['id'] == a), 0)
                pb = next((c.get('distance_to_depot', 0) for c in customers if c['id'] == b), 0)
                if pb < pa:
                    # perform swap
                    rt[i], rt[i+1] = rt[i+1], rt[i]
                    improved = True
            # end for
        return rt

    routes = [_route_swap_improve(rt) for rt in routes]

    # Final: ensure no duplicates and all customers present
    seen = set()
    final_routes = []
    for rt in routes:
        # filter duplicates if any
        filtered = []
        for cid in rt:
            if cid not in seen:
                filtered.append(cid)
                seen.add(cid)
        if filtered:
            final_routes.append(filtered)

    # If any customer missing due to repair, append as singletons (robustness)
    all_ids = set(c['id'] for c in customers)
    missing = all_ids - seen
    for mid in missing:
        final_routes.append([mid])

    return final_routes
