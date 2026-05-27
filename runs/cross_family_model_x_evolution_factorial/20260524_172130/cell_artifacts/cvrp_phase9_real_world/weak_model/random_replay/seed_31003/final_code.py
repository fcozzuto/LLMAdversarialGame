def solve_cvrp(instance):
    """
    Construct a deterministic CVRP solution using a simple heuristic:
    1. Initialize unvisited customers.
    2. Build routes greedily by adding nearest feasible customers until capacity exhausted.
    3. Repeat until all customers are served.
    """
    # Parse the instance
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['capacity']
    
    # Initialize unvisited customers: list of (id, demand, x, y)
    unvisited = [
        (idx, cust['demand'], cust['x'], cust['y'])
        for idx, cust in enumerate(customers, start=1)
    ]
    
    routes = []
    
    while unvisited:
        route = []
        load = 0
        current_x, current_y = depot['x'], depot['y']
        remaining = unvisited.copy()
        
        while True:
            # Find feasible customers: those with demand that fits in remaining capacity
            feasible_customers = [
                (cust_id, demand, x, y) for (cust_id, demand, x, y) in remaining
                if demand + load <= capacity
            ]
            if not feasible_customers:
                break  # no more feasible customers, finish this route

            # Choose the closest feasible customer
            min_dist = None
            next_customer = None
            for cust_id, demand, x, y in feasible_customers:
                dist = (x - current_x)**2 + (y - current_y)**2  # squared Euclidean for efficiency
                if (min_dist is None) or (dist < min_dist):
                    min_dist = dist
                    next_customer = (cust_id, demand, x, y)

            # Add the chosen customer to the route
            cust_id, demand, x, y = next_customer
            route.append(cust_id)
            load += demand
            current_x, current_y = x, y
            
            # Remove from unvisited
            for idx, item in enumerate(remaining):
                if item[0] == cust_id:
                    del remaining[idx]
                    break
                    
        # Append the route
        routes.append(route)
        # Update unvisited
        unvisited = remaining

    return routes

