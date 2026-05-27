def solve_cvrp(instance):
    """
    Deterministic CVRP solver with constructive, repair, and local search phases.
    
    Parameters:
    instance: dict with keys:
        - 'depot': int (depot node id)
        - 'customers': list of dicts, each with 'id', 'demand'
        - 'distance_matrix': 2D list or array, indexed by node ids
        
    Returns:
    routes: list of routes, each route is a list of customer ids (excluding depot)
    """
    # Extract data
    depot = instance['depot']
    customers = instance['customers']
    distance_matrix = instance['distance_matrix']
    
    customer_ids = [c['id'] for c in customers]
    demands = {c['id']: c['demand'] for c in customers}
    
    # Initialize list of unvisited customers
    unvisited = set(customer_ids)
    
    # Step 1: Construct initial routes using a greedy nearest neighbor approach
    routes = []
    while unvisited:
        route = []
        load = 0
        current_node = depot
        while True:
            # Find feasible customers from unvisited that can be added
            feasible_customers = [c for c in unvisited if demands[c] + load <= instance['vehicle_capacity']]
            if not feasible_customers:
                break
            # Select the nearest feasible customer
            next_customer = min(feasible_customers, key=lambda c: distance_matrix[current_node][c])
            route.append(next_customer)
            load += demands[next_customer]
            unvisited.remove(next_customer)
            current_node = next_customer
        routes.append(route)
    
    # Step 2: Improve routes with a simple local search—try swapping customers between routes
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_a = routes[i]
                route_b = routes[j]
                for a_idx in range(len(route_a)):
                    for b_idx in range(len(route_b)):
                        cA = route_a[a_idx]
                        cB = route_b[b_idx]
                        # Check capacity constraints if swapped
                        load_a = sum(demands[c] for c in route_a)
                        load_b = sum(demands[c] for c in route_b)
                        new_load_a = load_a - demands[cA] + demands[cB]
                        new_load_b = load_b - demands[cB] + demands[cA]
                        if new_load_a <= instance['vehicle_capacity'] and new_load_b <= instance['vehicle_capacity']:
                            # Calculate current total distance
                            def route_distance(route):
                                dist = distance_matrix[depot][route[0]] if route else 0
                                for k in range(len(route)-1):
                                    dist += distance_matrix[route[k]][route[k+1]]
                                dist += distance_matrix[route[-1]][depot] if route else 0
                                return dist
                            
                            current_total = route_distance(route_a) + route_distance(route_b)
                            # Swap customers
                            new_route_a = route_a[:]
                            new_route_b = route_b[:]
                            new_route_a[a_idx], new_route_b[b_idx] = cB, cA
                            new_total = route_distance(new_route_a) + route_distance(new_route_b)
                            if new_total < current_total:
                                routes[i] = new_route_a
                                routes[j] = new_route_b
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break
    return routes

