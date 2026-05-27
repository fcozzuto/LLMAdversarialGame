def solve_cvrp(instance):
    # instance expected to have:
    # - 'demands': dict or list of customer demands, indexed by customer id
    # - 'locations': dict or list of customer locations, indexed by customer id
    # - 'vehicle_capacity': maximum capacity for each vehicle
    # - 'depot': customer id of the depot
    # Customers are numbered, with depot as a special node.
    
    # Extract problem data
    demands = instance['demands']
    locations = instance['locations']
    vehicle_capacity = instance['vehicle_capacity']
    depot = instance['depot']
    
    # Prepare list of customer ids excluding depot
    customer_ids = [c for c in demands if c != depot]
    
    # Initialize unvisited customers set
    unvisited = set(customer_ids)
    
    # List to store all routes (excluding depot at start/end)
    routes = []
    
    while unvisited:
        current_load = 0
        current_route = []
        current_location = depot
        
        # Build a route greedily based on nearest customer heuristic
        while True:
            # Find the next customer to visit
            # Condition: customer unvisited and demand fits in remaining capacity
            candidates = [
                c for c in unvisited
                if demands[c] + current_load <= vehicle_capacity
            ]
            if not candidates:
                # No more candidates can be added to current route
                break
            
            # Pick the nearest candidate to current_location
            nearest_customer = None
            min_distance = float('inf')
            for c in candidates:
                loc_c = locations[c]
                loc_curr = locations[current_location]
                dist = ((loc_c[0] - loc_curr[0])**2 + (loc_c[1] - loc_curr[1])**2)**0.5
                if dist < min_distance:
                    min_distance = dist
                    nearest_customer = c
            
            # Add the selected customer to current route
            current_route.append(nearest_customer)
            current_load += demands[nearest_customer]
            unvisited.remove(nearest_customer)
            current_location = locations[nearest_customer]
        
        # After constructing one route, append it to routes list
        routes.append(current_route)
    
    return routes

