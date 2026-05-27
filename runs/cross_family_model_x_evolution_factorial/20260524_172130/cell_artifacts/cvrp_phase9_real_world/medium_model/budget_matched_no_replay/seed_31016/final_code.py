def solve_cvrp(instance):
    # Assumptions about instance structure:
    # instance is a dict with keys:
    #  - 'customers': list of dicts with 'id', 'demand' (int), 'x','y' (optional)
    #  - 'vehicle_capacity': int
    # If keys are different, adapt minimally.
    customers = []
    depot_id = None

    # Normalize input
    if isinstance(instance, dict):
        if 'customers' in instance:
            customers = list(instance['customers'])
        elif 'nodes' in instance:
            customers = list(instance['nodes'])
        else:
            # construct from a flat structure if provided
            customers = []
            for k, v in instance.items():
                if isinstance(v, dict) and 'id' in v:
                    customers.append(v)
        vehicle_capacity = instance.get('vehicle_capacity', None)
        depot_id = instance.get('depot', None)
    else:
        # If not dict, cannot proceed
        return []

    # Ensure we have required fields
    # Build a simple structure: id -> demand
    custs = []
    for c in customers:
        cid = c.get('id', None)
        d = c.get('demand', 0)
        if cid is None:
            continue
        custs.append({'id': cid, 'demand': int(d)})

    if vehicle_capacity is None:
        # Fallback to sum of demands to avoid zero
        total_demand = sum(c['demand'] for c in custs)
        vehicle_capacity = max(1, int(total_demand // max(1, (len(custs) // 3 + 1))))

    # Simple deterministic heuristic:
    # 1) Sort customers by id (stable)
    # 2) Construct routes greedily by adding next unvisited customer if capacity allows
    # 3) If next customer exceeds capacity, start a new route
    # This is constructive and deterministic.

    custs_sorted = sorted(custs, key=lambda c: c['id'])

    routes = []
    current_route = []
    current_load = 0

    for c in custs_sorted:
        d = c['demand']
        if d > vehicle_capacity:
            # A single customer heavier than a vehicle; create an empty route attempt
            # Still assign as its own route to satisfy constraint
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([c['id']])
            continue

        if current_load + d <= vehicle_capacity:
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

    # If any route empty (shouldn't), remove
    routes = [r for r in routes if r]

    # Return as list of lists of ids
    return routes
