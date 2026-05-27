def solve_cvrp(instance):
    # Extract data from instance
    depot = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['vehicle_capacity']
    
    # Create list of all customer IDs
    customer_ids = [cust['id'] for cust in customers]
    # Map customer id to its info for quick lookup
    customer_map = {cust['id']: cust for cust in customers}
    
    # Initialize routes list
    routes = []
    # Keep track of used customers
    unserved = set(customer_ids)
    
    # Function to compute distance between two points
    def dist(a, b):
        return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5
    
    # Build a simple initial route using a greedy approach
    while unserved:
        route = []
        load = 0
        current_loc = (depot['x'], depot['y'])
        current_id = None
        # Start at depot
        start_loc = (depot['x'], depot['y'])
        while True:
            # Find closest unserved customer that fits capacity
            candidates = []
            for cid in unserved:
                c = customer_map[cid]
                # Check if demand fits remaining capacity
                if load + c['demand'] <= vehicle_capacity:
                    distance = dist(current_loc, (c['x'], c['y']))
                    candidates.append((distance, cid))
            if not candidates:
                # No suitable candidates, end this route
                break
            # Choose the closest customer
            candidates.sort(key=lambda x: x[0])
            next_cid = candidates[0][1]
            c = customer_map[next_cid]
            # Append customer to route
            route.append(next_cid)
            # Update load and location
            load += c['demand']
            current_loc = (c['x'], c['y'])
            # Mark customer as served
            unserved.remove(next_cid)
        # Save the constructed route
        routes.append(route)
    return routes

