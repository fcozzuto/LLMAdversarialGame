def solve_cvrp(instance):
    # Extract problem data
    depot = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['vehicle_capacity']
    
    # Create a list of unserved customers
    unserved = customers.copy()
    
    routes = []
    
    while unserved:
        route = []
        load = 0
        current_node = depot
        # While there are remaining customers and capacity allows
        while True:
            # Find the nearest feasible customer not yet served
            feasible_candidates = [
                c for c in unserved
                if load + c['demand'] <= vehicle_capacity
            ]
            if not feasible_candidates:
                break
            # Select the candidate with minimum distance from current_node
            next_customer = min(
                feasible_candidates,
                key=lambda c: (
                    # Calculate distance from current_node to candidate
                    ((current_node['x'] - c['x']) ** 2 + (current_node['y'] - c['y']) ** 2) ** 0.5
                )
            )
            # Add chosen customer to route
            route.append(next_customer['id'])
            load += next_customer['demand']
            # Move current_node to the chosen customer
            current_node = next_customer
            # Remove served customer
            unserved.remove(next_customer)
        # Append constructed route
        routes.append(route)
    return routes

