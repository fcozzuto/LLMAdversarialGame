def solve_cvrp(instance):
    # Instance data: 
    # instance['depot']: depot id
    # instance['customers']: list of dicts with keys 'id', 'demand', 'x', 'y'
    # instance['vehicle_capacity']: maximum load per vehicle
    
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    depot_id = instance['depot']
    
    # Create a mapping from customer id to customer data
    customer_map = {cust['id']: cust for cust in customers}
    
    # Build a list of customers to service
    remaining_customers = customers[:]
    
    routes = []
    
    while remaining_customers:
        current_load = 0
        route = []
        current_location = depot_id
        
        # Greedily add customers to the current route
        while remaining_customers:
            # Select the next customer based on nearest neighbor heuristic
            # from current_location
            min_dist = None
            next_customer = None
            for cust in remaining_customers:
                # Get coordinates
                if current_location == depot_id:
                    loc_x, loc_y = 0, 0
                else:
                    loc_x, loc_y = customer_map[current_location]['x'], customer_map[current_location]['y']
                cust_x, cust_y = cust['x'], cust['y']
                dist = (loc_x - cust_x)**2 + (loc_y - cust_y)**2  # squared Euclidean distance for determinism
                if (min_dist is None) or (dist < min_dist):
                    min_dist = dist
                    next_customer = cust
            # Check capacity constraint
            if current_load + next_customer['demand'] <= capacity:
                # Add customer to route
                route.append(next_customer['id'])
                current_load += next_customer['demand']
                current_location = next_customer['id']
                remaining_customers.remove(next_customer)
            else:
                # Can't add more customers to this route
                break
        routes.append(route)
    
    # Optional local optimization: try to improve routes by swapping customers between routes
    # For simplicity and determinism, skip complex swaps.
    # Return the constructed routes
    return routes

