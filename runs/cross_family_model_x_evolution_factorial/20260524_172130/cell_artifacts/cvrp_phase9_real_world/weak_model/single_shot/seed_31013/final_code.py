def solve_cvrp(instance):
    # instance is a dictionary with keys:
    # 'customers': list of dicts with 'id', 'demand', 'x', 'y'
    # 'depot': dict with 'id', 'x', 'y'
    # 'vehicle_capacity': number
    
    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']
    
    # Prepare customer list
    customer_list = [c for c in customers]
    unvisited = set(c['id'] for c in customer_list)
    
    # Build a quick lookup for customer data
    customer_dict = {c['id']: c for c in customer_list}
    
    routes = []
    
    # While there are unvisited customers
    while unvisited:
        route = []
        load = 0
        current_x, current_y = depot['x'], depot['y']
        
        # Create a list of remaining customers
        remaining_customers = list(unvisited)
        
        # Initialize a local list for case when no customer can be added
        while True:
            # Find the customer closest to current location that can be served
            min_dist = None
            next_customer_id = None
            for cid in remaining_customers:
                c = customer_dict[cid]
                if load + c['demand'] <= capacity:
                    dist = ( (c['x'] - current_x)**2 + (c['y'] - current_y)**2 )**0.5
                    if (min_dist is None) or (dist < min_dist):
                        min_dist = dist
                        next_customer_id = cid
            # If no suitable customer, end this route
            if next_customer_id is None:
                break
            # Add this customer to route
            c = customer_dict[next_customer_id]
            route.append(c['id'])
            load += c['demand']
            current_x, current_y = c['x'], c['y']
            unvisited.remove(next_customer_id)
            remaining_customers.remove(next_customer_id)
        routes.append(route)
    return routes

