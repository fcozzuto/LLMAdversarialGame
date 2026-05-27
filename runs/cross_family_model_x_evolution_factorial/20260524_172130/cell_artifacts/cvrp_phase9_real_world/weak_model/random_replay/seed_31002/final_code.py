def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) for the given instance using
    a deterministic, interpretable approach with constructive, repair, and local search methods.
    
    Args:
        instance: A dictionary with the following keys:
            'depot': int, the depot customer ID
            'customers': dict of customer_id -> {'x': float, 'y': float, 'demand': float}
            'vehicle_capacity': float, maximum load capacity of each vehicle
    
    Returns:
        routes: List of routes, each route is a list of customer IDs (excluding depot)
    """
    # Extract data from instance
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Create a list of all customer IDs
    unassigned = list(customers.keys())
    
    # Function to compute Euclidean distance between two customers
    def distance(cust1, cust2):
        dx = customers[cust1]['x'] - customers[cust2]['x']
        dy = customers[cust1]['y'] - customers[cust2]['y']
        return (dx*dx + dy*dy)**0.5
    
    # Build an initial solution: assign customers to routes greedily
    routes = []
    while unassigned:
        current_load = 0
        route = []
        # Start from depot: for simplicity, start each route from depot
        # Choose the closest unassigned customer to depot that fits the capacity
        # For interpretability, always pick the closest feasible customer
        last_customer = depot
        while True:
            feasible_customers = []
            for c in unassigned:
                demand = customers[c]['demand']
                if current_load + demand <= capacity:
                    dist = distance(last_customer, c)
                    feasible_customers.append((dist, c))
            if not feasible_customers:
                break
            # pick the closest feasible customer
            feasible_customers.sort(key=lambda x: x[0])
            _, next_customer = feasible_customers[0]
            # Assign customer to route
            route.append(next_customer)
            current_load += customers[next_customer]['demand']
            unassigned.remove(next_customer)
            last_customer = next_customer
        routes.append(route)
    
    # Repair step: try to improve routes by exchanging customers between routes
    # For simplicity and interpretability, attempt pairwise swaps if they reduce total distance
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for a_idx, a in enumerate(route_i):
                    for b_idx, b in enumerate(route_j):
                        # Check capacity constraints after swap
                        demand_i = sum(customers[c]['demand'] for c in route_i)
                        demand_j = sum(customers[c]['demand'] for c in route_j)
                        demand_a = customers[a]['demand']
                        demand_b = customers[b]['demand']
                        new_demand_i = demand_i - demand_a + demand_b
                        new_demand_j = demand_j - demand_b + demand_a
                        if new_demand_i <= capacity and new_demand_j <= capacity:
                            # Compute old total distance
                            old_dist = total_route_distance(route_i, customers, distance, depot) + \
                                       total_route_distance(route_j, customers, distance, depot)
                            # Create new routes after swap
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[a_idx] = b
                            new_route_j[b_idx] = a
                            new_dist = total_route_distance(new_route_i, customers, distance, depot) + \
                                       total_route_distance(new_route_j, customers, distance, depot)
                            if new_dist < old_dist:
                                # Accept swap
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
    
    # Final local improvement: try to remove customer from route if similar, then re-insert in better position
    def total_route_distance(route, customers, dist_fn, depot):
        total = dist_fn(depot, route[0]) if route else 0
        for i in range(len(route)-1):
            total += dist_fn(route[i], route[i+1])
        if route:
            total += dist_fn(route[-1], depot)
        return total
    
    # Local search: re-insert customers in better position
    for route_idx, route in enumerate(routes):
        for c_idx in range(len(route)):
            customer_id = route[c_idx]
            current_location = customer_id
            best_position = c_idx
            best_improvement = 0
            for insert_idx in range(len(route)):
                if insert_idx == c_idx:
                    continue
                new_route = route[:]
                # Remove customer
                new_route.pop(c_idx)
                # Insert at new position
                new_route.insert(insert_idx, customer_id)
                # Check capacity
                demand_sum = sum(customers[c]['demand'] for c in new_route)
                if demand_sum <= capacity:
                    old_dist = total_route_distance(route, customers, distance, depot)
                    new_dist = total_route_distance(new_route, customers, distance, depot)
                    if new_dist < old_dist:
                        route[:] = new_route
                        best_improvement = new_dist - old_dist
                        break
    # Return routes (excluding depot)
    return routes

