def solve_cvrp(instance):
    # instance expected to have keys: 'nodes', 'depot', 'demands', 'vehicle_capacity'
    nodes = instance['nodes']
    depot = instance['depot']
    demands = instance['demands']
    capacity = instance['vehicle_capacity']
    
    # Build list of customer IDs (excluding depot)
    customers = [node for node in nodes if node != depot]
    
    # Initialize unserved customers
    unserved = set(customers)
    
    routes = []
    # Construct routes greedily
    while unserved:
        current_load = 0
        current_route = []
        current_node = depot
        
        # Build route until no customer can be added
        while True:
            # Find feasible customers to add
            feasible_customers = []
            for customer in unserved:
                demand = demands[customer]
                if current_load + demand <= capacity:
                    feasible_customers.append(customer)
            if not feasible_customers:
                break
            # Select next customer (deterministically, smallest ID)
            next_customer = min(feasible_customers)
            # Append to route
            current_route.append(next_customer)
            current_load += demands[next_customer]
            unserved.remove(next_customer)
            current_node = next_customer
        
        routes.append(current_route)
    
    # Now, attempt to improve routes with basic local search
    # For simplicity, we'll try pairwise swaps within routes that improve total distance
    
    # Assume 'edges' in 'instance' could define distances, but since not specified, 
    # we rely on a simple heuristic: in this implementation, distances are not used for improvement,
    # as no distance info provided. To keep the code simple and deterministic,
    # we will skip local improvements.
    
    # Return the built routes
    return routes

