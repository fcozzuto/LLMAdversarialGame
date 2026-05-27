def solve_cvrp(instance):
    # instance is expected to be a dict with:
    # - 'depot': depot_id
    # - 'customers': list of dicts with keys 'id', 'demand'
    # - 'vehicle_capacity': int or float
    # For simplicity, we assume a complete graph with distances defined as Euclidean by coordinates if provided.
    # To remain self-contained and deterministic without imports, we implement a simple constructive clustering:
    depot = instance['depot']
    customers = list(instance['customers'])
    capacity = instance['vehicle_capacity']

    # If coordinates are provided, we can compute a simple distance; otherwise ignore distance and use a deterministic order.
    # Prepare a map for quick access
    idx = {c['id']: c for c in customers}

    # Sort customers deterministically by id to ensure reproducibility
    customers.sort(key=lambda c: c['id'])

    # Simple constructive algorithm:
    # - Create routes by filling each route until capacity would be exceeded.
    # - Start a new route when adding the next customer would exceed capacity.
    # - Each route is a list of customer ids (excluding depot).
    routes = []
    current_route = []
    current_load = 0

    for c in customers:
        dem = c['demand']
        if dem > capacity:
            # If a single customer exceeds capacity, create a dedicated route (cannot be served), but to keep feasibility we skip.
            # In a strict CVRP, this should be handled; here we place the customer alone if possible and continue.
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([c['id']])
            current_route = []
            current_load = 0
            continue

        if current_load + dem <= capacity:
            current_route.append(c['id'])
            current_load += dem
        else:
            # finalize current route and start new one
            if current_route:
                routes.append(current_route)
            current_route = [c['id']]
            current_load = dem

    if current_route:
        routes.append(current_route)

    # Deterministic repair: ensure no route is empty and every customer appears exactly once
    seen = set()
    final_routes = []
    for r in routes:
        # remove potential duplicates (defensive)
        new_r = []
        for cid in r:
            if cid not in seen:
                new_r.append(cid)
                seen.add(cid)
        if new_r:
            final_routes.append(new_r)

    # If some customers missing due to a logic error, append them at the end (defensive)
    if len(seen) < len(customers):
        missing = [c['id'] for c in customers if c['id'] not in seen]
        if not final_routes:
            final_routes = [missing]
        else:
            final_routes[-1].extend(missing)

    # Ensure every customer appears exactly once
    all_ids = [c['id'] for c in customers]
    id_count = {i: 0 for i in all_ids}
    for r in final_routes:
        for cid in r:
            id_count[cid] = id_count.get(cid, 0) + 1

    # If any id_count != 1, fix by distributing
    for cid in all_ids:
        if id_count.get(cid, 0) != 1:
            # remove duplicates from routes
            for r in final_routes:
                while cid in r:
                    r.remove(cid)
            # place exactly once in the first route
            placed = False
            for r in final_routes:
                if sum(1 for x in r if x is not None) == 0:
                    r.append(cid)
                    placed = True
                    break
            if not placed:
                final_routes.append([cid])

    return final_routes
