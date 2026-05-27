def solve_cvrp(instance):
    # Instance is assumed to be a dictionary with keys:
    # 'depot': integer representing depot node ID
    # 'demands': dict {node_id: demand}
    # 'distances': dict {(node1, node2): distance}
    # 'vehicle_capacity': integer
    # 'customers': list of customer node IDs (excluding depot)
    
    depot = instance['depot']
    demands = instance['demands']
    distances = instance['distances']
    vehicle_capacity = instance['vehicle_capacity']
    customers = instance['customers']
    
    # Initialize list to hold final routes
    routes = []
    
    # Keep track of unvisited customers
    unvisited = set(customers)
    
    while unvisited:
        route = []
        remaining_capacity = vehicle_capacity
        current_location = depot
        
        # Build route greedily by selecting the closest feasible customer
        while True:
            # Filter customers that can be served with current remaining capacity
            feasible_customers = [
                node for node in unvisited
                if demands[node] <= remaining_capacity
            ]
            if not feasible_customers:
                break
            # Find the nearest feasible customer
            next_customer = min(
                feasible_customers,
                key=lambda node: distances.get((current_location, node), float('inf'))
            )
            # Append customer to route
            route.append(next_customer)
            unvisited.remove(next_customer)
            remaining_capacity -= demands[next_customer]
            current_location = next_customer
        
        # Add the completed route to the routes list
        routes.append(route)
    
    return routes

