def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) using a deterministic,
    interpretable construction and local-search heuristic.
    
    Args:
        instance (dict): A dictionary with keys:
            - 'customers': List of customer demands, indexed from 0 to n-1.
            - 'depot': Index of the depot (assumed to be 0).
            - 'coordinates': List of (x, y) tuples for each node including depot.
            - 'vehicle_capacity': Capacity of each vehicle.
    
    Returns:
        List of routes, each route is a list of customer indices (excluding depot).
    """
    customers = instance['customers']
    depot_index = instance['depot']
    coordinates = instance['coordinates']
    capacity = instance['vehicle_capacity']
    
    n_customers = len(customers)
    customer_ids = list(range(n_customers))
    
    # Compute Euclidean distance between two nodes
    def dist(i, j):
        dx = coordinates[i][0] - coordinates[j][0]
        dy = coordinates[i][1] - coordinates[j][1]
        return (dx*dx + dy*dy) ** 0.5
    
    # Prepare list of unvisited customers
    unvisited = set(customer_ids)
    
    # Initialize list to hold routes
    routes = []
    
    # While there are unvisited customers, build a route
    while unvisited:
        # Start a new route from the depot
        route = []
        load = 0
        current_node = depot_index
        
        # Greedily insert the nearest feasible customer
        while True:
            # Find feasible customers
            feasible_customers = [
                c for c in unvisited
                if load + customers[c] <= capacity
            ]
            if not feasible_customers:
                break
            # Select the customer with minimal distance to current node
            next_customer = min(
                feasible_customers,
                key=lambda c: dist(current_node, c)
            )
            # Add customer to route
            route.append(next_customer)
            load += customers[next_customer]
            unvisited.remove(next_customer)
            current_node = next_customer
        
        routes.append(route)
    
    # Improve routes locally: try to exchange customers between routes
    improved = True
    while improved:
        improved = False
        # For each pair of routes, attempt a swap
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                # Check all pairs of customers between the two routes for beneficial swaps
                for c_idx_i, c_i in enumerate(route_i):
                    for c_idx_j, c_j in enumerate(route_j):
                        demand_i = customers[c_i]
                        demand_j = customers[c_j]
                        load_i = sum(customers[c] for c in route_i)
                        load_j = sum(customers[c] for c in route_j)
                        # Check if swap respects capacity constraints
                        new_load_i = load_i - demand_i + demand_j
                        new_load_j = load_j - demand_j + demand_i
                        if new_load_i <= capacity and new_load_j <= capacity:
                            # Calculate current total distance
                            def route_distance(route):
                                total = 0.0
                                prev = depot_index
                                for c in route:
                                    total += dist(prev, c)
                                    prev = c
                                total += dist(prev, depot_index)
                                return total
                            current_total = route_distance(route_i) + route_distance(route_j)
                            # Swap customers
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[c_idx_i] = c_j
                            new_route_j[c_idx_j] = c_i
                            new_total = route_distance(new_route_i) + route_distance(new_route_j)
                            if new_total < current_total:
                                # Accept the swap
                                routes[i] = new_route_i
                                routes[j] = new_route_j
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break
        # Loop continues until no improvement
    
    return routes

