def solve_cvrp(instance):
    # instance is expected to be a dict with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id of depot (not used in routes)
    # - 'vehicles': int number of vehicles
    # - 'capacity': int capacity per vehicle
    # This is a deterministic constructive solver with simple repair/local steps.

    # Prepare data
    customers = [c for c in instance.get('customers', [])]
    depot_id = instance.get('depot', None)
    vehicle_count = int(instance.get('vehicles', 1))
    capacity = int(instance.get('capacity', 0))
    if capacity <= 0:
        # Fallback: sum of all demands and split evenly
        capacity = max(1, sum(c['demand'] for c in customers) // max(1, vehicle_count))

    # Sort customers by a simple heuristic: demand/priority balance using id as tiebreaker
    # We want deterministic order: sort by id
    customers_sorted = sorted(customers, key=lambda c: c['id'])

    # Helper: build initial routes by packing sequentially until capacity filled
    routes = []
    current_route = []
    current_load = 0

    for c in customers_sorted:
        d = int(c['demand'])
        if d > capacity:
            # If a single customer exceeds capacity, create a dedicated route for it
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([c['id']])
            continue

        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            # finish current route and start a new one
            routes.append(current_route)
            current_route = [c['id']]
            current_load = d

    if current_route:
        routes.append(current_route)

    # If we have more routes than vehicles, merge greedily (deterministic repair)
    # Merge the last route into previous ones until count <= vehicle_count
    while len(routes) > vehicle_count:
        # take the last route and append its customers to previous route
        last = routes.pop()
        if not routes:
            routes.append(last)
            break
        routes[-1].extend(last)

    # If we have fewer routes than vehicles, we can split some routes to utilize all vehicles
    # Split the largest routes if needed to reach at most vehicle_count (or exactly)
    while len(routes) < vehicle_count:
        # find a route with length > 1 to split
        split_done = False
        for i, r in enumerate(routes):
            if len(r) >= 2:
                mid = len(r) // 2
                r1 = r[:mid]
                r2 = r[mid:]
                routes[i] = r1
                routes.insert(i+1, r2)
                split_done = True
                break
        if not split_done:
            break  # cannot split further

    # Final pass: ensure no route exceeds capacity (by construction, should be OK)
    final_routes = []
    for r in routes:
        load = sum(next(c['demand'] for c in customers if c['id'] == cid) for cid in r)
        if load <= capacity:
            final_routes.append(list(r))
        else:
            # As a last resort, split this route into individual customer routes
            for cid in r:
                final_routes.append([cid])

    # Ensure deterministic ordering within each route by id order
    final_routes = [sorted(r) for r in final_routes]

    return final_routes
