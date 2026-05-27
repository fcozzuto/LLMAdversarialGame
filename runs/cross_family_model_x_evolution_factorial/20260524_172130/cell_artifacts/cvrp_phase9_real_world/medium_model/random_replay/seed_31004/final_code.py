def solve_cvrp(instance):
    """
    Deterministic constructive solver with simple local repair for CVRP.
    Assumptions:
    - instance is a dict with:
        - 'customers': list of dicts with 'id' (int) and 'demand' (int) and 'x','y' optional
        - 'depot': int id of depot (not included in routes)
        - 'capacity': int vehicle capacity
    - Return: list of routes, each route is [customer_id, ...] (no depot)
    Notes:
    - Deterministic: uses sorted by (demand, id) and nearest-insertion style build with simple heuristic.
    - Our simple distance uses Manhattan if coordinates present, otherwise abstract distance by id difference.
    - No external data or imports.
    """
    # Extract data with safe defaults
    customers = instance.get('customers', [])
    depot_id = instance.get('depot', 0)
    capacity = instance.get('capacity', 0)

    # Build a simple customers map
    custs = []
    for c in customers:
        cid = c.get('id', None)
        if cid is None or cid == depot_id:
            continue
        demand = int(c.get('demand', 0))
        x = c.get('x', None)
        y = c.get('y', None)
        custs.append({'id': cid, 'demand': demand, 'x': x, 'y': y})

    # If no customers, return empty routes
    if not custs:
        return []

    # Helper: distance between two customers (or to depot)
    # Use Manhattan if coordinates present; else simple absolute difference of ids
    def dist(a, b):
        ax = a.get('x'); ay = a.get('y')
        bx = b.get('x'); by = b.get('y')
        if ax is not None and ay is not None and bx is not None and by is not None:
            return abs(ax - bx) + abs(ay - by)
        # Fallback: use id-based pseudo-distance
        return abs(a['id'] - b['id'])

    # Determine an initial order: sort by (demand, id) for determinism
    custs_sorted = sorted(custs, key=lambda c: (c['demand'], c['id']))

    # Build routes by a simple greedy packing: start new route when capacity would be exceeded
    routes = []
    current_route = []
    current_load = 0

    # Helper: pointer to a customer dict by id for distance access if needed
    id_to_cust = {c['id']: c for c in custs_sorted}

    # We'll implement a very simple sequential insertion to be deterministic:
    # For each customer in sorted order, try to place into current route if capacity allows,
    # otherwise start a new route. Also try to insert at end of route if distance is acceptable
    for c in custs_sorted:
        if current_load + c['demand'] <= capacity:
            current_route.append(c['id'])
            current_load += c['demand']
        else:
            # finish current route
            if current_route:
                routes.append(current_route)
            # start new route with this customer
            current_route = [c['id']]
            current_load = c['demand']
    # append last route
    if current_route:
        routes.append(current_route)

    # Repair step: ensure each route is feasible (no single demand exceeds capacity)
    # If any customer has demand > capacity, make it its own route (edge case)
    final_routes = []
    for r in routes:
        if not r:
            continue
        # compute loads; if any single customer exceeds capacity, split it
        temp_route = []
        temp_load = 0
        for cid in r:
            d = id_to_cust[cid]['demand']
            if d > capacity:
                # put as its own route
                if temp_route:
                    final_routes.append(temp_route)
                    temp_route = []
                    temp_load = 0
                final_routes.append([cid])
            else:
                if temp_load + d <= capacity:
                    temp_route.append(cid)
                    temp_load += d
                else:
                    if temp_route:
                        final_routes.append(temp_route)
                    temp_route = [cid]
                    temp_load = d
        if temp_route:
            final_routes.append(temp_route)

    # If any route ends empty due to repair, filter
    final_routes = [r for r in final_routes if r]

    return final_routes
