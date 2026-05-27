def solve_cvrp(instance):
    """
    Constructive, interpretable CVRP solver following a deterministic, single-shot approach.
    Builds initial routes greedily and refines by local swaps to improve feasibility and compactness.
    """
    # Parse input instance
    customers = instance['customers']
    depot = instance['depot']
    vehicle_capacity = instance['vehicle_capacity']
    
    # Initialize data structures
    # Each customer: {'id': int, 'x': float, 'y': float, 'demand': float}
    unvisited = set(c['id'] for c in customers)
    
    # Helper functions
    def distance(c1, c2):
        if c1 == 'depot':
            x1, y1 = depot['x'], depot['y']
        else:
            x1, y1 = next(c for c in customers if c['id'] == c1)['x'], next(c for c in customers if c['id'] == c1)['y']
        if c2 == 'depot':
            x2, y2 = depot['x'], depot['y']
        else:
            x2, y2 = next(c for c in customers if c['id'] == c2)['x'], next(c for c in customers if c['id'] == c2)['y']
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5

    def select_next(current, remaining_customers, load):
        # Select the nearest unvisited customer that fits capacity
        candidates = []
        for c_id in remaining_customers:
            c = next(c for c in customers if c['id'] == c_id)
            if c['demand'] <= load:
                dist = distance(current, c_id)
                candidates.append((dist, c_id))
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    # Build initial routes
    routes = []
    while unvisited:
        route = []
        load = 0
        current = 'depot'
        while True:
            next_customer = select_next(current, unvisited, vehicle_capacity - load)
            if next_customer is None:
                break
            c = next(cust for cust in customers if cust['id'] == next_customer)
            route.append(c['id'])
            load += c['demand']
            unvisited.remove(c['id'])
            current = c['id']
        routes.append(route)

    # Local improvement: attempt to swap adjacent customers within routes to reduce total distance
    def improve_route(route):
        improved = True
        while improved:
            improved = False
            for i in range(len(route) - 1):
                # Swap customers i and i+1
                new_route = route[:]
                new_route[i], new_route[i+1] = new_route[i+1], new_route[i]
                # Check if swap reduces total distance
                def route_distance(r):
                    total = 0
                    prev = 'depot'
                    for cust_id in r:
                        c = next(c for c in customers if c['id'] == cust_id)
                        total += distance(prev, c['id'])
                        prev = c['id']
                    total += distance(prev, 'depot')
                    return total
                if route_distance(new_route) < route_distance(route):
                    route = new_route
                    improved = True
        return route

    # Apply local improvements
    routes = [improve_route(r) for r in routes]

    return routes

