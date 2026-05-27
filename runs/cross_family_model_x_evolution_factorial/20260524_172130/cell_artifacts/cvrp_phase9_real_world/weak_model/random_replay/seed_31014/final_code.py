def solve_cvrp(instance):
    # Unpack the instance
    depot = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['vehicle_capacity']

    # Initialize unvisited customers
    unvisited = set(c['id'] for c in customers)

    # Create a mapping from customer id to customer data for quick access
    customer_map = {c['id']: c for c in customers}

    # List to hold all routes
    routes = []

    # Constructive phase: build routes by greedily selecting nearest customers respecting capacity
    while unvisited:
        route = []
        load = 0
        current_location = depot['location']

        while True:
            # Find the nearest unvisited customer that fits in the remaining capacity
            candidates = []
            for cid in unvisited:
                customer = customer_map[cid]
                demand = customer['demand']
                if load + demand <= vehicle_capacity:
                    # Calculate Euclidean distance
                    dx = customer['location'][0] - current_location[0]
                    dy = customer['location'][1] - current_location[1]
                    dist = (dx * dx + dy * dy) ** 0.5
                    candidates.append((dist, cid))
            if not candidates:
                break
            # Select customer with minimal distance
            candidates.sort()
            _, selected_cid = candidates[0]
            selected_customer = customer_map[selected_cid]
            route.append(selected_cid)
            load += selected_customer['demand']
            current_location = selected_customer['location']
            unvisited.remove(selected_cid)

        # Append built route
        routes.append(route)

    # Local search improvement: attempt to swap customers between routes to reduce total distance
    # For interpretability, perform a simple pairwise swap if it improves total distance
    def total_distance(routes):
        dist = 0
        for route in routes:
            prev_location = depot['location']
            for cid in route:
                customer = customer_map[cid]
                curr_location = customer['location']
                dx = curr_location[0] - prev_location[0]
                dy = curr_location[1] - prev_location[1]
                dist += (dx * dx + dy * dy) ** 0.5
                prev_location = curr_location
            # Return to depot
            dx = depot['location'][0] - prev_location[0]
            dy = depot['location'][1] - prev_location[1]
            dist += (dx * dx + dy * dy) ** 0.5
        return dist

    # Attempt to improve routes by swapping customers between routes
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_a = routes[i]
                route_b = routes[j]
                for idx_a in range(len(route_a)):
                    for idx_b in range(len(route_b)):
                        cID_a = route_a[idx_a]
                        cID_b = route_b[idx_b]
                        c_a = customer_map[cID_a]
                        c_b = customer_map[cID_b]
                        # Check capacity constraints
                        load_a = sum(customer_map[c]['demand'] for c in route_a)
                        load_b = sum(customer_map[c]['demand'] for c in route_b)
                        new_load_a = load_a - c_a['demand'] + c_b['demand']
                        new_load_b = load_b - c_b['demand'] + c_a['demand']
                        if new_load_a <= vehicle_capacity and new_load_b <= vehicle_capacity:
                            # Perform swap
                            new_route_a = route_a[:]
                            new_route_b = route_b[:]
                            new_route_a[idx_a], new_route_b[idx_b] = cID_b, cID_a
                            new_routes = routes[:]
                            new_routes[i] = new_route_a
                            new_routes[j] = new_route_b
                            old_dist = total_distance(routes)
                            new_dist = total_distance(new_routes)
                            if new_dist < old_dist:
                                routes = new_routes
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break
    return routes

