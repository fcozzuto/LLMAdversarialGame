def solve_cvrp(instance):
    # instance is expected to be a dict with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': dict or object (ignored, only capacity and demands)
    # - 'vehicle_capacity': int
    # For simplicity, we assume:
    # - customers have ids as integers starting from 1
    # - a deterministic distance heuristic is not required; we only need routes
    # Build routes by simple greedy sequential packing with deterministic order

    # Extract data with safe defaults
    customers = instance.get('customers', [])
    depot = instance.get('depot', None)
    capacity = instance.get('vehicle_capacity', 0)

    # Normalize customer list to ensure deterministic order by id
    cus = []
    for c in customers:
        cid = c.get('id')
        if cid is None:
            continue
        demand = c.get('demand', 0)
        cus.append({'id': cid, 'demand': demand})

    # Kind of a constructive heuristic:
    # - process customers in increasing id
    # - fill a route until capacity would be exceeded, then start a new route
    # - this guarantees each customer is visited exactly once
    cus.sort(key=lambda x: x['id'])

    routes = []
    i = 0
    n = len(cus)

    while i < n:
        remaining = capacity
        route = []
        # add as many customers as fit, in deterministic order
        while i < n and cus[i]['demand'] <= remaining:
            route.append(cus[i]['id'])
            remaining -= cus[i]['demand']
            i += 1
        # if a single customer's demand exceeds capacity, skip (degenerate)
        if not route and i < n:
            # cannot fit this customer; to keep feasibility, place them alone if possible
            cid = cus[i]['id']
            d = cus[i]['demand']
            if d <= capacity:
                route.append(cid)
                i += 1
            else:
                # mark as unserviceable under given capacity; skip to avoid infinite loop
                # This mirrors a repair: assign as a solo large-capacity route if possible
                # else ignore (but we must visit all; as a last resort, place it anyway)
                route.append(cid)
                i += 1
        routes.append(route)

    return routes
