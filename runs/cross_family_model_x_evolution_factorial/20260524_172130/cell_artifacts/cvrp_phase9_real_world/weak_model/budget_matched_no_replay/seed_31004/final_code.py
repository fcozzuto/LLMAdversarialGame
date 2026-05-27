def solve_cvrp(instance):
    # Assuming instance is a dictionary with keys:
    # 'depot': depot id (int)
    # 'customers': list of customer dicts, each with 'id', 'demand', 'x', 'y'
    # 'vehicle_capacity': int
    
    depot_id = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Create a list of customers excluding depot
    unvisited = customers.copy()
    # Sort customers by demand for a simple selection heuristic
    unvisited.sort(key=lambda c: c['demand'])
    
    routes = []
    
    while unvisited:
        capacity_remaining = capacity
        route = []
        # Build a route by selecting customers greedily
        i = 0
        while i < len(unvisited):
            customer = unvisited[i]
            demand = customer['demand']
            if demand <= capacity_remaining:
                # Add customer to route
                route.append(customer['id'])
                capacity_remaining -= demand
                # Remove from unvisited
                unvisited.pop(i)
            else:
                i += 1
        # Append the constructed route
        routes.append(route)
    
    # Improve routes using a simple local improvement:
    # For each route, attempt to swap adjacent customers if it reduces total route length (not computed here for simplicity)
    # For interpretability, perform a simple intra-route reordering based on proximity
    for idx, route in enumerate(routes):
        if len(route) > 1:
            # Get customer coordinates
            route_customers = [next(c for c in customers if c['id'] == cid) for cid in route]
            # Perform a simple greedy reordering: start at first customer, always go to the nearest unvisited customer
            ordered = [route_customers[0]]
            unvisited_customers = route_customers[1:]
            while unvisited_customers:
                last = ordered[-1]
                # Find nearest customer
                next_cust = min(unvisited_customers,
                                key=lambda c: (c['x'] - last['x'])**2 + (c['y'] - last['y'])**2)
                ordered.append(next_cust)
                unvisited_customers.remove(next_cust)
            # Update route with reordered customer ids
            routes[idx] = [c['id'] for c in ordered]
    
    return routes

