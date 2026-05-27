def solve_cvrp(instance):
    # Instance is a dict with 'depot', 'customers' (list of dicts with 'id', 'x', 'y', 'demand'), 
    # 'vehicle_capacity'
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Create a list of customers with their attributes
    customer_list = [dict(c) for c in customers]
    # Initialize set of unvisited customers
    unvisited = set(c['id'] for c in customer_list)
    # Map customer id to customer data for quick lookup
    customer_map = {c['id']: c for c in customer_list}
    # Initialize list of routes
    routes = []
    
    # Define a function to compute Euclidean distance
    def dist(a, b):
        return ((a['x'] - b['x'])**2 + (a['y'] - b['y'])**2)**0.5
    
    # Continue until all customers are assigned
    while unvisited:
        route = []
        load = 0
        current_node = depot
        # Build route greedily
        while True:
            # Find feasible customers: unvisited and demand fits
            feasible_customers = [cid for cid in unvisited if 
                                  customer_map[cid]['demand'] + load <= capacity]
            if not feasible_customers:
                # No more feasible customers in this route
                break
            # Select the nearest customer among feasible
            next_cid = min(feasible_customers, key=lambda cid: dist(current_node, customer_map[cid]))
            route.append(next_cid)
            load += customer_map[next_cid]['demand']
            current_node = customer_map[next_cid]
            unvisited.remove(next_cid)
        routes.append(route)
    return routes

