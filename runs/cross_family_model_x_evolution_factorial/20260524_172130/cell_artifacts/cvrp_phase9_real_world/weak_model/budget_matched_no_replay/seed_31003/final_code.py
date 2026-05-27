def solve_cvrp(instance):
    # Extract instance data
    depot = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['vehicle_capacity']
    
    # Copy of customers to be assigned
    unvisited = customers[:]
    
    routes = []

    while unvisited:
        # Start a new route from depot
        current_capacity = vehicle_capacity
        route = []
        current_location = depot

        # Greedily add the closest feasible customer
        while True:
            # Find the closest unvisited customer that fits in remaining capacity
            feasible_customer = None
            min_distance = float('inf')
            for customer in unvisited:
                demand = customer['demand']
                if demand <= current_capacity:
                    dist = abs(current_location['x'] - customer['x']) + abs(current_location['y'] - customer['y'])
                    if dist < min_distance:
                        min_distance = dist
                        feasible_customer = customer
            
            if feasible_customer is None:
                # No feasible customers left for current route
                break
            
            # Add selected customer to route
            route.append(feasible_customer['id'])
            # Update capacity and location
            current_capacity -= feasible_customer['demand']
            current_location = feasible_customer
            # Remove visited customer
            unvisited.remove(feasible_customer)
        
        routes.append(route)
    return routes

