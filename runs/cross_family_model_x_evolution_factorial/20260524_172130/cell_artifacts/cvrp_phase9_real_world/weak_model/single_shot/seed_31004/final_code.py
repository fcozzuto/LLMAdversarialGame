def solve_cvrp(instance):
    # Extract data from instance
    customers = instance['customers']  # list of dicts: {'id': int, 'x': float, 'y': float, 'demand': float}
    depot = instance['depot']            # dict: {'id': int, 'x': float, 'y': float}
    vehicle_capacity = instance['vehicle_capacity']

    # Prepare customer data excluding depot (assuming depot is not in customers list)
    customer_list = customers

    # Initialize unvisited customers
    unvisited = set(cust['id'] for cust in customer_list)

    # Build a quick lookup for customer info
    customer_dict = {cust['id']: cust for cust in customer_list}

    # Function to compute Euclidean distance
    def distance(a, b):
        dx = a['x'] - b['x']
        dy = a['y'] - b['y']
        return (dx*dx + dy*dy)**0.5

    # Start building routes
    routes = []

    while unvisited:
        route = []
        load = 0.0
        current_location = depot

        # Greedily assign customers to the current route
        while True:
            # Find the closest unvisited customer that fits capacity
            candidates = []
            for cid in unvisited:
                cust = customer_dict[cid]
                if load + cust['demand'] <= vehicle_capacity:
                    dist = distance(current_location, cust)
                    candidates.append((dist, cid))
            if not candidates:
                break
            # Select the closest candidate
            candidates.sort(key=lambda x: x[0])
            next_cust_id = candidates[0][1]
            # Add to route
            route.append(next_cust_id)
            unvisited.remove(next_cust_id)
            load += customer_dict[next_cust_id]['demand']
            current_location = customer_dict[next_cust_id]

        routes.append(route)

    # Optional: Improve routes with intra-route local swaps (simple 2-opt like)
    # For interpretability, limit to a simple heuristic: try swapping adjacent customers to reduce total distance
    def route_distance(route):
        total = 0.0
        prev_location = depot
        for cid in route:
            total += distance(prev_location, customer_dict[cid])
            prev_location = customer_dict[cid]
        total += distance(prev_location, depot)
        return total

    # Apply a single pass of local improvement: attempt to swap adjacent customers if it reduces route distance
    for idx in range(len(routes)):
        route = routes[idx]
        improved = True
        while improved:
            improved = False
            for i in range(len(route) - 1):
                # Swap customers i and i+1
                new_route = route[:]
                new_route[i], new_route[i+1] = new_route[i+1], new_route[i]
                if route_distance(new_route) < route_distance(route):
                    route = new_route
                    improved = True
            routes[idx] = route

    return routes

