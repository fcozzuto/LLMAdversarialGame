def solve_cvrp(instance):
    # Assumptions about instance structure:
    # instance is a dict with:
    # - 'customers': list of dicts with 'id'(int), 'x','y','demand'(int)
    # - 'depot': dict with 'id' (int)
    # - 'vehicle_capacity': int
    # For a minimal deterministic constructive solver, we compute simple nearest-eligible insertion per route.

    customers = list(instance['customers'])
    depot_id = instance['depot']['id']
    capacity = instance['vehicle_capacity']

    # Build distance function (deterministic, integer coordinates)
    def dist(a, b):
        dx = a['x'] - b['x']
        dy = a['y'] - b['y']
        return abs(dx) + abs(dy)

    # Map from id to customer
    by_id = {c['id']: c for c in customers}

    # Start with all customers unassigned (except depot)
    remaining = set(c['id'] for c in customers)

    routes = []

    # Simple greedy constructive: repeatedly form a route by adding the nearest feasible customer to the route end
    # Start a new route from depot (conceptually) and build until capacity would be exceeded.
    # We'll represent route as list of customer ids (excluding depot)
    while remaining:
        # Start new route with empty sequence, current load 0, current last location is depot
        route = []
        current_loc = by_id[depot_id]
        current_load = 0

        # Build route by repeatedly picking the closest remaining customer
        while remaining:
            # Find candidate that fits capacity and is nearest to current_loc
            best_id = None
            best_dist = None
            for cid in remaining:
                c = by_id[cid]
                if current_load + c['demand'] > capacity:
                    continue
                d = dist(current_loc, c)
                if best_dist is None or d < best_dist:
                    best_dist = d
                    best_id = cid

            if best_id is None:
                # No feasible next customer for current route, finish this route
                break

            # Add best_id to route
            route.append(best_id)
            current_load += by_id[best_id]['demand']
            current_loc = by_id[best_id]
            remaining.remove(best_id)

        # If route empty (shouldn't normally happen unless a single customer exceeds capacity), take a single customer
        if not route and remaining:
            cid = next(iter(remaining))
            c = by_id[cid]
            if c['demand'] <= capacity:
                route.append(cid)
                remaining.remove(cid)
            else:
                # Skip unsatisfiable customer (shouldn't happen with valid input)
                remaining.remove(cid)

        routes.append(route)

    return routes
