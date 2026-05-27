def solve_cvrp(instance):
    """
    Solves the Capacitated Vehicle Routing Problem (CVRP) using a deterministic,
    interpretable heuristic with constructive and local-improvement steps.

    Args:
        instance (dict): A dictionary with keys:
            - 'depot': int, the depot node id
            - 'customers': list of customer node ids
            - 'demands': dict {node_id: demand}
            - 'coords': dict {node_id: (x, y)}
            - 'vehicle_capacity': int, capacity of each vehicle
    
    Returns:
        routes (list of list): List of routes, each route is list of customer node ids (without depot)
    """
    depot = instance['depot']
    customers = instance['customers']
    demands = instance['demands']
    coords = instance['coords']
    capacity = instance['vehicle_capacity']
    
    # Helper function: compute Euclidean distance
    def dist(a, b):
        (x1, y1) = coords[a]
        (x2, y2) = coords[b]
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5

    # Initialize list of unserved customers
    unserved = set(customers)
    routes = []

    # Construct initial routes using a simple nearest neighbor heuristic
    while unserved:
        route = []
        load = 0
        current_node = depot
        while True:
            # Find feasible customers sorted by distance
            feasible_customers = [
                (cust, dist(current_node, cust))
                for cust in unserved
                if load + demands[cust] <= capacity
            ]
            if not feasible_customers:
                break
            # Pick the nearest feasible customer
            feasible_customers.sort(key=lambda x: x[1])
            chosen_customer = feasible_customers[0][0]
            # Add customer to route
            route.append(chosen_customer)
            load += demands[chosen_customer]
            unserved.remove(chosen_customer)
            current_node = chosen_customer
        routes.append(route)

    # Local improvement: try to better routes by exchanging customers
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                # Try all pairs of customers to swap between the two routes
                for idx_i, c1 in enumerate(route_i):
                    for idx_j, c2 in enumerate(route_j):
                        # Check if swap is feasible
                        load_i = sum(demands[c] for c in route_i)
                        load_j = sum(demands[c] for c in route_j)
                        new_load_i = load_i - demands[c1] + demands[c2]
                        new_load_j = load_j - demands[c2] + demands[c1]
                        if new_load_i <= capacity and new_load_j <= capacity:
                            # Calculate current cost
                            def route_distance(route):
                                total = dist(depot, route[0]) if route else 0
                                for k in range(len(route) - 1):
                                    total += dist(route[k], route[k+1])
                                total += dist(route[-1], depot) if route else 0
                                return total
                            current_cost = route_distance(route_i) + route_distance(route_j)
                            # Swap customers
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[idx_i] = c2
                            new_route_j[idx_j] = c1
                            new_cost = route_distance(new_route_i) + route_distance(new_route_j)
                            # Accept swap if better
                            if new_cost < current_cost:
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

    return routes

