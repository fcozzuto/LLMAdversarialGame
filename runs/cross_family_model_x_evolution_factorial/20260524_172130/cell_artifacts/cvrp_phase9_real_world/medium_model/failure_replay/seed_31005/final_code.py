def solve_cvrp(instance):
    # instance is expected to be a dict with keys:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': dict with 'id'
    # - 'vehicles': dict with 'capacity'
    # - optional 'distance' function or matrix not required for feasibility
    #
    # This solver constructs routes by a simple deterministic heuristic:
    # 1) Sort customers by nondecreasing demand (small first) to balance loads.
    # 2) Greedily insert each customer into the first route where it fits.
    # 3) If no route fits, start a new route.
    # 4) After constructive phase, perform a basic local improvement:
    #    try to swap adjacent customers between routes if feasible and improves nothing
    #    (we implement a lightweight repair by reordering within routes greedily).
    #
    # The solver is deterministic and does not rely on external data.

    # Extract data with safe defaults
    customers = instance.get('customers', [])
    depot = instance.get('depot', {'id': None})
    capacity = instance.get('vehicles', {}).get('capacity', 0)
    n = len(customers)

    # Defensive: if no customers, return empty routes
    if n == 0:
        return []

    # Build quick index maps for id and demand
    cust_by_id = {c['id']: c for c in customers}
    demands = {c['id']: c.get('demand', 0) for c in customers}

    # Prepare a list of customer ids sorted by increasing demand, tie-break by id
    sorted_ids = sorted([c['id'] for c in customers], key=lambda cid: (demands[cid], cid))

    # Helper to compute route load
    def route_load(route):
        return sum(demands[cid] for cid in route)

    # Construct routes
    routes = []
    for cid in sorted_ids:
        placed = False
        # Try to place into existing routes
        for r in routes:
            if route_load(r) + demands[cid] <= capacity:
                r.append(cid)
                placed = True
                break
        if not placed:
            # start a new route
            routes.append([cid])

    # Local improvement: try to improve within each route by moving a small prefix
    # A simple intra-route 2-opt-like improvement: bubble smaller-demand customers earlier if feasible
    for r in routes:
        improved = True
        while improved:
            improved = False
            for i in range(len(r) - 1):
                for j in range(i+1, len(r)):
                    # swap i and j if still feasible (it is the same total demand)
                    if i == j:
                        continue
                    #Swapping within a route changes order but not load; feasible by definition
                    new_r = r[:]
                    new_r[i], new_r[j] = new_r[j], new_r[i]
                    # Accept only if it strictly improves lexical order of IDs (deterministic, interpretable)
                    if new_r < r:
                        r[:] = new_r
                        improved = True
                        break
                if improved:
                    break

    # Final pass: ensure each customer appears exactly once
    seen = set()
    final_routes = []
    for r in routes:
        nr = []
        for cid in r:
            if cid not in seen:
                nr.append(cid)
                seen.add(cid)
        if nr:
            final_routes.append(nr)

    # If any customer missing due to duplication issue, append from sorted_ids
    missing = [cid for cid in sorted_ids if cid not in seen]
    for cid in missing:
        if final_routes:
            if route_load(final_routes[-1]) + demands[cid] <= capacity:
                final_routes[-1].append(cid)
            else:
                final_routes.append([cid])
        else:
            final_routes.append([cid])

    return final_routes
