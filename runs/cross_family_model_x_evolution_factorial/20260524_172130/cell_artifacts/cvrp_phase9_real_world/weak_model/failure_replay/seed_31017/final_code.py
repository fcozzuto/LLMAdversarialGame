def solve_cvrp(instance):
    # Extract instance data
    depot = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['vehicle_capacity']
    
    # Prepare customer data: each customer as (id, demand, x, y)
    customer_list = []
    for cust_id, demand, x, y in customers:
        customer_list.append({'id': cust_id, 'demand': demand, 'x': x, 'y': y})
        
    # Initialize list of routes
    routes = []
    
    # Keep track of unassigned customers
    unassigned = customer_list.copy()
    
    # While there are still customers to assign
    while unassigned:
        # Start a new route from depot
        route = []
        remaining_capacity = vehicle_capacity
        current_x, current_y = depot['x'], depot['y']
        route_customers = []
        
        # Sort unassigned customers by proximity to the current location
        unassigned.sort(key=lambda c: (c['x'] - current_x)**2 + (c['y'] - current_y)**2)
        
        # For each customer, in order
        for customer in unassigned:
            demand = customer['demand']
            if demand <= remaining_capacity:
                # Assign to current route
                route.append(customer['id'])
                remaining_capacity -= demand
                current_x, current_y = customer['x'], customer['y']
                route_customers.append(customer)
        
        # Remove assigned customers from unassigned list
        for customer in route_customers:
            unassigned.remove(customer)
        
        # Append the constructed route
        routes.append(route)
        
    # Return list of routes (excluding depot, which is implicit)
    return routes

