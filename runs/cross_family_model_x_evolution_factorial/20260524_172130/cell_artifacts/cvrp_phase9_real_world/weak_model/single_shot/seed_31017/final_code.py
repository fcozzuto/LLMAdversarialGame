def solve_cvrp(instance):
    # Unpack instance data
    customers = instance['customers']
    depot = instance['depot']
    vehicle_capacity = instance['vehicle_capacity']
    
    # Initialize unvisited customers
    unvisited = set(c['id'] for c in customers)
    
    # Create a lookup for customer data for quick access
    customer_data = {c['id']: c for c in customers}
    
    routes = []
    
    # Continue until all customers are assigned
    while unvisited:
        current_route = []
        load = 0
        current_location_id = depot['id']
        route_customers = []
        
        # Repeat until no more customers can be added to current route
        while True:
            # Find feasible customers: unvisited, capacity allowed
            feasible_customers = []
            for cid in unvisited:
                cdata = customer_data[cid]
                if load + cdata['demand'] <= vehicle_capacity:
                    feasible_customers.append(cdata)
            if not feasible_customers:
                break
            # Select next customer: closest to current location (deterministic)
            current_location = None
            if current_location_id == depot['id']:
                current_location = depot
            else:
                current_location = customer_data[current_location_id]
            # Find the closest feasible customer
            next_customer = min(
                feasible_customers,
                key=lambda c: ( (c['x'] - current_location['x'])**2 + (c['y'] - current_location['y'])**2 )
            )
            # Add to route
            route_customers.append(next_customer['id'])
            load += next_customer['demand']
            current_location_id = next_customer['id']
            unvisited.remove(next_customer['id'])
        
        # Append the constructed route
        routes.append(route_customers)
    
    return routes

