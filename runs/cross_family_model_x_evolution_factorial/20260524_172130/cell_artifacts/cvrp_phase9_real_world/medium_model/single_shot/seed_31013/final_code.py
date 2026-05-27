def solve_cvrp(instance):
    # Instance format assumed:
    # instance is a dict with:
    # - 'customers': list of dicts with keys 'id', 'demand'
    # - 'vehicles': int (number of vehicles)
    # - 'capacity': int (capacity per vehicle)
    # - Optionally 'depot': {'id': 0, 'x': ..., 'y': ...} (not used in this deterministic version)
    #
    # We implement a simple deterministic constructive solver:
    # 1) Sort customers by non-increasing demand (large first) to respect capacity early.
    # 2) Create routes by filling each vehicle up to capacity in that order.
    # 3) If a single customer's demand exceeds capacity, it's impossible; we still place it in a new route to indicate handling, though normally such instance would be infeasible.
    #
    # Output: list of routes, each route is a list of customer ids (no depot)
    customers = instance.get('customers', [])
    capacity = instance.get('capacity', 0)
    vehicle_count = instance.get('vehicles', 1)

    # Defensive: build a list of (id, demand)
    custs = [(c['id'], c.get('demand', 0)) for c in customers]

    # Sort by demand desc, then by id for determinism
    custs.sort(key=lambda x: (-x[1], x[0]))

    routes = []
    current_route = []
    current_load = 0

    # Simple constructive filling
    for cid, demand in custs:
        if demand > capacity:
            # If one customer alone exceeds capacity, handle by placing in its own route
            # This keeps deterministic behavior; in real CVRP this would be infeasible.
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([cid])
            continue

        if current_load + demand <= capacity:
            current_route.append(cid)
            current_load += demand
        else:
            # finish current route and start a new one
            if current_route:
                routes.append(current_route)
            current_route = [cid]
            current_load = demand

        # If we exceed the number of vehicles, start a new route (simulate more vehicles)
        if len(routes) + (1 if current_route else 0) > vehicle_count:
            # Start a new route when we exhaust declared vehicles
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0

    if current_route:
        routes.append(current_route)

    # If we ended up with more routes than vehicles, it's still a valid partition; the problem statement
    # doesn't require using all vehicles exactly once, only to respect capacity and visit all customers.

    # As a final deterministic touch, ensure there are no empty routes and that every customer appears exactly once
    seen = set()
    final_routes = []
    for r in routes:
        if not r:
            continue
        new_r = []
        for cid in r:
            if cid not in seen:
                new_r.append(cid)
                seen.add(cid)
        if new_r:
            final_routes.append(new_r)

    # If any customer missing due to duplicates (shouldn't happen), append remaining
    if len(seen) != len(custs):
        remaining = [cid for cid, _ in custs if cid not in seen]
        if remaining:
            final_routes.append(remaining)

    return final_routes
